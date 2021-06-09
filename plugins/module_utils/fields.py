from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import unicodedata
from ansible_collections.onepassword.connect.plugins.module_utils import const


def field_from_params(field_params, generate_field_value=False):
    if "field_type" not in field_params:
        raise TypeError("Field is missing type value")

    return {
        "type": field_params["field_type"].upper(),
        "label": field_params.get("label"),
        "section": field_params.get("section"),
        "recipe": _get_generator_recipe(field_params.get("generator_recipe")) if generate_field_value else None,
        "generate": generate_field_value,
        "value": None if generate_field_value else field_params.get("value")
    }


def create(field_params, previous_fields=None):
    if not field_params:
        return

    # TODO: Should Ansible ignore fields w/o labels?
    if not previous_fields:
        previous_fields = []

    for params in field_params:
        if params.get("label") == const.NOTES_FIELD_LABEL:
            # The Notes field should not be editable by Ansible,
            # and the old value is preserved if it exists
            existing_notes_field = _get_field_by_label(
                previous_fields, const.NOTES_FIELD_LABEL
            )
            if existing_notes_field:
                yield existing_notes_field
            continue

        should_generate_value = False

        if params.get("generate_value") == const.GENERATE_ALWAYS:
            should_generate_value = True
        elif params.get("generate_value") == const.GENERATE_ON_CREATE:
            old_field = _get_field_by_label(
                previous_fields, params.get("label")
            )
            if not old_field:
                should_generate_value = True
            else:
                params.update({
                    "value": old_field.get("value"),
                    # Don't allow user to change the preserved value's type
                    "field_type": old_field.get("type")
                })

        yield field_from_params(
            params,
            generate_field_value=should_generate_value
        )


def _get_field_by_label(fields, label):
    if not fields or not label:
        return None

    try:
        iter(fields)
    except TypeError:
        return None

    label = normalize_label(label)

    return next((
        field for field in fields
        if normalize_label(field.get("label")) == label
    ), None)


def normalize_label(raw_str):
    """Standardizes utf-8 encoding for comparison
     and removes leading/trailing spaces"""
    if not raw_str:
        return None

    unicode_normalized = unicodedata.normalize("NFKD", raw_str)
    return unicode_normalized.strip()


def _get_generator_recipe(config):
    """
    Creates dict with Password Generator Recipe settings
    :param config: Dict[str, Any]
    :return: dict
    """
    if not config:
        # Returning none/empty dict when "generate_value" is True
        # tells the server to use recipe defaults
        return None

    character_sets = []

    if config.get("include_digits") is not False:
        character_sets.append("DIGITS")
    if config.get("include_letters") is not False:
        character_sets.append("LETTERS")
    if config.get("include_symbols") is not False:
        character_sets.append("SYMBOLS")

    return dict(
        length=config["length"],
        characterSets=character_sets
    )


def flatten_fieldset(fieldset):
    """Remap the list of fields to a dict of fields, where the key is the field label.
    If label is undefined, use the field UUID instead.

    Remapping provides a nicer interface for the user when
    accessing fields within Ansible playbooks.

    :param list of dict fieldset: List of field dictionaries
    :return dict
    """
    if not fieldset:
        return {}

    flattened = {}

    for field in fieldset:
        key = field.get("label")
        if not key:
            key = field["id"]
        flattened[key] = field

    return flattened
