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
    return API_CONFIG


def op_item():
    """Helper that compiles item spec and all common module specs
    :return dict
    """
    item_spec = dict(
        name=dict(
            type="str",
            aliases=["title"]
        ),
        uuid=dict(
            type="str",
        ),
        category=dict(
            type="str",
            default="password",
            choices=list(map(str.lower, const.ItemType.choices()))
        ),
        urls=dict(
            type="list",
            elements="str"
        ),
        favorite=dict(
            type="bool"
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
        field=dict(
            type="str"
        ),
        vault=dict(
            type="str"
        )
    )
    item_spec.update(common_options())
    return item_spec


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
    vault_id=dict(
        fallback=(env_fallback, ['OP_VAULT_ID'])
    ),
    hostname=dict(
        fallback=(env_fallback, ['OP_CONNECT_HOST'])
    ),
    token=dict(
        fallback=(env_fallback, ['OP_CONNECT_TOKEN']),
        no_log=True
    ),
)

# User-configurable attributes for one or more fields on an Item
FIELD = dict(
    label=dict(type="str", required=True),
    value=dict(type="str", no_log=True),
    overwrite=dict(type="bool", default=True),
    section=dict(type="str"),
    field_type=dict(
        type="str",
        default="string",
        choices=list(map(str.lower, const.FieldType.choices()))
    ),
    generate_value=dict(type="bool", default=False),
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
    default="created",
    choices=["created", "upserted", "absent"]
)

# 1Password item tags
TAGS = dict(
    type="list",
    elements="str"
)

# Common config for a password option.
# Always allow the end user to delegate password creation to
# the generator.
password_opts = dict(
    value=dict(type="str", no_log=True),
    generate=dict(type="bool", default=False)
)
