from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from ansible_collections.onepassword.connect.plugins.module_utils import vault, fields, const

NOTES_FIELD = {"id": "notesPlain", "type": "STRING", "purpose": "NOTES", "label": const.NOTES_FIELD_LABEL}
FIELD_FROM_SERVER_LABEL = "Secret Codeword"
FIELD_FROM_SERVER = {
    "id": "password",
    "type": "CONCEALED",
    "purpose": "PASSWORD",
    "label": FIELD_FROM_SERVER_LABEL,
    "value": "a-secret-password-2",
    "section": {"id": "SECTION1"}
}


def _get_field_by_label(label, fields):
    """Helper to pick field from list of returned fields"""
    return list(filter(lambda f: f["label"] == label, fields)).pop()


@pytest.fixture
def fieldset_from_server():
    return [
        FIELD_FROM_SERVER,
        NOTES_FIELD,
    ]


@pytest.fixture
def protected_fields_from_playbook():
    return [
        {
            "field_type": "string",
            "generate_value": True,
            "label": FIELD_FROM_SERVER_LABEL,
            "overwrite": False,
            "section": "SECTION1",
        }
    ]


@pytest.fixture
def mixed_protection_item_fields():
    return [
        {
            # Preserve the original
            "field_type": "string",
            "generate_value": True,
            "label": FIELD_FROM_SERVER_LABEL,
            "overwrite": False,
            "value": "Example"
        },
        {
            # Overwrite field, don't preserve original
            "field_type": "string",
            "value": "ABC123",
            "label": "UnprotectedField",
            "overwrite": True
        }
    ]


@pytest.mark.parametrize("fieldset, expected", (
        ([{"label": "test", "overwrite": False}], True),
        ([], True),
        ([{"label": "", "overwrite": False}], False),
        ([{"label": "", "overwrite": True}], True)
))
def test_protected_field_must_have_label(fieldset, expected):
    assert fields.protected_fields_have_label(fieldset) == expected


def test_server_created_fields_are_returned(fieldset_from_server, protected_fields_from_playbook):
    """Assert fields created automatically by the server (e.g. Notes) are unaffected by fieldset updates"""
    fieldset = fields.update_fieldset(
        fieldset_from_server,
        protected_fields_from_playbook
    )

    expected_field_labels = [NOTES_FIELD["label"], FIELD_FROM_SERVER_LABEL]
    returned_field_labels = [field.get("label") for field in fieldset]

    assert len(fieldset) == 2
    assert set(expected_field_labels) & set(returned_field_labels)


def test_protected_field_gets_old_value(fieldset_from_server, protected_fields_from_playbook):
    """Assert the protected field is set to the value retrieved from the server"""

    updated_fieldset = fields.update_fieldset(
        fieldset_from_server,
        protected_fields_from_playbook
    )

    field = _get_field_by_label(FIELD_FROM_SERVER_LABEL, updated_fieldset)

    assert field["value"] == FIELD_FROM_SERVER["value"]


def test_protected_field_drops_generator_config(fieldset_from_server, protected_fields_from_playbook):
    """Assert any generator-related attrs are removed if field is protected"""
    protected_fields = protected_fields_from_playbook[:]
    protected_fields[0].update({"generate_value": True, "generator_recipe": {"length": 3}})

    updated_fieldset = fields.update_fieldset(
        fieldset_from_server,
        protected_fields_from_playbook
    )

    field = _get_field_by_label(FIELD_FROM_SERVER_LABEL, updated_fieldset)

    assert (set(["generate_value", "generator_recipe"]) & set(field.keys())) == set()


def test_unprotected_fields_unaffected_by_protected_setting(fieldset_from_server, protected_fields_from_playbook):
    """Assert fields without the `overwrite` flag are overwritten"""

    unprotected_field = {
        # Overwrite field, don't preserve original
        "field_type": "string",
        "value": "ABC123",
        "label": "UnprotectedField",
        "overwrite": True
    }

    playbook_fieldset_with_unprotected_field = [*protected_fields_from_playbook, *[unprotected_field]]

    updated_fieldset = fields.update_fieldset(
        fieldset_from_server,
        playbook_fieldset_with_unprotected_field
    )

    result_field = _get_field_by_label(unprotected_field["label"], updated_fieldset)
    assert result_field["value"] == unprotected_field["value"]

    protected_field = _get_field_by_label(FIELD_FROM_SERVER_LABEL, updated_fieldset)
    assert protected_field["value"] == FIELD_FROM_SERVER["value"]
