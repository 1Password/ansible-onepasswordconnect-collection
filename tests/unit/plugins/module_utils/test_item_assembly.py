from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, fields, const, errors


def test_field_creation_defaults():
    params = {
        "field_type": const.FieldType.STRING,
        "label": "Test Item",
        "value": "MySecretValue",
        "generate_value": "never"
    }

    field = list(fields.create([params])).pop()
    assert field["label"] == params["label"]
    assert field["type"] == params["field_type"].upper()
    assert field["generate"] is False
    assert field["value"] == params["value"]
    assert field.get("recipe") is None
    assert field.get("section") is None
    assert field.get("purpose") is None


def test_field_minimum_config():
    incomplete_field_defn = [{"label": "should fail, missing field type"}]

    with pytest.raises(TypeError):
        list(fields.create(incomplete_field_defn))

    field_defns = [{
        "field_type": const.FieldType.STRING,
    }]

    field = list(fields.create(field_defns)).pop()

    assert field["type"] is not None
    assert field["label"] is None
    assert field["value"] is None
    assert field["generate"] is False
    assert field["section"] is None


def test_field_value_generation_config_generate_is_false():
    field_params = {
        "field_type": const.FieldType.STRING,
        "value": "MySecretValue",
        "generate_value": const.GENERATE_NEVER,
        "generator_recipe": {
            "length": 6,
            "include_letters": False
        }
    }

    field = list(fields.create([field_params])).pop()

    # Generate false ==> don't overwrite value
    assert field["value"] == field_params["value"]
    assert field.get("recipe") is None


def test_field_value_generation_config_generate_is_true():
    field_params = {
        "field_type": const.FieldType.STRING,
        "item_type": "login",
        "value": "MySecretValue",
        "generate_value": const.GENERATE_ALWAYS,
        "generator_recipe": {
            "length": 6
        }
    }

    field = list(fields.create([field_params])).pop()

    # Generate true ==> clear value, the generator will overwrite it
    assert field["value"] is None
    assert field.get("recipe") is not None
    assert field["recipe"]["length"] == 6
    assert field["generate"] is True


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

    assert field.get("recipe") is not None
    assert field["recipe"]["length"] == 6
    assert sorted(field["recipe"]["characterSets"]) == sorted(["LETTERS", "DIGITS"])


def test_item_creation_minimum_values():
    item_category = const.ItemType.API_CREDENTIAL
    vault_id = "abc123"

    item = vault.assemble_item(
        vault_id=vault_id,
        category=item_category
    )

    assert item["title"] is None
    assert item["vault"]["id"] == vault_id
    assert item["category"] == item_category
    assert not item["urls"]
    assert not item["tags"]
    assert not item["fields"]
    assert "sections" not in "item"


def test_item_with_fields_in_sections():
    sections = ("Odds Section", "Evens Section")

    fieldset = [
        {
            "label": "Example1",
            "section": sections[0],
            "value": "test1",
            "type": const.FieldType.STRING,
            "generate_field": const.GENERATE_NEVER,
        },
        {
            "label": "Example2",
            "section": sections[1],
            "value": "test2",
            "generate_field": const.GENERATE_NEVER,
            "type": const.FieldType.CONCEALED
        },
        {
            "label": "Example 3",
            "section": sections[0],
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
    # Expect duplicate section names to be combined
    assert len(item.get("sections")) == 2

    item_sections = sorted((section["label"] for section in item.get("sections")))
    assert item_sections == sorted(sections)


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


def test_notes_field_is_unchanged():
    previous_fields = [{
        "id": "123xyz",
        "label": const.NOTES_FIELD_LABEL,
        "type": const.FieldType.STRING,
        "value": "i am a note field"
    }]

    params = [{
        "label": const.NOTES_FIELD_LABEL,
        "field_type": const.FieldType.CONCEALED,
        "value": "updated notes field value"
    }]

    field = list(fields.create(params, previous_fields=previous_fields)).pop()

    assert field.get("value") == "i am a note field"
    assert field.get("id") == "123xyz"
    assert field.get("type") == const.FieldType.STRING


FIELD_PURPOSE_TESTCASES = [
    pytest.param(
        const.ItemType.API_CREDENTIAL, "xyz", const.FieldType.STRING, const.PURPOSE_NONE, id="default_field_purpose"
    ),
    pytest.param(
        const.ItemType.PASSWORD, "password", const.FieldType.CONCEALED, const.PURPOSE_PASSWORD,
        id="primary_password_for_password_item"
    ),
    pytest.param(
        const.ItemType.SERVER, "password", const.FieldType.CONCEALED, const.PURPOSE_NONE,
        id="item_type_does_not_use_password_field_purpose"
    ),
    pytest.param(
        const.ItemType.SERVER, "username", const.FieldType.STRING, const.PURPOSE_NONE,
        id="item_type_does_not_use_username_field_purpose"
    ),
    pytest.param(
        const.ItemType.LOGIN, "password", const.FieldType.CONCEALED, const.PURPOSE_PASSWORD,
        id="primary_password_for_login_item",
    ),
    pytest.param(
        const.ItemType.LOGIN, "username", const.FieldType.STRING, const.PURPOSE_USERNAME,
        id="primary_username_for_login_item",
    ),
    pytest.param(
        const.ItemType.LOGIN, "password", const.FieldType.STRING, const.PURPOSE_NONE,
        id="wrong_field_type_for_login_item_primary_password",
    ),
    pytest.param(
        const.ItemType.LOGIN, "username", const.FieldType.OTP, const.PURPOSE_NONE,
        id="wrong_field_type_for_login_item_primary_username",
    ),
    pytest.param(
        const.ItemType.API_CREDENTIAL, const.NOTES_FIELD_LABEL, const.FieldType.STRING, const.PURPOSE_NOTES,
        id="notes_field_is_assigned_notes_purpose"
    ),
]


@pytest.mark.parametrize("item_type,label,field_type,expected_purpose", FIELD_PURPOSE_TESTCASES)
def test_field_purpose_assignment(item_type, label, field_type, expected_purpose):
    """Assert field purpose is set when item type and field type meet criteria"""

    fields = [
        {
            "label": label,
            "type": field_type,
            "value": "example123",
        },
    ]

    item = vault.assemble_item(
        vault_id="1234xyz",
        category=item_type,
        fieldset=fields
    )

    assert len(item["fields"])
    assert item["fields"][0]["purpose"] == expected_purpose


def test_username_and_password_purpose_is_limited_to_one_field():
    """Assert the field purpose assignment applies to the last field that
    matches the purpose criteria.
    """
    two_primary_password_fields = [
        {
            "label": "password",
            "type": const.FieldType.CONCEALED,
            "value": "FIRST_PASSWORD_FIELD",
        },
        {
            "label": "password",
            "type": const.FieldType.CONCEALED,
            "value": "SECOND_PASSWORD_FIELD",
        },
    ]

    with pytest.raises(errors.PrimaryPasswordAlreadyExists):
        vault.assemble_item(
            vault_id="1234xyz",
            category=const.ItemType.PASSWORD,
            fieldset=two_primary_password_fields
        )

    two_primary_username_fields = [
        {
            "label": "username",
            "type": const.FieldType.STRING,
            "value": "FIRST_USERNAME_FIELD",
        },
        {
            "label": "username",
            "type": const.FieldType.STRING,
            "value": "SECOND_USERNAME_FIELD",
        },
    ]

    with pytest.raises(errors.PrimaryUsernameAlreadyExists):
        vault.assemble_item(
            vault_id="1234xyz",
            category=const.ItemType.LOGIN,
            fieldset=two_primary_username_fields
        )


def test_password_item_type_requires_primary_password():
    """Assert at least one field with type `concealed` is defined
    when creating item with type ItemType.PASSWORD.
    """
    fields = [
        {
            "label": "Garage Code",
            "type": const.FieldType.STRING,
            "value": "1234",
        },
        {
            "label": "Anniversary",
            "type": const.FieldType.MONTH_YEAR,
            "value": "12/10",
        },
    ]

    with pytest.raises(errors.PrimaryPasswordUndefined):
        vault.assemble_item(
            vault_id="1234xyz",
            category=const.ItemType.PASSWORD,
            fieldset=fields
        )
