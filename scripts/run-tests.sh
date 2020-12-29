#!/usr/bin/env bash

set -euo pipefail

if ! docker info >/dev/null 2>&1; then
    echo "==> [ERROR] Docker must be running before executing tests."
    exit 1
fi

if ! command -v ansible-test &> /dev/null; then
  echo "==> [ERROR] ansible-test not found in PATH. Please install or update PATH variable."
  exit 1
fi

# Only allow test types of "units" or "integration"
if [[ -z ${1+x} ]]; then
  echo "[ERROR] Usage: run-tests.sh units|integration|sanity"
  exit 1
elif [[ "$1" == "units" || "$1" == "integration" || "$1" == "sanity" ]]; then
  TEST_SUITE="$1"
else
  echo "[ERROR] Usage: run-tests.sh units|integration|sanity"
  exit 1
fi

COLLECTION_NAMESPACE="onepassword"
PACKAGE_NAME="connect"

# Collection will be copied to this path so that we can
# set the correct ANSIBLE_COLLECTION_PATH for tests.
TMP_DIR_PATH="$(mktemp -d)"
TMP_COLLECTIONS_PATH="${TMP_DIR_PATH}/collections/ansible_collections/${COLLECTION_NAMESPACE}/${PACKAGE_NAME}"

PATH_TO_PACKAGES="$(git rev-parse --show-toplevel)"

# Use a python3-compatible container
# https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html#container-images
DOCKER_IMG="ubuntu1804"

function _cleanup() {
  rm -r "${TMP_DIR_PATH}"
}

function inject_env_vars() {

  if [ "${TEST_SUITE}" != "integration" ]; then
    return
  fi

  if [ -z "${OP_CONNECT_HOST+x}" ] || [ -z "${OP_CONNECT_TOKEN+x}" ]; then
      echo "==> [ERROR] OP_CONNECT_HOST and OP_CONNECT_TOKEN environment vars are required."
      exit 1
  fi

  cd "${TMP_COLLECTIONS_PATH}/"
  # replace placeholders with env vars for integration tests
  find ./tests/integration/ -type f -name "*.yml" -exec sed -i '' "s|__OP_CONNECT_HOST__|${OP_CONNECT_HOST}|g" {} +
  find ./tests/integration/ -type f -name "*.yml" -exec sed  -i '' "s|__OP_CONNECT_TOKEN__|${OP_CONNECT_TOKEN}|g" {} +

  if [ ! -z "${OP_VAULT_ID+x}" ]; then
    find ./tests/integration -type f -name "*.yml" -exec sed -i '' "s|__OP_VAULT_ID__|${OP_VAULT_ID}|g" {} +
  fi

}

function setup() {
  # ansible-test has specific path requirements for Ansible Collection integration tests
  mkdir -p "${TMP_COLLECTIONS_PATH}"

  # copy all connect/{package names} folders into temp dir
  rsync -ar --exclude '.*' "${PATH_TO_PACKAGES}/" "${TMP_COLLECTIONS_PATH}"
}

function do_tests() {

  # `zz` is a throwaway value here
  # When the `if` cond sees `zz` it goes into the `else` block.
  if [ -z "${ANSIBLE_COLLECTIONS_PATHS+zz}" ]; then
    collection_path="${TMP_DIR_PATH}"
  else
    collection_path="${ANSIBLE_COLLECTIONS_PATH}:${TMP_DIR_PATH}"
  fi

  cd "${TMP_COLLECTIONS_PATH}/"

  echo "Initializing ansible-test ${TEST_SUITE} runner..........."
  ANSIBLE_COLLECTIONS_PATH="${collection_path}" ansible-test "${TEST_SUITE}" --docker "${DOCKER_IMG}"
}

trap _cleanup EXIT
setup
inject_env_vars
do_tests