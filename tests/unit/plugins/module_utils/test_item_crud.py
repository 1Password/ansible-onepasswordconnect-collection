from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, const


def test_create_item(mocker):
    params = {
        "vault_id": "Abc123",
        "category": const.ItemType.API_CREDENTIAL,
        "name": "My New Item",
        "favorite": True
    }

    mock_item = dict(params)
    mock_item["id"] = "abc123xyz9325"

    mock_api = mocker.Mock()
    mock_api.create_item.return_value = mock_item

    modified, new_item = vault.create_item(params, mock_api)

    assert modified is True
    mock_api.create_item.assert_called_once()


def test_check_mode(mocker):
    vault_id = "Abc123"

    mock_api = mocker.Mock()
    create_item_params = {
        "vault_id": vault_id,
        "category": const.ItemType.API_CREDENTIAL,
        "name": "My New Item",
        "favorite": True
    }
    modified, item = vault.create_item(create_item_params, mock_api, check_mode=True)
    assert modified
    assert mock_api.create_item.mock_calls == []

    item["vault"] = {"id": create_item_params["vault_id"]}
    item["id"] = "987654321"

    update_params = dict(create_item_params)
    update_params.update({"vault_id": vault_id, "name": "UPDATED Title"})

    modified, updated_item = vault.update_item(update_params, item, mock_api, check_mode=True)
    assert modified
    assert mock_api.update_item.mock_calls == []
    assert updated_item["title"] == update_params["name"]

    modified, delete_response = vault.delete_item(updated_item, mock_api, check_mode=True)
    assert modified
    assert delete_response == {}
    assert mock_api.delete_item.mock_calls == []


def test_delete_item(mocker):
    item = {
        "id": "xyz9876",
        "vault": {"id": "ABC123"},
        "category": const.ItemType.PASSWORD,
        "title": "My New Item"
    }
    mock_api = mocker.Mock()

    modified, new_item = vault.delete_item(item, mock_api)

    assert modified is True
    mock_api.delete_item.assert_called_once_with(item["vault"]["id"], item_id=item["id"])


def test_delete_item_when_does_not_exist(mocker):
    mock_api = mocker.Mock()

    non_existent_item = None
    modified, resp = vault.delete_item(non_existent_item, mock_api)

    assert modified is False
    assert not mock_api.delete_item.called


def test_update_item(mocker):
    vault_id = "Abc123"
    original_item = {
        "id": "XYZ123def456",
        "vault": {"id": vault_id},
        "title": "BEFORE_NAME",
        "category": const.ItemType.PASSWORD,
        "favorite": True
    }

    params = {
        "favorite": False,
        "title": "AFTER_NAME",
        "vault_id": vault_id,
        "category": const.ItemType.PASSWORD,
        "value": "hunter2",
        "fields": [
            {
                "label": "Password",
                "value": "hunter2",
                "field_type": const.FieldType.CONCEALED
            }
        ]
    }

    mock_api = mocker.Mock()
    mock_api.update_item.return_value = {
        "id": original_item["id"],
        "vault": original_item["vault"],
        "title": params["title"],
        "fields": params["fields"],
        "category": params["category"],
        "favorite": params["favorite"]
    }

    modified, updated_item = vault.update_item(params, original_item, mock_api)

    assert modified is True
    assert updated_item["favorite"] == params["favorite"]
    assert updated_item["title"] == params["title"]
    assert updated_item["vault"]["id"] == original_item["vault"]["id"]
