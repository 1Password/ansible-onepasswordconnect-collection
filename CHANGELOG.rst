=================================
onepassword.connect Release Notes
=================================

.. contents:: Topics


v2.2.1
======

Bugfixes
--------

- Add required meta/runtime.yml for Ansible Galaxy compat. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/50)
- Adding the ``security`` Ansible Automation Hub tag to add compliance with the Automation Hub guidelines. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/52)
- Fix typo ``OP_VAULT`` into ``OP_VAULT_ID`` in the documentation. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/63)
- module_utils - api now handles HTTP error responses. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/58)
- module_utils - api reads the response only if the status code is ``200``. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/64)

v2.2.0
======

Minor Changes
-------------

- Add ``connect.field_info`` module (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/39)

Bugfixes
--------

- generic_item - Creating a one-time password (``OTP``) field within an item now uses the correct field type. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/46)
- item_info - non-unique field labels were overwriting the field values for the returned item if the field label was already in the dictionary. This is now fixed by addding the ``flatten_fields_by_label`` option. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/34)

v2.1.1
======

Release Summary
---------------

This release improves compatibility with all Python runtimes supported by Ansible 2.9+.
We are making this change to better support customers downloading this collection through RedHat's Ansible Automation Hub.

Bugfixes
--------

- Replace Python 3.6+ features with backwards-compatible implementations.

v2.1.0
======

Release Summary
---------------

This version fixes several bugs, introduces more supported item types, and improves how the module handles special fields for certain item types.
Note there is a **breaking change** when defining an Item with ``type: login`` or ``type: password``

Minor Changes
-------------

- generic_item - add more supported item types (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/22)
- generic_item - default item type is now ``API_CREDENTIAL``. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/25)

Breaking Changes / Porting Guide
--------------------------------

- generic_item - if an Item of ``type: password`` has multiple ``concealed`` fields named ``password``, Ansible raises an error. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/20)
- generic_item - if an Item of ``type: password`` is created without a ``concealed`` field named ``password``, Ansible raises an error. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/20)
- generic_item - if an item of ``type: login`` has multiple ``string`` fields named ``username``, Ansible raises an error. (https://github.com/1Password/ansible-onepasswordconnect-collection/issues/20)

Bugfixes
--------

- Fix sed regex for currentVersion lookup in release tool. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/23)
- generic_item - preserve ``notesField`` regardless of playbook parameters. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/27)
- generic_item - use UTF-8 string normalization while searching for fields when updating an item. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/27)
- module_utils - ``get_item_by_name`` client method now returns the full item response instead of the overview. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/29)

v2.0.0
======

Minor Changes
-------------

- module_utils - Add support for ``API_CREDENTIAL`` item type. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/17)

Breaking Changes / Porting Guide
--------------------------------

- generic_item - ``generate_value`` setting accepts ``on_create``, ``always``, and ``never`` (default). This enables fine-grained controls for defining when 1Password Connect should generate a field's value. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/15)
- generic_item - item options ``state: upserted`` and ``state: created`` are replaced by ``state: present``. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/15)

Bugfixes
--------

- Makefile now uses the correct path to the testing script. (https://github.com/1Password/ansible-onepasswordconnect-collection/pull/14)

v1.0.1
======

Bugfixes
--------

- Exclude the `test/` directory from the build artifact.
- Resolve small issues with the Ansible Galaxy manifest file.

v1.0.0
======

Release Summary
---------------

First public release of the 1Password Ansible collection for Secrets Automation.

Bugfixes
--------

- Module documentation now adheres to Ansible standards.
- Remove Python 3.6 syntax as required by Ansible compile tests.
