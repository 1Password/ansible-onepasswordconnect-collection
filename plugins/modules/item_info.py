#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, 1Password & Agilebits (@1Password)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
module: item_info
author:
  - 1Password (@1Password)
requirements: []
notes:
  - The "field" option will be deprecated in v3.0.0 of the onepassword.connect collection.
  - Beginning in v3.0.0, the module will always return a list of fields under the "fields" key instead of a dictionary.
short_description: Returns information about a 1Password Item
description:
  - The name or ID of an item can be given.
  - It is possible to return information about a specific field instead of an item.
  - If no vaults are specified, the module searches every vault accessible by the API token.
options:
  item:
    type: str
    required: True
    description:
      - Name or ID of the item as shown in the 1Password UI.
  field:
    type: str
    description:
      - Name of specific field for the Item
  vault:
    type: str
    description:
      - Name or ID of the Vault in which the Item is stored.
      - If not specified, the module searches through every vault accessible by the API token.
  flatten_fields_by_label:
    type: bool
    default: true
    description:
        - Toggles whether the module returns an item's fields as a dictionary of fields keyed by the field label.
        - If false, the item fields are returned as a list.
        - B(WARNING) When set to C(true), non-unique field labels may overwrite each other.
          Consider using C(onepassword.connect.field_info) instead or setting this option to C(false).
        - Beginning in C(3.0.0) this setting will default to C(false)
extends_documentation_fragment:
  - onepassword.connect.api_params
'''

EXAMPLES = '''
---
- name: Find and return Item details for "Dev-Database" in vault with ID "2zbeu4smcibizsuxmyvhdh57b6"
  onepassword.connect.item_info:
    item: Dev-Database
    vault: 2zbeu4smcibizsuxmyvhdh57b6

- name: Find and return Item details for Item with ID "lixyh6993asdfq9njdzf221d3z" in vault with ID "2zbeu4smcibizsuxmyvhdh57b6"
  onepassword.connect.item_info:
    item: lixyh6993asdfq9njdzf221d3z
    vault: 2zbeu4smcibizsuxmyvhdh57b6

- name: Find and return Item details for Item with ID "lixyh6993asdfq9njdzf221d3z" without specifying the vault
  onepassword.connect.item_info:
    item: lixyh6993asdfq9njdzf221d3z

- name: Return 'key' field for Item "Dev-Database" in vault with ID "2zbeu4smcibizsuxmyvhdh57b6"
  onepassword.connect.item_info:
    item: Dev-Database
    field: key
    vault: 2zbeu4smcibizsuxmyvhdh57b6

- name: Return 'secretKey' field for Item with ID 'lixyh6993asdfq9njdzf221d3z' in vault with ID "2zbeu4smcibizsuxmyvhdh57b6"
  onepassword.connect.item_info:
    item: lixyh6993asdfq9njdzf221d3z
    field: secretKey
    vault: 2zbeu4smcibizsuxmyvhdh57b6

- name: Return 'ccNumber' field for Item 'Business Visa' in Vault 'Office Expenses'
  onepassword.connect.item_info:
    item: Business Visa
    field: ccNumber
    vault: Office Expenses

- name: Get all fields for an item, formatted as a list
  onepassword.connect.item_info:
    item: Business Visa
    vault: Office Expenses
    flatten_fields_by_label: false
'''

RETURN = '''
op_item:
  description: Dictionary containing Item properties. See 1Password API specs for complete structure.
  type: complex
  returned: when field option is not set
  contains:
    category:
        description: The Item template used when creating or modifying the item
        returned: success
        type: str
        sample: LOGIN
    created_at:
        description: Timestamp that reports when the Item was originally created
        returned: success
        type: str
        sample: "2020-11-23T15:29:07.312397-08:00"
    updated_at:
        description: Timestamp that reports when the Item was last modified.
        returned: success
        type: str
        sample: "2020-11-23T15:29:07.312397-08:00"
    id:
        description: Unique ID for the Item.
        returned: success
        type: str
        sample: "bactwEXAMPLEpxhpjxymh7yy"
    tags:
        description: All unique tag values associated with the item
        type: list
        elements: str
        returned: success
        sample:
            - tag1
            - tag2
    title:
        description: User-provided name for the Item. Displayed in 1Password clients.
        type: str
        returned: success
        sample: My Test Item
    vault:
        description: Information about the Vault containing this Item.
        type: dict
        returned: success
        sample:
            - id: abc1234EXAMPLEvault5678
    fields:
        type: dict
        description:
            - Collection of all fields for the Item. The key for each field is the field's label.
            - If C(flatten_fields_by_label) is C(true), this value will be a list.
        returned: success
field:
  description: Value of the field for the Item.
  type: complex
  returned: when field option is defined
  contains:
    label:
        type: str
        description: User-provided name for a field
        returned: success
    value:
        type: str
        description: Value stored under this field
        returned: success
    section:
        type: str
        description: The section name or identifier that the field is under
    field_type:
        type: str
        returned: success
        description: Type identifier for the field
        sample: "concealed"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.onepassword.connect.plugins.module_utils import specs, api, errors, fields, util
from ansible.module_utils.common.text.converters import to_native


def _get_item(op, item, vault_id):
    try:
        return op.get_item_by_id(vault_id, item)
    except (errors.NotFoundError, errors.BadRequestError):
        return op.get_item_by_name(vault_id, item)


def _find_item_field(item, selected_field):
    selected_field = util.utf8_normalize(selected_field)
    for field in item["fields"]:
        if util.utf8_normalize(field["label"]) == selected_field:
            return field["value"]
    return None


def _get_item_with_vault_id(op, item, vault_id):
    return _get_item(op, item, vault_id)


def _get_item_without_vault(op, item):
    vaults = op.get_vaults()
    for vault in vaults:
        try:
            return _get_item_with_vault_id(op, item, vault["id"])
        except errors.NotFoundError:
            pass
    raise errors.NotFoundError


def _try_get_item(op, item, vault):
    if vault:
        try:
            return _get_item_with_vault_id(op, item, vault)
        except errors.BadRequestError:
            vault = op.get_vault_id_by_name(vault)
            return _get_item_with_vault_id(op, item, vault)

    return _get_item_without_vault(op, item)


def to_result(*, item=None, msg=None, **kwargs):
    """Builds response dict with mandatory keys. If defined, optional keys in kwargs
    are included.

    If provided, the "msg" value is converted to the native text format with to_native.
    """
    result = {
        "op_item": item or {},
        "msg": to_native(msg or "")
    }
    if kwargs.get("field"):
        result["field"] = kwargs.get("field")

    return result


def main():
    arg_spec = specs.op_item_info()

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True,
    )

    api_client = api.create_client(module)
    field_label = module.params.get("field")
    flatten_fields_by_label = module.params.get("flatten_fields_by_label")
    vault = module.params.get("vault")
    # Either the item's label or its UUID
    item_identifier = module.params.get("item")

    try:
        item = _try_get_item(api_client, item_identifier, vault)
    except errors.NotFoundError:
        module.fail_json(**to_result(msg="Item not found"))
        return
    except TypeError as e:
        module.fail_json(**to_result(
            msg="Invalid Item config: {err}".format(err=e))
        )
        return
    except errors.Error as e:
        module.fail_json(**to_result(msg=e.message))
        return

    if field_label:
        field = _find_item_field(item, field_label)
        if not field:
            module.fail_json(**to_result(item=item, msg="Field not found"))
            return
        module.exit_json(**to_result(item=item, field=field))
        return

    if flatten_fields_by_label:
        item["fields"] = fields.flatten_fieldset(item["fields"])

    module.exit_json(**to_result(item=item))


if __name__ == '__main__':
    main()
