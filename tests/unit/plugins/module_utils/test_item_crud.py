from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, api, errors, const


def test_create_item(mocker):
    params = {
        "vault_id": "Abc123",
        "category": const.ItemType.PASSWORD,
        "title": "My New Item",
        "favorite": True
    }

    mock_api = mocker.Mock()
    mock_api.create_item.return_value = {}

    modified, new_item = vault.create_item(params, mock_api)

    assert modified is True
    mock_api.create_item.assert_called_once()


def test_delete_item(mocker):
    item_id = "abc123"
    params = {
        "vault_id": "Abc123",
        "category": const.ItemType.PASSWORD,
        "title": "My New Item",
        "favorite": True
    }

    mock_api = mocker.Mock()
    mock_api.get_item_by_name.return_value = {"id": item_id, "title": params["title"]}

    modified, new_item = vault.delete_item(params, mock_api)

    assert modified is True
    mock_api.get_item_by_name.assert_called_once_with(params["vault_id"], item_name=params["title"])
    mock_api.delete_item.assert_called_once_with(params["vault_id"], item_id=item_id)


def test_delete_item_when_does_not_exist(mocker):
    params = {
        "vault_id": "Abc123",
        "category": const.ItemType.PASSWORD,
        "title": "My New Item",
        "favorite": True
    }

    mock_api = mocker.Mock()
    mock_api.get_item_by_name.side_effect = errors.NotFoundError

    modified, resp = vault.delete_item(params, mock_api)

    assert modified is False
    assert not mock_api.delete_item.called


def test_update_item_create_when_not_exists(mocker):
    params = {
        "uuid": "XYZ123def456",
        "vault_id": "Abc123",
        "category": const.ItemType.PASSWORD,
        "title": "My New Item",
        "favorite": True
    }

    mock_api = mocker.Mock()
    mock_api.get_item_by_id.side_effect = errors.NotFoundError
    mock_api.create_item.return_value = {"id": params["uuid"], "vault": {"id": params["vault_id"]}}

    modified, updated_item = vault.upsert_item(params, mock_api)

    assert modified is True
    assert updated_item
