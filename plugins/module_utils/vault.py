from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from collections import namedtuple
from uuid import uuid4

from ansible.module_utils.common.dict_transformations import recursive_diff
from ansible_collections.onepassword.connect.plugins.module_utils import errors, fields, const

Section = namedtuple("Section", ["id", "label"])


def find_item(params, api_client):
    """
    Searches for an item by its title or UUID.

    The search is limited to the vault_id passed by the module parameters.
    :param params: Module parameters dictionary
    :param api_client: Connect API client instance
    :return: dict | None
    """
    vault_id = params.get("vault_id")
    if not vault_id:
        raise errors.MissingVaultID

    item_name = params.get("title")
    item_id = params.get("uuid")

    try:
        if item_id:
            return api_client.get_item_by_id(vault_id, item_id)
        else:
            return api_client.get_item_by_name(vault_id, item_name)
    except errors.NotFoundError:
        return None


def create_item(params, api_client, check_mode=False):
    """
    Creates a new Item in the designated Vault.

    :param params: dict Values and fields for the new item
    :param api_client: Connect API client
    :param check_mode: Whether Ansible is running in check mode.  No changes saved if True.
    :return: (bool, dict) Where bool represents whether action created an Item in 1Password.
    """

    vault_id = params.get("vault_id")
    if not vault_id:
        raise errors.MissingVaultID

    item_fields = fields.create(params.get("fields"))

    op_item = assemble_item(
        vault_id=vault_id,
        category=params["category"].upper(),
        title=params.get("name"),
        urls=params.get("urls"),
        favorite=params.get("favorite"),
        fieldset=item_fields,
        tags=params.get("tags")
    )

    if check_mode:
        op_item["fields"] = fields.flatten_fieldset(op_item.get("fields"))
        return True, op_item

    new_item = api_client.create_item(params["vault_id"], item=op_item)
    new_item["fields"] = fields.flatten_fieldset(new_item.get("fields"))
    return True, new_item


def update_item(params, original_item, api_client, check_mode=False):
    """If Item with matching UUID or name exists, replaces all old Item properties. If Item not found, creates new Item.

    If the replacement Item is equal to the "original" item, no action is taken by Ansible.

    :param params: dict Values to replace the existing values.
    :param original_item The item returned by the server. Values may be copied from this item while updating.
    :param api_client: Connect API client
    :param check_mode: Whether Ansible is running in check mode.  No changes saved if True.
    :return: (bool, dict) Where bool represents whether action modified an Item in 1Password.
    """

    try:
        vault_id = original_item["vault"]["id"]
    except KeyError:
        raise errors.MissingVaultID("Original item missing Vault ID")

    item_fields = fields.create(
        params.get("fields"),
        previous_fields=original_item.get("fields")
    )

    updated_item = assemble_item(
        vault_id=vault_id,
        category=params["category"].upper(),
        title=params.get("name"),
        urls=params.get("urls"),
        favorite=params.get("favorite"),
        tags=params.get("tags"),
        fieldset=item_fields
    )

    updated_item.update({
        "id": original_item["id"],
    })
    changed = recursive_diff(original_item, updated_item)

    if not bool(changed):
        original_item["fields"] = fields.flatten_fields(original_item["fields"])
        return False, original_item

    if check_mode:
        updated_item["fields"] = fields.flatten_fieldset(updated_item.get("fields"))
        return changed, updated_item

    item = api_client.update_item(updated_item["vault"]["id"], item=updated_item)
    item["fields"] = fields.flatten_fieldset(item.get("fields"))
    return bool(changed), item


def delete_item(item, api_client, check_mode=False):
    """
    Deletes an item or returns an empty dict if Item not found.

    :param item: dict Item to be deleted
    :param api_client: Connect API client
    :param check_mode: Whether Ansible is running in check_mode. No changes saved if True.
    :return: (bool, dict) Where bool represents whether action modified an Item in 1Password.
    """

    if not item:
        # Nothing to do if item not given
        return False, {}

    vault_id = item.get("vault", {}).get("id")
    if not vault_id:
        raise errors.MissingVaultID

    if check_mode:
        return True, {}

    try:
        return True, api_client.delete_item(vault_id, item_id=item["id"])
    except errors.NotFoundError:
        # Item does not exist, nothing to do
        return False, {}


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

    item = {
        "title": title,
        "vault": {"id": vault_id},
        "category": category,
        "urls": [{"href": url} for url in urls or []],
        "tags": tags or [],
        "fields": [],
        "favorite": bool(favorite)
    }

    sections = {}

    if fieldset is not None:
        for field in _prepare_fields(fieldset, category):
            section = None

            if field.get("section"):
                # Squash sections with case-sensitive,
                # identical names
                section_name = field["section"].strip()

                section = sections.setdefault(
                    section_name,
                    Section(id=str(uuid4()), label=section_name)
                )

            field.update({
                "section": {"id": section.id} if section else None,
            })

            item["fields"].append(field)

    if sections:
        item["sections"] = [
            {"id": section.id, "label": section.label}
            for _id, section in sections.items()
        ]

    return item


def _prepare_fields(fields, item_category):
    """Adds any additional metadata if item_category requires it"""
    primary_username_set = False
    primary_password_set = False

    for field in fields:
        field_purpose = _get_field_purpose(field, item_category)

        if field_purpose == const.PURPOSE_USERNAME:
            if primary_username_set:
                # Primary username may only be set once per item
                raise errors.PrimaryUsernameAlreadyExists(
                    "Item type {0} may only have one (1) 'username' field".format(item_category)
                )
            primary_username_set = True

        if field_purpose == const.PURPOSE_PASSWORD:
            if primary_password_set:
                raise errors.PrimaryPasswordAlreadyExists(
                    "Item type {0} may only have one (1) 'password' field".format(item_category))
            primary_password_set = True

        field.update({
            "purpose": field_purpose
        })

        yield field

    if item_category == const.ItemType.PASSWORD and not primary_password_set:
        raise errors.PrimaryPasswordUndefined(
            "Item type {0} requires a 'concealed' field named 'password'.".format(item_category)
        )


def _get_field_purpose(field, item_category):
    """
    Assign a field purpose based on the item category and the field's type.

    PURPOSE_USERNAME and PURPOSE_PASSWORD apply to the last seen field in the item
    that matches the criteria in this function.
    :param field: Field definition
    :param item_category: ItemType The category assigned to the item for this field
    :return: string
    """

    field_label = field.get("label")
    field_type = field.get("type", "").upper()

    if not field_label:
        return const.PURPOSE_NONE

    # Only use case-sensitive match for the notes field
    if field_type == const.FieldType.STRING and field_label == const.NOTES_FIELD_LABEL:
        return const.PURPOSE_NOTES

    field_label = field_label.lower()

    if item_category == const.ItemType.LOGIN:
        if field_type == const.FieldType.STRING and field_label == "username":
            return const.PURPOSE_USERNAME
        if field_type == const.FieldType.CONCEALED and field_label == "password":
            return const.PURPOSE_PASSWORD

    if item_category == const.ItemType.PASSWORD:
        if field_type == const.FieldType.CONCEALED and field_label == "password":
            return const.PURPOSE_PASSWORD

    return const.PURPOSE_NONE
