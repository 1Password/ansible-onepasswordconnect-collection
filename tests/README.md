# Testing

## Prerequisites
- Docker is running locally
- Running instance of Connect API server and Connect Syncer.
- The `ansible` Python package & its binaries are installed on the test runner (i.e. your computer, the CI container). 

Set the following environment variables:
```
export OP_VAULT_ID=<id_of_target_vault>
export OP_CONNECT_HOST=<http_url_to_connect_server> # see comment
export OP_CONNECT_TOKEN=<jwt_for_service_account>
```
**NOTE**: If running a Connect server locally, you will need to use `http://docker.for.mac.host.internal:8080` as the value for `OP_CONNECT_HOST`.

### Running tests

From the repository root, run `./scripts/run-tests.sh <units|integration>`

The script will:
- create a temporary directory (using [mktemp](https://linux.die.net/man/1/mktemp))
- copy the collections under the `1password` namespace into the temporary directory
- run `ansible-test <test_type> --docker {docker image}` 
- remove the temp directory when exiting


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


## **Why can't I run `ansible-test` from the repository root?**
>
>  Ansible 2.10 has a few issues with paths when running tests:
> - https://www.jeffgeerling.com/blog/2019/how-add-integration-tests-ansible-collection-ansible-test
> - https://github.com/ansible/ansible/issues/60215
