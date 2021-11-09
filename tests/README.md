# Testing

## Prerequisites
- Docker is running locally
- Connect API server and Connect Syncer running locally or on a remote server
- The `ansible` Python package & its binaries are installed on the test runner (i.e. your computer, the CI container). 

Set the following environment variables before running the tests:
```
export OP_VAULT_ID=id_of_target_vault
export OP_CONNECT_HOST=http_url_to_connect_server # see comment
export OP_CONNECT_TOKEN=jwt_for_service_account
```
**NOTE (macOS)**: If you are running the Connect server locally (i.e. not within a Docker container), set `OP_CONNECT_HOST` to `http://docker.for.mac.host.internal:8080`.

## Running tests

From the repository root, run `make test/unit` for Unit Tests and `make test/integration` for Integration Tests.

The script will:
- create a temporary directory (using [mktemp](https://linux.die.net/man/1/mktemp))
- copy the collections under the `1password` namespace into the temporary directory
- run `ansible-test <test_type> --docker {docker image}` 
- remove the temp directory after exiting


## Writing Tests

You must place integration tests in the appropriate `./tests/integration/targets/` directory. 

**Module Tests**
- Directory must match the name of the module.
- For example, you would place integration tests for `plugins/modules/foo.py` in a directory called `tests/integration/targets/foo/`


**Plugin Tests**
- Add the plugin type to the **directory** name.
- Examples: 
    - Lookup Plugin named "_foo_" => `./tests/integrations/targets/lookup_foo/` 
    - Connection Plugin named "_bar_" => `./tests/integration/targets/connection_bar/`

## Debugging Modules

Debugging Ansible modules is not a simple as debugging normal Python modules.

See Ansible's [Simple Debugging](https://docs.ansible.com/ansible/latest/dev_guide/debugging.html#simple-debugging) instructions for the current best practices.

If all else fails, adding a `raise Exception(some_value)` in a module will cause the module to exit and print the value of `some_value`.

# FAQ

### **Why can't I run `ansible-test` from the repository root?**

Ansible 2.10 has a few issues with paths when running tests for Collections:
> - https://www.jeffgeerling.com/blog/2019/how-add-integration-tests-ansible-collection-ansible-test
> - https://github.com/ansible/ansible/issues/60215

We also use Docker to avoid polluting local environments with test dependencies.