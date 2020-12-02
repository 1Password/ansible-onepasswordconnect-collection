from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, fields, const


def test_field_creation_defaults():
    params = {
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "label": "Test Item",
        "value": "MySecretValue",
        "generate_value": False
    }

    field = fields.create_field(**params)

    assert field["label"] == params["label"]
    assert field["type"] == params["field_type"].upper()
    assert field["generate"] == params["generate_value"]
    assert field["value"] == params["value"]
    assert field.get("recipe") is None
    assert field.get("section") is None
    assert field.get("purpose") == ""


def test_field_minimum_config():
    params = {}

    with pytest.raises(TypeError):
        fields.create_field(**params)

    field = fields.create_field(
        field_type=const.FieldType.STRING,
        item_type="login"
    )
    assert field["type"] is not None

    assert field["label"] is None
    assert field["value"] is None
    assert field["generate"] is False
    assert field["section"] is None


def test_field_value_generation_config_generate_is_false():
    params = {
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "value": "MySecretValue",
        "generate_value": False,
        "generator_recipe": {
            "length": 6,
            "include_letters": False
        }
    }

    field = fields.create_field(**params)

    # Generate false ==> don't overwrite value
    assert field["value"] == params["value"]
    assert field.get("recipe") is None


def test_field_value_generation_config_generate_is_true():
    params = {
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "value": "MySecretValue",
        "generate_value": True,
        "generator_recipe": {
            "length": 6
        }
    }

    field = fields.create_field(**params)

    # Generate false ==> don't overwrite value
    assert field["value"] is None
    assert field.get("recipe") is not None
    assert field["recipe"]["length"] == 6


def test_field_value_generation_character_settings():
    params = {
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "generate_value": True,
        "generator_recipe": {
            "length": 6,
            "include_letters": True,
            "include_symbols": False,
            "include_digits": None  # setting to None will NOT exclude the charset
        }
    }

    field = fields.create_field(**params)

    # Generate false ==> don't overwrite value
    assert field.get("recipe") is not None
    assert field["recipe"]["length"] == 6
    assert sorted(field["recipe"]["characterSets"]) == sorted(["LETTERS", "DIGITS"])


def test_item_creation_minimum_values():
    item_category = "custom"
    vault_id = "abc123"

    item = vault.assemble_item(
        vault_id=vault_id,
        category=item_category
    )

    assert item["title"] is None
    assert item["vault"]["id"] == vault_id
    assert item["category"] == item_category.upper()
    assert item["urls"] == []
    assert item["tags"] == []
    assert item["fields"] == []
    assert "sections" not in "item"


def test_item_with_fields_in_sections():
    fieldset = [
        {
            "label": "Example1",
            "section": "Odds Section",
            "value": "test1",
            "field_type": const.FieldType.STRING
        },
        {
            "label": "Example2",
            "section": "Evens Section",
            "value": "test2",
            "field_type": const.FieldType.CONCEALED
        },
        {
            "label": "Example 3",
            "section": "Odds Section",
            "field_type": const.FieldType.STRING
        }
    ]

    item_category = "custom"
    vault_id = "abc123"

    item = vault.assemble_item(
        vault_id=vault_id,
        category=item_category,
        fieldset=fieldset
    )

    assert item.get("sections") is not None
    assert len(item.get("sections")) == 2

    section_names = sorted((section["label"] for section in item.get("sections")))
    assert section_names == sorted(["Evens Section", "Odds Section"])
