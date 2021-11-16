from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import api, errors


def _format_error(error):
    """Creates an ansible-compatible `info` object that's returned by fetch_url"""
    return {"status": error.get("status"), "body": json.dumps(error).encode("utf8")}


URL_SEGMENTS = (
    ("http://localhost:8080", "example/path/", "v1", None, "http://localhost:8080/v1/example/path"),
    ("http://localhost/", "/example/", "v1", None, "http://localhost/v1/example"),
    ("http://1password.com", "/example", "v1", None, "http://1password.com/v1/example"),
    ("http://1password.com/", "example", "v1", None, "http://1password.com/v1/example"),
    ("http://1password.com", "example", None, None, "http://1password.com/{0}/example".format(api.OnePassword.API_VERSION)),
    ("http://localhost:8080", "/item/with space", "v1", None, "http://localhost:8080/v1/item/with%20space"),
    ("http://localhost:8080", "/item/with space", "v1", {"filter": "example eq 'test'"},
     "http://localhost:8080/v1/item/with%20space?filter=example+eq+%27test%27"),
)


@pytest.mark.parametrize("hostname, path, version, params, expected", URL_SEGMENTS)
def test_building_api_endpoint(hostname, path, version, params, expected):
    assert api.build_endpoint(hostname, path, params=params, api_version=version) == expected


@pytest.mark.parametrize("response_info, expected_exception", (
    (_format_error({"status": 500, "body": "serverError"}), errors.ServerError),
    (_format_error({"status": 404, "body": "notFound"}), errors.NotFoundError),
    (_format_error({"status": 401, "body": "unauthenticated"}), errors.AccessDeniedError),
    (_format_error({"status": 403, "body": "unauthorized"}), errors.AccessDeniedError),
    (_format_error({"status": 400, "body": "badRequest"}), errors.BadRequestError),
    (_format_error({"status": 499, "body": "generalCatchAll"}), errors.APIError),  # Any 4XX except the 4XX errors
))
def test_raise_for_error(response_info, expected_exception):
    with pytest.raises(expected_exception) as exc:
        api.raise_for_error(response_info)

        # Confirm error has expected attributes, too
        assert getattr(exc.value, "message") == response_info.get("body").decode("utf8")
        assert getattr(exc.value, "status_code") == response_info.get("status_code")


def test_api_client_factory_error_when_config_not_found(mocker):
    module = mocker.MagicMock()
    module.params = {}

    with pytest.raises(errors.AccessDeniedError):
        api.create_client(module)


def test_api_client_factory_creates_client(mocker):
    api_client_params = {"hostname": "http://localhost:8000", "token": "exampleToken"}

    module = mocker.MagicMock()
    module.params = api_client_params

    op_api_client = api.create_client(module)

    assert op_api_client.hostname == api_client_params["hostname"]
    assert op_api_client.token == api_client_params["token"]


@pytest.mark.parametrize("uuid, expected", (
    ("", False),
    ("1" * api.CLIENT_UUID_LENGTH, True),
    ("a" * api.CLIENT_UUID_LENGTH, True),
    ("x" * (api.CLIENT_UUID_LENGTH + 1), False),
    ("C5S3OVFSOLRWUSY1KP50ABCDEF", False),
    ("3R99IBO3J", False),
    ("cqdqekfpdwsb5dl2u4ljge2pdf", True)
))
def test_valid_client_uuid(uuid, expected):
    assert api.valid_client_uuid(uuid) == expected


def test_create_client_uuid():
    uuid = api.create_client_uuid()
    assert api.valid_client_uuid(uuid) is True
