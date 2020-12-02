from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.onepassword.connect.plugins.module_utils import const


def create_field(
        field_type,
        item_type,
        label=None,
        value=None,
        generate_value=False,
        generator_recipe=None,
        section_id=None,
        purpose=None
):
    """
    Creates a single Field dictionary from given configuration

    :param str field_type: Type ID for this field
    :param str item_type: Category value for the Item this field belongs to
    :param str label: Human-readable name for this field
    :param value: Value of the field
    :param bool generate_value: Indicate whether field is generated server-side
    :param dict generator_recipe: Customizations for value generator
    :param str section_id: Unique ID for the Item section the field should be placed into
    :param purpose: Specify field purpose if applicable
    :return: dict
    :rtype: dict
    """
    if not field_type or not item_type:
        raise TypeError("field_type and parent_item_type are required")

    field = {
        "label": label,
        "value": value,
        "type": field_type.upper(),
        "generate": bool(generate_value),
        "section": {"id": section_id} if section_id else None,
        "purpose": purpose or ""
    }

    if item_type.upper() in [const.ItemType.LOGIN, const.ItemType.PASSWORD]:
        # TODO: Username purpose handling?
        if field["type"] == const.FieldType.CONCEALED:
            field["purpose"] = "PASSWORD"

    if generate_value:
        field["recipe"] = _get_generator_recipe(generator_recipe)
        # Always ignore the provided value if user is requesting a generated value
        field["value"] = None

    return field


def update_fieldset(old_fields, new_fields):
    """Create new set of fields from the playbook params.

    Users may declare "overwrite=False" to reuse the field's value from the server
    IF AND ONLY IF the field has a label

    :param list of dict old_fields: Item fields returned by the server
    :param list of dict new_fields: Item fields as defined in the playbook
    :return list of dict
    """

    if not old_fields:
        # old item has no fields, skip processing
        # in most cases there will be at least ONE field (`notesField`)
        return new_fields

    return list(_merge_fields(old_fields, new_fields))


def _merge_fields(old_fields, new_fields):
    """Replace field value with value returned by the server.

    'Protected' field values should remain unchanged when running Ansible play

    :param list of dict old_fields: Item fields returned by the server
    :param list of dict new_fields: Item fields as defined in the playbook
    :return generator of dict
    """

    # TODO: Should Ansible ignore fields w/o labels?
    old = {f["label"].strip(): f for f in old_fields if f.get("label")}

    if const.NOTES_FIELD_LABEL in old:
        # Don't make changes to the notesField - not supported
        yield old[const.NOTES_FIELD_LABEL]

    for field in new_fields:
        immutable = all((
            not field.get("overwrite"),
            field.get("label"),
            field["label"] in old.keys()))
        if immutable:
            yield _field_with_old_value(field, old[field["label"]].get("value"))
        else:
            yield field


def _field_with_old_value(field_config, old_value):
    """Creates copy of a field, replacing its value with value from the server"""
    field = {**field_config, "value": old_value}

    # Remove generator config when preserving the old value
    field.pop("generate_value", None)
    field.pop("generator_recipe", None)

    return field


def protected_fields_have_label(fields):
    """Check for a field label when a field should persist old value"""
    if not fields:
        return True

    return all(field.get("label") for field in fields if field["overwrite"] is False)


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
    """Remap the list of fields to a dict of fields, where the key is the field label or id.

    Returns nicer format for pulling fields out of items.

    :param list of dict fieldset: List of field dictionaries
    :return dict
    """
    if not fieldset:
        return {}

    flattened = {}

    for field in fieldset:

        try:
            key = field["label"]
        except KeyError:
            key = field["id"]

        flattened[key] = field

    return flattened

