# Testing

## Prerequisites
- Docker is running locally
- The `ansible` Python package & its binaries are installed on the test runner (i.e. your computer, the CI container). 

From the repository root, run `./scripts/runtest.sh <units|integration>`

The script will:
- create a temporary directory (using [mktemp](https://linux.die.net/man/1/mktemp))
- copy the collections under the `1password` namespace into the temporary directory
- run `ansible-test integration --docker {docker image}` 
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
