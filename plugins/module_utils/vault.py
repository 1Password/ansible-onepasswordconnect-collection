from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from collections import namedtuple
from uuid import uuid4

from ansible_collections.onepassword.connect.plugins.module_utils import errors, fields

Section = namedtuple("Section", ["id", "label"])


def create_item(params, api_client):
    """
    Creates a new Item in the designated Vault.

    :param params: dict
    :param api_client:
    :return: (bool, dict) Where bool represents whether action created an Item in 1Password.
    """
    vault_id = params["vault_id"]
    op_item = assemble_item(
        vault_id=params["vault_id"],
        category=params["category"],
        title=params.get("name") or params.get("title"),
        urls=params.get("urls"),
        favorite=params.get("favorite"),
        fieldset=params.get("fields"),
        tags=params.get("tags")
    )
    new_item = api_client.create_item(vault_id, item=op_item)
    new_item["fields"] = fields.flatten_fieldset(new_item.get("fields"))

    return True, new_item


def upsert_item(params, api_client):
    """If Item with matching UUID or name exists, replaces all old Item properties. If Item not found, creates new Item.

    If the replacement Item is equal to the "original" item, no action is taken by Ansible.

    :param params: dict
    :param api_client:
    :return: (bool, dict) Where bool represents whether action modified an Item in 1Password.
    """
    if not fields.protected_fields_have_label(params.get("fields")):
        raise errors.Error("Fields with overwrite=False must have a label")

    vault_id = params.get("vault_id")
    item_name = params.get("title")
    item_id = params.get("uuid")

    try:
        if item_id:
            original = api_client.get_item_by_id(vault_id, item_id)
        else:
            original = api_client.get_item_by_name(vault_id, item_name)
    except errors.NotFoundError:
        return create_item(params, api_client)

    changed, updated_item = _update_item(original, params)

    if not changed:
        original["fields"] = fields.flatten_fields(original["fields"])
        return False, original

    item = api_client.update_item(updated_item["vault"]["id"], item=updated_item)
    item["fields"] = fields.flatten_fieldset(item.get("fields"))
    return changed, item


def delete_item(params, api_client):
    """
    Deletes an item or returns an empty dict if Item not found.

    :param params: dict Module parameters
    :param api_client:
    :return: (bool, dict) Where bool represents whether action modified an Item in 1Password.
    """

    vault_id = params.get("vault_id")

    item_id = params.get("uuid")

    if not item_id:
        try:
            op_item = api_client.get_item_by_name(vault_id, item_name=params.get("title"))
            item_id = op_item.get("id")
        except errors.NotFoundError:
            # Nothing to do, item does not exist
            return False, {}

    try:
        return True, api_client.delete_item(vault_id, item_id=item_id)
    except errors.NotFoundError:
        return False, {}


def _update_item(original_item, updated_item_params):
    item_fields = fields.update_fieldset(
        original_item.get("fields"),
        updated_item_params.get("fields")
    )

    updated_item = assemble_item(
        vault_id=original_item["vault"]["id"],
        category=updated_item_params["category"],
        title=updated_item_params.get("name") or updated_item_params.get("title"),
        urls=updated_item_params.get("urls"),
        favorite=updated_item_params.get("favorite"),
        tags=updated_item_params.get("tags"),
        fieldset=item_fields
    )

    updated_item.update({
        "id": original_item["id"],
    })
    return True, updated_item


def assemble_item(
        vault_id,
        category,
        title=None,
        urls=None,
        tags=None,
        favorite=None,
        fieldset=None,
):
    """
    Create a serialized Item from the given module parameters

    :param str vault_id: ID of Vault where Item will be stored
    :param str category: Defines the type of Item to create
    :param str title: Human-readable name for the Item
    :param list of str urls: Collection of URLs associated with the Item
    :param list of str tags: Searchable tags added to the item
    :param bool favorite: Toggle the Item's `favorite` setting
    :param list of dict fieldset: collection of fields for this Item
    :return: Assembled Item dict
    :rtype: dict
    """

    sections = {}

    item = {
        "title": title,
        "vault": {"id": vault_id},
        "category": category.upper(),
        "urls": [{"href": url} for url in urls or []],
        "tags": tags or [],
        "fields": []
    }

    if favorite:
        item["favorite"] = bool(favorite)

    if fieldset:
        for field_config in fieldset:
            if field_config.get("section"):
                # Squash sections with identical names
                # but continue respecting name casing
                section_name = field_config["section"].strip()

                section = sections.setdefault(
                    section_name,
                    Section(id=str(uuid4()), label=section_name)
                )
            else:
                section = None

            item["fields"].append(
                fields.create_field(
                    field_type=field_config.get("field_type") or field_config.get("type"),
                    item_type=item["category"],
                    label=field_config.get("label"),
                    value=field_config.get("value"),
                    generate_value=field_config.get("generate_value"),
                    generator_recipe=field_config.get("generator_recipe"),
                    section_id=section.id if section else None,
                    purpose=field_config.get("purpose")
                )
            )

    # Remap unique sections to expected schema format
    if sections:
        item["sections"] = [
            {"id": section.id, "label": section.label}
            for n, section in sections.items()
        ]

    return item
