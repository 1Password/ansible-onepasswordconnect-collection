#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, 1Password & Agilebits (@1Password)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
module: generic_item
author:
  - 1Password (@1Password)
requirements: []
notes:
short_description: Creates a customizable 1Password Item
description:
  - Create or update an Item in a Vault.
  - Fully customizable using the Fields option.
  - B(NOTE) Any item fields without C(label) are removed when updating an existing item.
options:
  vault_id:
    type: str
    required: True
    description:
        - ID of the 1Password vault that will be accessed.
        - Uses environment variable C(OP_VAULT_ID) if not explicitly defined in the playbook.
  name:
    type: str
    aliases:
        - title
    description:
      - Name of the Item
      - If C(state) is C(present) and c(uuid) is defined, the given value will overwrite previous Item name
      - If C(state) is C(present) and c(uuid) is NOT defined, the module will try to find an item with the same name.
        If an item cannot be found, a new item with the given name is created and the old item is not deleted.
  uuid:
    type: str
    description:
      - Unique ID for a single Item.
      - Ignored if C(state) is C(present) and the item doesn't exist.
      - If C(state) is C(present) and C(uuid) is NOT defined, the module will try to find an item using C(name).
        If an item cannot be found, a new item is created with the C(name) value and the old item is not changed.
  category:
    type: str
    default: api_credential
    description:
      - >
        Applies the selected category template to the item. Other 1Password clients use category templates to help
        organize fields when rendering an item.
      - >
        The category cannot be changed after creating an item.
        To change the category, recreate the item with the new category
      - >
        If the category is C(login) or C(password) and the item has a field named C(password),
        that field will be the primary password when the item is displayed in 1Password clients.
      - >
        If the category is C(login) and the item has a field named C(username),
        that field becomes the primary username when the item is displayed in 1Password clients.
    choices:
      - login
      - password
      - server
      - database
      - api_credential
      - software_license
      - secure_note
      - wireless_router
      - bank_account
      - email_account
      - credit_card
      - membership
      - passport
      - outdoor_license
      - driver_license
      - identity
      - reward_program
      - social_security_number
  urls:
    type: list
    elements: str
    description:
      - Store one or more URLs on an item
      - URLs are clickable in the 1Password UI
  favorite:
    type: bool
    default: false
    description: Toggles the 'favorite' attribute for an Item

  fields:
    description: List of fields associated with the Item
    type: list
    elements: dict
    suboptions:
      label:
        type: str
        required: true
        description: The name of the field
      value:
        type: str
        description: Sets the value of the field.
      section:
        type: str
        description:
          - Places the field into a named group. If section does not exist, it is created.
          - If two or more fields belong to the same C(section), they are grouped together under that section.
      field_type:
        type: str
        default: string
        aliases:
        - type
        description:
            - Sets expected value type for the field.
            - >
                If C(generic_item.category) is C(login) or C(password), the field with type C(concealed) and
                named C(password) becomes the item's primary password.
        choices:
          - string
          - email
          - concealed
          - url
          - otp
          - date
          - month_year
      generate_value:
        type: str
        default: 'never'
        choices: ['always', 'on_create', 'never']
        description:
          - Generate a new value for the field using the C(generator_recipe).
          - Overrides C(value) if I(generate_value=on_create) and field does not exist or if I(generate_value=always).
          - I(generate_value=never) will use the data in C(value).
          - I(generate_value=always) will assign a new value to this field every time Ansible runs the module.
          - I(generate_value=on_create) will generate a new value and ignore C(value) if the field does not exist.
            If the field does exist, the module will use the previously generated value and ignore
            the C(value).
          - The module searches for field by using a case-insensitive match for the C(label)
            within the field's C(section).
      generator_recipe:
        type: dict
        description:
          - Configures 1Password's Secure Password Generator
          - If C(generate_value) is 'never', these options have no effect.
        suboptions:
          length:
            type: int
            default: 32
            description:
              - Defines number of characters in generated password
          include_digits:
            type: bool
            default: true
            description:
              - Toggle whether generated password includes digits (0-9)
          include_letters:
            type: bool
            default: true
            description:
              - Toggle whether generated password includes ASCII characters (a-zA-Z)
          include_symbols:
            type: bool
            default: true
            description:
              - Toggle whether generated password includes ASCII symbol characters

extends_documentation_fragment:
  - onepassword.connect.item_tags
  - onepassword.connect.item_state
  - onepassword.connect.api_params
'''

EXAMPLES = '''
- name: Create an Item with no fields
  onepassword.connect.generic_item:
    title: Example Item
    state: present

- name: Create an item and generate its value if the item does not exist.
  onepassword.connect.generic_item:
    title: Club Membership
    state: present
    fields:
      - label: Secret Code
        field_type: concealed
        generate_value: on_create
        generator_recipe:
            length: 16
            include_letters: yes
            include_digits: yes
            include_symbols: no
        section: Club Card Details
  register: op_item  # Access item values through `op_item['data']`
  no_log: true       # Hide the output - it will contain the secret value you just stored

- name: Update an item while preserving the generated Secret Code value
  onepassword.connect.generic_item:
    title: Club Membership
    state: present
    fields:
      - label: Secret Code
        field_type: concealed
        overwrite: no
        generate_value: never
        generator_recipe: # ignored because generate_value == never
            length: 16
            include_letters: yes
            include_digits: yes
            include_symbols: no
        section: Club Card Details
  no_log: true

- name: Change an Item's Name and leave the generated Secret Code value unchanged
  onepassword.connect.generic_item:
    title: Guild Membership Details
    uuid: 3igj89sdf9ssdf89g
    state: present
    fields:
      - label: Secret Code
        field_type: concealed
        overwrite: no
        generate_value: on_create
        generator_recipe: # ignored because generate_value == never
            length: 16
            include_letters: yes
            include_digits: yes
            include_symbols: no
        section: Club Card Details
  no_log: true


- name: Delete an Item by its Item UUID
  onepassword.connect.generic_item:
    uuid: 3igj89sdf9ssdf89g
    state: absent
  no_log: true

- name: Delete an Item by its name
  onepassword.connect.generic_item:
    title: Club Membership
    state: absent
  no_log: true
'''

RETURN = '''
op_item:
  description: >
    Dictionary containing Item properties or an empty dictionary if I(state=absent).
    See 1Password Connect API for complete structure.
  type: complex
  returned: always
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
        description: Lists all defined fields for the Item. The key for each field is the field's label.
        returned: success
        sample: {"ExampleField": {"id": "123example", "label": "Test", "type": "STRING", "value": "exampleValue"}}
msg:
    description: Information returned when an error occurs.
    type: str
    returned: failure
    sample: Invalid Vault ID
'''

from ansible.module_utils.common.text.converters import to_native

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.onepassword.connect.plugins.module_utils import specs, api, vault, errors


def main():
    # Name always required when creating a new Item
    required_if = [
        ("state", "present", ("name",))
    ]

    module = AnsibleModule(
        argument_spec=specs.op_item(),
        supports_check_mode=True,
        required_if=required_if
    )

    results = {"op_item": {}, "changed": False}

    changed = False
    api_response = {}
    try:
        api_client = api.create_client(module)
        state = module.params["state"].lower()

        item = vault.find_item(module.params, api_client)

        if state == "absent":
            changed, api_response = vault.delete_item(
                item,
                api_client,
                check_mode=module.check_mode
            )
        else:
            if not item:
                changed, api_response = vault.create_item(
                    module.params,
                    api_client,
                    check_mode=module.check_mode
                )
            else:
                changed, api_response = vault.update_item(
                    module.params,
                    item,
                    api_client,
                    check_mode=module.check_mode
                )
    except TypeError as e:
        results.update({"msg": to_native("Invalid Item config: {err}".format(err=e))})
        module.fail_json(**results)
    except errors.Error as e:
        results.update({"msg": to_native(e.message)})
        module.fail_json(**results)

    results.update({"op_item": api_response, "changed": bool(changed)})
    module.exit_json(**results)


if __name__ == '__main__':
    main()
