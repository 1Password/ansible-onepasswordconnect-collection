from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, fields, const


def test_field_creation_defaults():
    params = [
        {
            "field_type": const.FieldType.STRING,
            "label": "Test Item",
            "value": "MySecretValue",
            "generate_value": "never"
        }
    ]

    field = list(fields.create(params)).pop()
    assert field["label"] == params[0]["label"]
    assert field["type"] == params[0]["field_type"].upper()
    assert field["generate"] is False
    assert field["value"] == params[0]["value"]
    assert field.get("recipe") is None
    assert field.get("section") is None
    assert field.get("purpose") is None


def test_field_minimum_config():
    incomplete_field_defn = [{"label": "should fail, missing field type"}]

    with pytest.raises(TypeError):
        list(fields.create(incomplete_field_defn))

    field_defns = [{
        "field_type": const.FieldType.STRING,
        "item_type": "login"
    }]

    field = list(fields.create(field_defns)).pop()

    assert field["type"] is not None
    assert field["label"] is None
    assert field["value"] is None
    assert field["generate"] is False
    assert field["section"] is None


def test_field_value_generation_config_generate_is_false():
    field_defns = [{
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "value": "MySecretValue",
        "generate_value": const.GENERATE_NEVER,
        "generator_recipe": {
            "length": 6,
            "include_letters": False
        }
    }]

    field = list(fields.create(field_defns)).pop()

    # Generate false ==> don't overwrite value
    assert field["value"] == field_defns[0]["value"]
    assert field.get("recipe") is None


def test_field_value_generation_config_generate_is_true():
    field_defns = [{
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "value": "MySecretValue",
        "generate_value": const.GENERATE_ALWAYS,
        "generator_recipe": {
            "length": 6
        }
    }]

    field = list(fields.create(field_defns)).pop()

    # Generate false ==> don't overwrite value
    assert field["value"] is None
    assert field.get("recipe") is not None
    assert field["recipe"]["length"] == 6


def test_field_value_generation_character_settings():
    params = [{
        "field_type": const.FieldType.STRING,
        "generate_value": const.GENERATE_ALWAYS,
        "generator_recipe": {
            "length": 6,
            "include_letters": True,
            "include_symbols": False,
            "include_digits": None  # setting to None will NOT exclude the charset
        }
    }]

    field = list(fields.create(params)).pop()

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
            "type": const.FieldType.STRING,
            "generate_field": const.GENERATE_NEVER,
        },
        {
            "label": "Example2",
            "section": "Evens Section",
            "value": "test2",
            "generate_field": const.GENERATE_NEVER,
            "type": const.FieldType.CONCEALED
        },
        {
            "label": "Example 3",
            "section": "Odds Section",
            "type": const.FieldType.STRING,
            "generate_field": const.GENERATE_NEVER,
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


def test_field_value_generation_on_create_only():
    previous_fields = [{
        "label": "EXAMPLE 123",
        "value": "example/value/test",
        "type": const.FieldType.STRING,
    }]

    params = [{
        "label": "EXAMPLE 123",
        "field_type": const.FieldType.STRING,
        "generate_value": const.GENERATE_ON_CREATE,
        "generator_recipe": {
            "length": 6,
            "include_letters": True,
            "include_symbols": False,
        }
    }]

    field = list(fields.create(params, previous_fields=previous_fields)).pop()

    assert field.get("value") == previous_fields[0]["value"]


def test_notes_field_is_not_updated():
    previous_fields = [{
        "label": const.NOTES_FIELD_LABEL,
        "value": "i am a note field"
    }]

    params = [{
        "label": const.NOTES_FIELD_LABEL,
        "field_type": const.FieldType.STRING,
        "value": "updated notes field value"
    }]

    field = list(fields.create(params, previous_fields=previous_fields)).pop()

    assert field.get("value") == "i am a note field"
