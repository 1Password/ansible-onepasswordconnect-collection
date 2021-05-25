[//]: # (START/LATEST)
# Latest

## Features
 * 

## Fixes
 * 

## Security
 * 

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

## Security
[//]: # (* A user-friendly description of a security fix. {issue-number})

---

[//]: # (START/v1.0.1)
# v1.0.1

## Features
[//]: # (* A user-friendly description of a new feature. {issue-number})

## Fixes
[//]: # (* A user-friendly description of a fix. {issue-number})
* Resolves small issues with the Ansible Galaxy manifest file
* Exclude the `test/` directory from the build artifact.

## Security
[//]: # (* A user-friendly description of a security fix. {issue-number})

---

[//]: # (START/v1.0.0)
# v1.0.0

First public release of the 1Password Ansible collection for Secrets Automation.

## Features

## Fixes
* Module documentation now adheres to Ansible standards
* Remove Python3.6 syntax as required by [Ansible compile tests](https://docs.ansible.com/ansible/latest/dev_guide/testing_compile.html#testing-compile)

## Security
* 

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
