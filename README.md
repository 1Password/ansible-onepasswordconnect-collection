# 1Password Connect Ansible Collection

The 1Password Connect collection contains modules that interact with 1Password Connect. The modules communicate with 1Password Connect to support Vault Item create/read/update/delete operations.

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Module & Environment Variables](#module-variables)
* [`generic_item` Module](#connectgeneric_item-module)
  + [Usage Examples](#usage-examples)
* [`item_info` Module](#item_info-module)
  + [Usage Examples](#examples)
* [Testing](#testing)
* [About 1Password](#about-1password)


### Requirements
- ansible >= 2.9
- Python >= 3.6.0
- 1Password Connect
    
## Installation

**Closed Beta Instructions**

During Closed Beta the Ansible Collection can be installed via the Git URL: 

`ansible-galaxy collection install git@github.com:1password/ansible-onepasswordconnect-collection.git,v0.1.0`

For more information, see Ansible's documentation for [Installing a Collection from a Git Repository](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-a-collection-from-a-git-repository)

## Module Variables

All modules support the following variable definitions. You may either explicitly define the value on the task or use the associated environment variable to use the same value across all tasks.

Environment variables are ignored if the module variable is defined for a task.

Module Variable | Environment Variable | Description
---: | --- | --- |
`hostname` | `OP_CONNECT_HOST` | URL of the 1Password Connect API Server |
`token` | `OP_CONNECT_TOKEN` | JWT used to authenticate requests to API Server |
`vault_id`| `OP_VAULT_ID` | (Optional) UUID of a 1Password Vault the Service Account is allowed to access |


## `connect.generic_item` Module

> 🔥 **Warning** 🔥 It is _strongly_ recommended you define `no_log: true` on any tasks that interact with 1Password Connect. Ansible may print sensitive data if `no_log` is not set.

### Usage Examples
**Create a new Item**
```yaml
---
- name: Create 1Password Secret
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "serviceaccount.jwt.here"
  tasks:
    - onepassword.connect.generic_item:
        vault_id: "qwerty56789asdf"
        title: Club Membership
        state: created
        fields:
          - label: Codeword
            value: "hunter2"
            section: "Personal Info"
            field_type: concealed
      no_log: true
      register: op_item
```

### A note about `state`

1Password can generate a field's value on the user's behalf when creating or updating an Item. Because generating random values is not idempotent, the module uses 3 different state values when working with Items:

- `created` => Create a **new** Item every time Ansible runs the task.
- `updated` => Upsert (update or create if not exists) the item every time Ansible runs the task.
- `deleted` => Remove the item. Ignores errors if Item does not exist.

In most cases the `updated` state is the recommended setting if you want to ensure an Item exists. 

To preserve values across playbook executions, add `overwrite: no` to the field. This instructs the module to copy the field's existing value as-is during the update operation. 

---

**Update an Item**

Updating an Item is an **"upsert"** operation. If an item matching the given Item ID or Item Name is not found, the module will create a new Item using the provided task configuration.

> ❗️**Note**❗The upsert operation will remove any Item attributes and fields not defined in the task definition. 
> 
> We recommend storing the Items created by Ansible in a Vault that only the Service Account may access.

```yaml
---
- name: Update a 1Password Secret
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "valid.jwt.here"
    OP_VAULT: "zyzzyz1234example"
  tasks:
    - onepassword.connect.generic_item:
        title: Club Membership
      # uuid: 1ff75fa9fexample  -- or use an Item ID to locate an item instead
        state: upserted
        fields:
          - label: Codeword
            field_type: concealed
            overwrite: no   # This field reuses the stored value from the existing field with the same label
          - label: Dashboard Password
            generate_value: yes
            generator_recipe:
                length: 16
                include_symbols: no
      no_log: true
```

## `item_info` Module

Get information about an Item, including fields and metadata. 


### Examples

**Find an Item by Name**
```yaml
--- 
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "valid.jwt.here"
  collections:
    - onepassword.connect
  tasks:
    - name: Find the item with the label "Staging Database" in the vault "Staging Env"
      item_info:
        item: Staging Database
        vault: Staging Env
      no_log: true
      register: op_item
```


<details>
<summary>View `item_info` result registered to `op_item`</summary>
<br>

```
{
    "changed": false,
    "failed": false,
    "op_item": {
        "category": "SERVER",
        "createdAt": "2020-11-23T15:29:07.312397-08:00",
        "fields": {
            "Test": {
                "id": "j6ao3EXAMPLEvmzbrtre",
                "label": "Test",
                "type": "STRING",
                "value": ".........."
            },
            "notesPlain": {
                "id": "notesPlain",
                "label": "notesPlain",
                "purpose": "NOTES",
                "type": "STRING"
            }
        },
        "id": "bactwEXAMPLEpxhpjxymh7yy",
        "tags": [],
        "title": "Test Item 2",
        "updatedAt": "2020-11-23T15:29:07.312397-08:00",
        "vault": {
            "id": "4ktuuifg2ad7m4vEXAMPLEm"
        }
    }
}
```
</details>


**Find a field by name**

This example passes a `field` value to the `item_info` module. 

When `field` is defined, the module will perform a case-sensitive search for a field with a matching `label` value.

```yaml
---
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "valid.jwt.here"
  collections:
    - onepassword.connect
  tasks:
    - name: Get the 'Admin Password' field from the 'Staging Database' item
      item_info:
        item: Staging Database
        vault: Staging Env 
        field: Admin Username  # find field named "Admin Username"
      no_log: true
      register: op_item

    - name: Print the username
      ansible.builtin.debug:
        var: "{{ op_item.field }}"
```


## Testing

See [tests/README.md](./tests/README.md)

## About 1Password

[**1Password**](https://1password.com) is a privacy-focused password manager that keeps you safe online.

**1Password** is the world’s most-loved password manager. By combining industry-leading security and award-winning design, the company provides private, secure, and user-friendly password management to businesses and consumers globally. More than 60,000 business customers trust 1Password as their enterprise password manager.

## Security
1Password requests you practice responsible disclosure if you discover a vulnerability. 

Please file requests via [BugCrowd](https://bugcrowd.com/agilebits). 

For information about security practices, please visit our [Security homepage](https://support.1password.com/1password-security/).