import json
import os
import subprocess


class OpCLI:
    def __init__(self, service_account_token: str):
        self.sa = service_account_token
        self._set_service_account_token(service_account_token)

    def item_get(self, item: str, vault: str):
        return self._execute_command(["op", "item", "get", item, "--vault", vault, "--format=json"])

    def generic_item(self):
        pass

    def _set_service_account_token(self, service_account_token):
        self.env = os.environ.copy()
        self.env["OP_SERVICE_ACCOUNT"] = service_account_token

    def _execute_command(self, command_args: list[str]):
        result = subprocess.run(command_args, check=True, capture_output=True, env=self.env)
        return json.loads(result.stdout)
