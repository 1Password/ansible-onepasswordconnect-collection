from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment:

    DOCUMENTATION = r'''
options:
    state:
        type: str
        default: present
        choices:
            - present
            - absent
        description:
            - I(present) will try to find the item using its vault ID and provided C(name) or C(UUID).
              If the item with a matching name or UUID is not found, the item is created.
            - To change the C(name) of an item, a C(uuid) MUST be provided. See C(name) for additional details.
            - I(absent) will delete the item if it exists. No change are made if the item is not found.
    '''
