# 1Password Connect Ansible Collection

The 1Password Connect collection contains modules that interact with your 1Password Connect deployment. The modules communicate with the 1Password Connect API to support Vault Item create/read/update/delete operations.

You can learn more about [Secrets Automation and 1Password Connect](https://1password.com/secrets/) on our website.

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Module & Environment Variables](#module-variables)
* [`generic_item` Module](#connectgeneric_item-module)
* [`item_info` Module](#item_info-module)
* [`field_info` Module](#field_info-module)
* [Testing](#testing)
* [About 1Password](#about-1password)
* [Security](#security)


### Requirements
- Python >= 3.6.0
- 1Password Connect >= 1.0.0
    
#### Supported Ansible Versions

This collection has been tested against the following Ansible versions:
* `ansible-core`: >=2.9, 2.11, 2.12
* `ansible`: >=4.0, <5.0

## Installation

You can install the Ansible collection from [Ansible Galaxy](https://galaxy.ansible.com/onepassword/connect):

```
ansible-galaxy collection install onepassword.connect
```

## Module Variables

All modules support the following variable definitions. You may either explicitly define the value on the task or let Ansible fallback to an environment variable to use the same value across all tasks.

Environment variables are ignored if the module variable is defined for a task.

| Module Variable | Environment Variable | Description                                                             |
|----------------:|----------------------|-------------------------------------------------------------------------|
|      `hostname` | `OP_CONNECT_HOST`    | URL of a 1Password Connect API Server                                   |
|         `token` | `OP_CONNECT_TOKEN`   | JWT used to authenticate 1Password Connect API requests                 |
|      `vault_id` | `OP_VAULT_ID`        | (Optional) UUID of a 1Password Vault the API token is allowed to access |


## `connect.generic_item` Module

> 🔥 **Warning** 🔥 It is _strongly_ recommended you define `no_log: true` on any tasks that interact with 1Password Connect. Ansible may print sensitive data if `no_log` is not set.

### Example Usage
**Create a new Item**
```yaml
---
- name: Create 1Password Secret
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "api.jwt.here"
  tasks:
    - onepassword.connect.generic_item:
        vault_id: "qwerty56789asdf"
        title: Club Membership
        state: present
        fields:
          - label: Codeword
            value: "hunter2"
            section: "Personal Info"
            field_type: concealed
          - label: Random Code
            generate_value: on_create
            generator_recipe:
                length: 16
                include_letters: yes
                include_digits: yes
                include_symbols: no
      no_log: true
      register: op_item
```

### A note about `state`

The `generic_item` module follows Ansible's `present/absent` state pattern.

- `state: present`
    - If the module _cannot find a matching Item_ by its `uuid` or `title`, a new item is created with the defined values.
    - If the module _finds a matching Item_ on the server, it will completely replace the old Item with a new Item defined by the playbook values.
- `state:absent`
    - If the Item cannot be found, no action is taken.
    - If the Item is found, it is deleted. Otherwise, no action is taken.

**Search order for an existing Item**
1. Search by the Item's `uuid`, if provided.
2. Search by `title`, using a case-sensitive, exact-match query.


### Generating field values

1Password can generate a field's value on the user's behalf when creating or updating an Item. Because generating random values is not idempotent, the user can specify one of three settings for `generate_value`:

`generate_value` setting  | Effect |
---: | --- |
`never` | **(Default)** The field value is not generated; uses `value` parameter instead.
`on_create` | Generate the field's value if the field does not already exist. The field's stored value is preserved across playbook executions.
`always` | Generate a new value for the field everytime the playbook is run. Overwrites `value` parameter.
---

**Update an Item**

**❗️Note❗** The update operation will completely replace the Item matching the `title` or `uuid` field. Any properties not provided in the task definition will be lost.

We recommend storing the Items created by Ansible in a Vault that only 1Password Connect may access.

```yaml
---
- name: Update a 1Password Secret
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "valid.jwt.here"
    OP_VAULT_ID: "zyzzyz1234example"
  tasks:
    - onepassword.connect.generic_item:
        title: Club Membership
      # uuid: 1ff75fa9fexample  -- or use an Item ID to locate an item instead
        state: present
        fields:
          - label: Codeword
            field_type: concealed
          - label: Dashboard Password
            generate_value: always  # new value is generated every time playbook is run
            generator_recipe:
                length: 16
                include_symbols: no
      no_log: true
```

## `item_info` Module

Get information about an Item, including fields and metadata. 


### Example Usage

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


## `field_info` Module

Use the `onepassword.connect.field_info` module to get the value of an item field.

The `field_info` module will first find the item by name or UUID, then search for the requested field by name. If a `section` is provided, the module will only search within that item section. **If no section is provided, the field name must be unique within the item**.

The search method compares field names using the [`unicodedata.normalize`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize) function and the `NKFD` form.

### Example Usage

```yaml
---
  hosts: localhost
  environment:
    OP_CONNECT_HOST: http://localhost:8001
    OP_CONNECT_TOKEN: "valid.jwt.here"
  collections:
    - onepassword.connect
  tasks:
    - name: Find a field labeled "username" in an item named "MySQL Database" in a specific vault.
      onepassword.connect.field_info:
      item: MySQL Database
      field: username
      vault: 2zbeu4smcibizsuxmyvhdh57b6
    no_log: true
    register: op_item

    - name: Print the field definition
      ansible.builtin.debug:
        var: "{{ op_item.field }}"
```

<details>
<summary>View output registered to the `op_item` variable</summary>
<br>

```
{
    "value": "mysql_username_example",
    "section": "",
    "id": "fb3b40ac85f5435d26e"
}
```
</details>

## Testing

Use the `test` Makefile target to run unit tests:

```shell
make test
```

For more information about testing, see [tests/README.md](./tests/README.md)

## About 1Password

[**1Password**](https://1password.com) is a privacy-focused password manager that keeps you safe online.

By combining industry-leading security and award-winning design, the company provides private, secure, and user-friendly password management to businesses and consumers globally. More than 60,000 business customers trust 1Password as their enterprise password manager.

## Security
1Password requests you practice responsible disclosure if you discover a vulnerability. 

Please file requests via [BugCrowd](https://bugcrowd.com/agilebits). 

For information about security practices, please visit our [Security homepage](https://support.1password.com/1password-security/).
