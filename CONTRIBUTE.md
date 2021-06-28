# Contributing

Thank you taking the time to improve the 1Password Ansible collection! 

After reading this document, you will: 
- have set up a development environment; 
- know how to file issues;
- understand the pull request process.


## Set up a Development Environment

### Install Ansible

> If you have already installed a supported version of Ansible, you can skip to the [Clone the Repo](#clone-the-repo) step.

This collection requires **Python v3.6 or greater**. If you don't have Python installed, consider using [pyenv](https://github.com/pyenv/pyenv) to install the supported Python runtime.


Current Ansible-core and Ansible version supported:
- `ansible-core`: **2.11**
- `ansible`: **4.0**

You may install Ansible in a `virtualenv` or globally. 

#### Install Ansible via virtualenv

```bash
python3 -m venv <path_to_venv>/onepassword_ansible
source <path_to_venv>/onepassword_ansible activate

pip3 install ansible-core==2.11.*
pip3 install ansible==4.0.*
```

#### Install Ansible System-wide 
```bash
pip3 install ansible-core==2.11.*
pip3 install ansible==4.0.*
```

### Clone the Repo

Please create a personal fork of the repository before beginning any work. The [GitHub guide on forks and PRs](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) is a great place to learn more about this process.

```bash
mkdir -p ~/onepassword/ansible_collections/onepasswword
cd ~/onepassword/ansible_collections/onepassword

# Clone the collection repo into the namespace: {..}/ansible_collections/onepassword
git clone git@github.com:1Password/ansible-onepasswordconnect-collection.git connect
cd connect

# (OPTIONAL): Overwrite Ansible's collection lookup path 
# to first look for collections inside ~/onepassword/ansible_collections/... 
export ANSIBLE_COLLECTIONS_PATHS=~/onepassword:$ANSIBLE_COLLECTIONS_PATHS

# Verify - you should see docs for the `generic_item` module in your terminal
ansible-doc onepassword.connect.generic_item
```

Ansible is [particular about the folder structure](https://github.com/ansible/ansible/issues/60215) for custom collections. For Ansible to recognize the collection, the collection namespace must live inside a folder named `ansible_collections/`. All `onepassword` collections must exist within the `onepassword` namespace folder.

For more information about the `ANSIBLE_COLLECTIONS_PATHS` environment variable, visit the [Ansible documentation](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_COLLECTIONS_PATHS).

## Running Tests

We run our tests using Docker images. See [tests/README.md](tests/README.md) for complete instructions.


## Filing Issues

We welcome you to file bug reports and feature requests through GitHub issues. 

There are templates for issues and feature requests, but if the issue does not fall into either category, please use an empty issue and be as specific as possible.

## Pull Requests

Open a new PR using a branch from your personal fork. Again, the [GitHub guide on forks and PRs](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) is a great resource!

When describing the PR, please provide the following:
- Summary of changes
- How the changes impact the end-user
- How to test the change

