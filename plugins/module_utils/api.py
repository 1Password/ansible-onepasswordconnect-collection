from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import os
import base64

import sys
import re

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote, urlunparse, urlparse
from ansible_collections.onepassword.connect.plugins.module_utils import errors, const


def create_client(module):
    if not module.params.get("hostname") or not module.params.get("token"):
        raise errors.AccessDeniedError(message="Server hostname or auth token not defined")

    return OnePassword(
        hostname=module.params["hostname"],
        token=module.params["token"],
        module=module
    )


class OnePassword:
    API_VERSION = "v1"

    def __init__(self, hostname, token, module):
        self.hostname = hostname
        self.token = token
        self._module = module
        self._user_agent = _format_user_agent(
            const.COLLECTION_VERSION,
            python_version=".".join(str(i) for i in sys.version_info[:3]),
            ansible_version=self._module.ansible_version
        )

    def _send_request(self, path, method="GET", data=None, params=None):
        fetch_kwargs = {
            "url": build_endpoint(self.hostname, path, params=params, api_version=self.API_VERSION),
            "method": method,
            "headers": self._build_headers(),
        }

        if method.upper() in ["POST", "PUT", "PATCH"]:
            fetch_kwargs["data"] = self._module.jsonify(data)

        response_body = {}

        resp, info = fetch_url(self._module, **fetch_kwargs)
        if resp:
            try:
                response_body = json.loads(resp.read().decode("utf-8"))
            except (AttributeError, ValueError):
                if info.get("status") == 204:
                    # No Content response
                    return {}

                msg = "Server returned error with invalid JSON: {err}".format(
                    err=info.get("msg", "<Undefined error>")
                )
                return self._module.fail_json(msg=msg)
        else:
            raise_for_error(info)

        return response_body

    def _build_headers(self):
        return {
            "Authorization": "Bearer {token}".format(token=self.token),
            "User-Agent": self._user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_item_by_id(self, vault_id, item_id):
        path = "/vaults/{vault_id}/items/{item_id}".format(vault_id=vault_id, item_id=item_id)
        return self._send_request(path)

    def get_item_by_name(self, vault_id, item_name):
        try:
            item = self._get_item_id_by_name(vault_id, item_name)
            item_id = item["id"]
        except KeyError:
            raise errors.NotFoundError

        return self.get_item_by_id(vault_id, item_id)

    def create_item(self, vault_id, item):
        path = "/vaults/{vault_id}/items".format(vault_id=vault_id)
        return self._send_request(path, method="POST", data=item)

    def update_item(self, vault_id, item):
        path = "/vaults/{vault_id}/items/{item_id}".format(vault_id=item["vault"]["id"], item_id=item["id"])
        return self._send_request(path, method="PUT", data=item)

    def delete_item(self, vault_id, item_id):
        path = "/vaults/{vault_id}/items/{item_id}".format(vault_id=vault_id, item_id=item_id)
        return self._send_request(path, method="DELETE")

    def get_vaults(self):
        path = "/vaults"
        return self._send_request(path)

    def get_vault_id_by_name(self, vault_name):
        """Find the vault ID associated with the given vault name

        Loops through the results of the 'GET vault' query and tries
        to do an exact match with each vault name that is returned.
        :param vault_name: Name of the requested vault
        : return: str
        """
        resp = self.get_vaults()

        for vault in resp:
            if vault["name"] == vault_name:
                return vault["id"]
        raise errors.NotFoundError

    def _get_item_id_by_name(self, vault_id, item_name):
        """Find the Item ID associated with the given Item Name

        Loops through results of SCIM-style query and tries to
        do an exact match with each returned Item Title and the given Item title
        :param vault_id:
        :param item_name: Title parameter of the requested Item
        :return: str
        """
        query_filter = {"filter": 'title eq "{item_name}"'.format(item_name=item_name)}

        path = "/vaults/{vault_id}/items".format(vault_id=vault_id)
        resp = self._send_request(path, params=query_filter)

        if not resp:
            raise errors.NotFoundError
        if len(resp) > 1:
            raise errors.APIError(
                message="More than 1 match found for an Item with that name. Please adjust your search query."
            )

        return resp[0]


def build_endpoint(hostname, path, params=None, api_version=None):
    url_parts = list(urlparse(hostname))

    if not api_version:
        api_version = OnePassword.API_VERSION

    # Path _may_ have a space in it if client passes item name, for example
    url_parts[2] = "{api_version}/{path}".format(
        api_version=api_version,
        path=quote(path.strip('/'))
    )
    if params:
        url_parts[4] = urlencode(params)
    return urlunparse(url_parts)


def raise_for_error(response_info):
    try:
        response_info_body = json.loads(response_info.get("body").decode("utf-8"))
        err_details = {
            "message": response_info_body.get("message"),
            "status_code": response_info_body.get("status")
        }
    except (AttributeError, ValueError):
        # `body` key not present if urllib throws an error ansible doesn't handle
        err_details = {
            "message": response_info.get("msg", "Error not defined"),
            "status_code": response_info.get("status")
        }

    if err_details["status_code"] >= 500:
        raise errors.ServerError(**err_details)
    elif err_details["status_code"] == 404:
        raise errors.NotFoundError(**err_details)
    elif err_details["status_code"] in [401, 403]:
        raise errors.AccessDeniedError(**err_details)
    elif err_details["status_code"] == 400:
        raise errors.BadRequestError(**err_details)
    else:
        raise errors.APIError(**err_details)


def _format_user_agent(collection_version, python_version=None, ansible_version=None):
    return "op-connect-ansible/{version} Python/{py_version} Ansible/{ansible}".format(
        version=collection_version,
        py_version=python_version or "unknown",
        ansible=ansible_version or "unknown"
    )


# Client UUIDs must be exactly 26 characters.
CLIENT_UUID_LENGTH = 26


def valid_client_uuid(uuid):
    """Checks whether a given UUID meets the client UUID spec"""
    # triple curly braces needed to escape f-strings as regex quantifiers
    return re.match(rf"^[0-9a-z]{{{CLIENT_UUID_LENGTH}}}$", uuid) is not None


def create_client_uuid():
    """Creates a valid client UUID.

    The UUID is not intended to be cryptographically random."""
    rand_bytes = os.urandom(16)
    base32_utf8 = base64.b32encode(rand_bytes).decode("utf-8")
    return base32_utf8.rstrip("=").lower()
