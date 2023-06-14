from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
from ansible_collections.onepassword.connect.plugins.module_utils import const

"""
Defines common option specs for modules
"""


def common_options():
    """Collects & returns options shared by all module implementations
    :return: dict
    """
    # Just API params for now
    return API_CONFIG, SERVICE_ACCOUNT_CONFIG


def op_item():
    """Helper that compiles item spec and all common module specs
    :return dict
    """
    item_spec = dict(
        vault_id=dict(
            required=True,
            fallback=(env_fallback, ['OP_VAULT_ID'])
        ),
        name=dict(
            type="str",
            aliases=["title"]
        ),
        uuid=dict(
            type="str",
        ),
        category=dict(
            type="str",
            default=const.ItemType.API_CREDENTIAL.lower(),
            choices=const.ItemType.choices(),
        ),
        urls=dict(
            type="list",
            elements="str"
        ),
        favorite=dict(
            type="bool",
            default=False
        ),
        fields=dict(
            type="list",
            elements="dict",
            options=FIELD
        ),
        tags=TAGS,
        state=STATE
    )
    item_spec.update(common_options())
    return item_spec


def op_item_info():
    """Helper that compiles item info spec and all common module specs
    :return dict
    """
    item_spec = dict(
        item=dict(
            type="str",
            required=True
        ),
        flatten_fields_by_label=dict(
            type="bool",
            default=True
        ),
        # Direct users to field_info module instead
        field=dict(
            type="str",
            removed_from_collection="onepassword.connect",
            removed_in_version="3.0.0",
        ),
        vault=dict(
            type="str"
        )
    )
    for option in common_options():
        item_spec.update(option)
    return item_spec


def op_field_info():
    """
    Helper that compiles the field_info argspec with common module specs
    :return: dict
    """
    field_spec = dict(
        item=dict(
            type="str",
            required=True
        ),
        field=dict(
            type="str",
            required=True
        ),
        vault=dict(
            type="str",
            required=True,
        ),
        section=dict(
            type="str"
        )
    )
    field_spec.update(common_options())
    return field_spec


# Configuration for the "Secure Password/Value Generator"
GENERATOR_RECIPE_OPTIONS = dict(
    length=dict(
        type="int",
        default=32
    ),
    include_digits=dict(
        type="bool",
        default=True,
    ),
    include_letters=dict(
        type="bool",
        default=True,
    ),
    include_symbols=dict(
        type="bool",
        default=True,
    ),
)

# API config options for all modules
API_CONFIG = dict(
    hostname=dict(
        fallback=(env_fallback, ['OP_CONNECT_HOST'])
    ),
    token=dict(
        fallback=(env_fallback, ['OP_CONNECT_TOKEN']),
        no_log=True
    ),
)

# SERVICE_ACCOUNT_CONFIG config options for all modules
SERVICE_ACCOUNT_CONFIG = dict(
    service_account_token=dict(
        fallback=(env_fallback, ['OP_SERVICE_ACCOUNT_TOKEN']),
        no_log=True
    )
)

# User-configurable attributes for one or more fields on an Item
FIELD = dict(
    label=dict(type="str", required=True),
    value=dict(type="str", no_log=True),
    section=dict(type="str"),
    field_type=dict(
        type="str",
        default="string",
        choices=const.FieldType.choices(),
        aliases=["type"]
    ),
    generate_value=dict(
        type="str",
        default=const.GENERATE_NEVER,
        choices=list(const.GENERATE_VALUE_CHOICES)
    ),
    generator_recipe=dict(
        type="dict",
        options=GENERATOR_RECIPE_OPTIONS
    )
)
#############################################
# Common attributes
#############################################
# Resource Create/Update/Delete statuses
STATE = dict(
    type="str",
    default="present",
    choices=["present", "absent"]
)

# 1Password item tags
TAGS = dict(
    type="list",
    elements="str"
)
