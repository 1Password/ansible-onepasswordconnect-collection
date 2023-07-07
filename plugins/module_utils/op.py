import json
import os
import subprocess


class OpCLI:
    def __init__(self, service_account_token: str):
        self._set_service_account_token(service_account_token)

    def item_get(self, vault: str, item: str):
        try:
            return self._execute_command(
                ["op", "item", "get", item, "--vault", vault, "--format=json"]
            )
        except subprocess.CalledProcessError:
            return None

    def delete_item(self, vault: str, item: str):
        return self._execute_command(["op", "item", "delete", item, "--vault", vault])

    def create_item(self, item):
        return subprocess.run(
            ["op", "item", "create", "--format", "json"],
            input=bytes(json.dumps(item).encode("utf-8")),
            check=True,
            capture_output=False,
            env=self.env,
        )

    def update_item(self, vault: str, item: str):
        return self._execute_command(["op", "item", "edit", item, "--vault", vault])

    def _set_service_account_token(self, service_account_token):
        self.env = os.environ.copy()
        self.env["OP_SERVICE_ACCOUNT_TOKEN"] = service_account_token

    def _execute_command(self, command_args: list[str]):
        result = subprocess.run(
            command_args, check=True, capture_output=True, env=self.env
        )

        if len(result.stdout) == 0:
            return {}

        return json.loads(result.stdout)
