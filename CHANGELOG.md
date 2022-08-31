[//]: # (START/LATEST)
# Latest

## Features
  * A user-friendly description of a new feature. {issue-number}

## Fixes
 * A user-friendly description of a fix. {issue-number}

## Security
 * A user-friendly description of a security fix. {issue-number}

---

[//]: # (START/v2.2.1)
# v2.2.1

## Fixes
* Connect responses of type `HTTPError` or `null` are now properly handled. (#59)
* Added an Ansible Automation Hub tag (`security`) to add compliance with the Automation Hub guidelines. Credits to @JohnLieske for the contribution. (#52)
* Added required `meta/runtime.yml` for Ansible Galaxy compat. (#50)

---

[//]: # (START/v2.2.0)
# v2.2.0

## Features
[//]: # (* A user-friendly description of a new feature. {issue-number})
* Introduce the `onepassword.connect.field_info` module (#39)

## Fixes
[//]: # (* A user-friendly description of a fix. {issue-number})
* Add `flatten_fields_by_label` option to the `onepassword.connect.field_info` module. (#34)
    * The new option defaults to `true` and preserves the behavior seen in versions <=2.1.1.
    * **The default behavior will change in release v3.0.0**
    * See [PR #39](https://github.com/1Password/ansible-onepasswordconnect-collection/pull/39) for more details.

* Creating a one-time password (`OTP`) field within an item now uses the correct field type. (#46)

---

[//]: # (START/v2.1.1)
# v2.1.1

This release improves compatibility with all Python runtimes supported by Ansible 2.9+. 

We are making this change to better support customers downloading this collection through RedHat's Ansible Automation Hub. 

## Fixes
[//]: # (* A user-friendly description of a fix. {issue-number})
* Replace Python 3.6+ features with backwards-compatible implementations. (#31)

---

[//]: # (START/v2.1.0)
# v2.1.0

This version fixes several bugs, introduces more supported item types, and improves how the module handles special fields for certain item types. 

Note there is a **breaking change** when defining an Item with `type: login` or `type: password`:

* Creating a `type: password` Item without a `concealed` field named **password** will raise an error
* If the Item type is `password` and there are multiple `concealed` fields named **password**, Ansible raises an error
* If the Item type is `login` and there are multiple string fields named **username**, Ansible raises an error.

## Features
 * Change default item type to `API_CREDENTIAL` (#25)
 * Add more supported item type choices (#24)

## Fixes
 * `get_item_by_name` client method now returns the full item response instead of the overview. (#29)
 * Fix field_purpose assignment when item type is `PASSWORD` or `LOGIN` (#28)  
 * Use UTF-8 string normalization while searching for fields when updating an item. (#27)  
 * The `generic_item` module now preserves the notes field without it being present in the module parameters (#27)  
 * Fix sed regex for currentVersion lookup in release tool. (#23)

---

[//]: # (START/v2.0.0)
# v2.0.0

This release introduces two breaking changes to the `generic_item` module:

- The Item options `state: upserted` and `state: created` have been replaced by `state: present`. Please refer to the README for usage details.

- You now have fine-grained controls for defining when 1Password Connect should generate a field's value. The `generate_value` setting now accepts `on_create`, `always`, and `never` (default).

## Features
[//]: # (* A user-friendly description of a new feature. {issue-number})
  * You can now use the familiar `state: absent` and `state: present` when defining 1Password vault items in your playbooks. (#15)
  * Introduce `on_create` / `always` / `never` options for a field's `generate_value` setting (#15).
  * Add support for API_CREDENTIAL item type (#17)


## Fixes
[//]: # (* A user-friendly description of a fix. {issue-number})

 * Makefile now uses the correct path to the testing script. (#14)

---

[//]: # (START/v1.0.1)
# v1.0.1

## Fixes
[//]: # (* A user-friendly description of a fix. {issue-number})
* Resolves small issues with the Ansible Galaxy manifest file
* Exclude the `test/` directory from the build artifact.

---

[//]: # (START/v1.0.0)
# v1.0.0

First public release of the 1Password Ansible collection for Secrets Automation.

## Fixes
* Module documentation now adheres to Ansible standards
* Remove Python3.6 syntax as required by [Ansible compile tests](https://docs.ansible.com/ansible/latest/dev_guide/testing_compile.html#testing-compile)

---

[//]: # (START/v0.0.2)
# v0.0.2

## Features
* `field.overwrite` option is now True by default.
* `field.label` is now required
* Clarify `state: upserted` arg in README

---

[//]: # (START/v0.0.1)
# v0.0.1

## Features
* Initial beta release.

---
