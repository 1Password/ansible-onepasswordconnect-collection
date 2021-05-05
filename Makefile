export MAIN_BRANCH ?= main

.DEFAULT_GOAL := help
.PHONY: test test/unit test/integration build clean release/prepare release/tag .check_bump_type .check_git_clean help

GIT_BRANCH := $(shell git symbolic-ref --short HEAD)
WORKTREE_CLEAN := $(shell git status --porcelain 1>/dev/null 2>&1; echo $$?)
SCRIPTS_DIR := $(CURDIR)/scripts

curVersion := $$(sed -n -E 's/^version: ([0-9]+\.[0-9]+\.[0-9]+)$/\1/p' galaxy.yml)

test: test/unit ## Run unit tests in a Docker container
test/unit:
	$(SCRIPTS_DIR)/run-tests.sh units

test/integration:	## Run integration tests inside a Docker container
	$(SCRIPTS_DIR)/run-tests.sh integration

build: clean	## Build collection artifact
	ansible-galaxy collection build --output-path dist/

clean:	## Removes dist/ directory
	@rm -rf ./dist

help:	## Prints this help message
	@grep -E '^[\/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## Release functions =====================

release/prepare: .check_git_clean	## Bumps version and creates release branch (call with 'release/prepare version=<new_version_number>')

	@test $(version) || (echo "[ERROR] version argument not set."; exit 1)
	@git fetch --quiet origin $(MAIN_BRANCH)

	@sed -i.tmp -E 's/^(version:) ([0-9]+\.[0-9]+\.[0-9]+)$$/\1 "$(version)"/' galaxy.yml
	@sed -i.tmp -E 's/^(COLLECTION_VERSION) = "(.+)"$$/\1 = "$(version)"/' plugins/module_utils/const.py

	@NEW_VERSION=$(version) $(SCRIPTS_DIR)/prepare-release.sh
	@rm -f galaxy.yml.tmp plugins/module_utils/const.py.tmp


release/tag: .check_git_clean	## Creates git tag using version from package.json
	@git pull --ff-only
	@echo "Applying tag 'v$(curVersion)' to HEAD..."
	@git tag --sign "v$(curVersion)" -m "Release v$(curVersion)"
	@echo "[OK] Success!"
	@echo "Remember to call 'git push --tags' to persist the tag."

## Helper functions =====================

.check_git_clean:
ifneq ($(GIT_BRANCH), $(MAIN_BRANCH))
	@echo "[ERROR] Please checkout default branch '$(MAIN_BRANCH)' and re-run this command."; exit 1;
endif
ifneq ($(WORKTREE_CLEAN), 0)
	@echo "[ERROR] Uncommitted changes found in worktree. Address them and try again."; exit 1;
endif
