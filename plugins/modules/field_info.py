#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, 1Password & Agilebits (@1Password)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
module: field_info
author:
  - 1Password (@1Password)
requirements: []
notes:
version_added: 2.2.0
short_description: Returns the value of a field in a 1Password item.
description:
  - Get the value a single field given its label.
  - You may provide a section label to limit the search to that item section.
options:
  item:
    type: str
    required: True
    description:
      - Name or ID of the item
  field:
    type: str
    required: True
    description:
      - The field label to search for.
      - If the section parameter is undefined, the  field label must be unique across all item fields.
  vault:
    type: str
    required: True
    description:
      - ID of the Vault containing the item
  section:
    type: str
    description:
      - An item section label or ID.
      - If provided, the module limits the search for the field to this section.
      - If not provided, the module searches the entire item for the field.

extends_documentation_fragment:
  - onepassword.connect.api_params
'''

EXAMPLES = '''
---
- name: Find a field labeled "username" in an item named "MySQL Database" in a specific vault.
  onepassword.connect.field_info:
    item: MySQL Database
    field: username
    vault: 2zbeu4smcibizsuxmyvhdh57b6

- name: Find a field labeled "username" in a specific section.
  onepassword.connect.field_info:
    item: MySQL Database
    section: Credentials
    field: username
    vault: 2zbeu4smcibizsuxmyvhdh57b6
'''

RETURN = '''
field:
    description: The value and metadata of the field
    type: complex
    returned: always
    contains:
      value:
        type: str
        description: The field's stored value
        returned: success
      section:
        type: str
        description: The section containing this field, if any.
      id:
        type: str
        returned: success
        description: UUID for the returned field
        sample: "fb3b40ac85f5435d26e"
'''

from ansible.module_utils.six import text_type
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.onepassword.connect.plugins.module_utils import specs, api, errors, fields, util
from ansible.module_utils.common.text.converters import to_native


def find_field(field_identifier, item, section=None) -> dict:
    """
    Tries to find the requested field within the provided item.

    The field may be a valid client UUID or it may be the field's label.
    If the section kwarg is provided, the function limits its search
    to fields within that section.
    """
    if not item.get("fields"):
        raise errors.NotFoundError("Item has no fields")

    section_uuid = None
    if section:
        section_uuid = _get_section_uuid(item.get("sections"), section)

    if api.valid_client_uuid(field_identifier):
        return _find_field_by_id(field_identifier, item["fields"], section_uuid)

    return _find_field_by_label(field_identifier, item["fields"], section_uuid)


def _find_section_id_by_label(sections, label):
    label = util.utf8_normalize(label)

    for section in sections:
        if util.utf8_normalize(section["label"]) == label:
            return section["id"]

    raise errors.NotFoundError("Section label not found in item")


def _get_section_uuid(sections, section_identifier):
    if not sections:
        return None

    if not api.valid_client_uuid(section_identifier):
        return _find_section_id_by_label(sections, section_identifier)
    return section_identifier


def _find_field_by_label(field_label, fields, section_id=None):
    wanted_label = util.utf8_normalize(field_label)

    for field in fields:
        label = util.utf8_normalize(field["label"])
        if section_id is None and label == wanted_label:
            return field

        if field.get("section", {}).get("id") == section_id \
                and label == wanted_label:
            return field

    raise errors.NotFoundError("Field with provided label not found in item")


def _find_field_by_id(field_id, fields, section_id=None):
    for field in fields:

        if section_id is None and field["id"] == field_id:
            return field

        if field.get("section", {}).get("id") == section_id \
                and field["id"] == field_id:
            return field

    raise errors.NotFoundError("Field not found in item")


def get_item(vault, item, op_client):
    if not api.valid_client_uuid(vault):
        vault = _get_vault_id(vault, op_client.get_vaults())

    if not api.valid_client_uuid(item):
        return op_client.get_item_by_name(vault, item)
    return op_client.get_item_by_id(vault, item)


def _get_vault_id(vault_name, all_vaults):
    normalized_vault_name = util.utf8_normalize(vault_name)

    for vault in all_vaults:
        if normalized_vault_name == util.utf8_normalize(vault.get("name")):
            return vault["id"]
    raise errors.NotFoundError("Vault not found")


def _to_field_info(field) -> dict:
    return {
        "value": field.get("value"),
        "section": field.get("section", {}).get("id"),
        "id": field.get("id")
    }


def main():
    result = {"field": {}}

    module = AnsibleModule(
        argument_spec=specs.op_field_info(),
        supports_check_mode=True
    )

    api_client = api.create_client(module)

    field_label = module.params.get("field")
    vault_id = module.params.get("vault")
    item_id = module.params.get("item")
    section_label = module.params.get("section")

    if not api.valid_client_uuid(vault_id):
        module.fail_json({"field": {}, "msg": "Vault ID invalid or undefined."})
        return

    try:
        item = get_item(vault_id, item_id, api_client)
        field = find_field(field_label, item, section=section_label)
        result.update({"field": _to_field_info(field)})
    except errors.NotFoundError as e:
        result.update({"msg": to_native("Field not found: {err}".format(err=e))})
        module.fail_json(**result)
    except errors.Error as e:
        result.update({"msg": to_native(e)})
        module.fail_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
