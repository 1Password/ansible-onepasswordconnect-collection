<img alt="" role="img" src="https://blog.1password.com/posts/2021/secrets-automation-launch/header.svg"/>

<div align="center">
  <h1>1Password Connect Ansible Collection</h1>
  <p>Access and manage your 1Password items in your Ansible Automation Platform through your self-hosted <a href="https://developer.1password.com/docs/connect">1Password Connect server</a>.</p>
  <a href="https://github.com/1Password/ansible-onepasswordconnect-collection#-get-started">
    <img alt="Get started" src="https://user-images.githubusercontent.com/45081667/226940040-16d3684b-60f4-4d95-adb2-5757a8f1bc15.png" height="37"/>
  </a>
</div>

---

The 1Password Connect collection contains modules that interact with your 1Password Connect deployment. The modules communicate with the 1Password Connect API to support Vault Item create/read/update/delete operations.

## Requirements

- `ansible`: **>=7.x**
- `ansible-core`: **>=2.15**
- `python`: **>=3.9**
- `1Password Connect`: **>= 1.0.0**

## ✨ Get started

### 🚀 Quickstart

1. You can install the Ansible collection from [Ansible Galaxy](https://galaxy.ansible.com/onepassword/connect):

```
ansible-galaxy collection install onepassword.connect
```

2. Example of getting information about an Item, including fields and metadata:

```yaml
---
hosts: localhost
vars:
  connect_token: "valid.jwt.here"
environment:
  OP_CONNECT_HOST: http://localhost:8001
collections:
  - onepassword.connect
tasks:
  - name: Find the item with the label "Staging Database" in the vault "Staging Env"
    item_info:
      token: "{{ connect_token }}"
      item: Staging Database
      vault: Staging Env
    no_log: true
    register: op_item
```

### 📄 Usage

Refer to the [Usage Guide](USAGEGUIDE.md) for documentation for example usage.

## 💙 Community & Support

- File an [issue](https://github.com/1Password/ansible-onepasswordconnect-collection/issues) for bugs and feature requests.
- Join the [Developer Slack workspace](https://join.slack.com/t/1password-devs/shared_invite/zt-1halo11ps-6o9pEv96xZ3LtX_VE0fJQA).
- Subscribe to the [Developer Newsletter](https://1password.com/dev-subscribe/).

## 🔐 Security

1Password requests you practice responsible disclosure if you discover a vulnerability.

Please file requests by sending an email to bugbounty@agilebits.com.
