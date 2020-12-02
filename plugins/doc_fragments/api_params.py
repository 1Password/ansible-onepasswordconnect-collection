from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment:

    DOCUMENTATION = r'''
options:
    vault_id:
        type: str
        description:
            - ID of the 1Password vault that will be accessed.
    hostname:
        type: str
        description:
            - URL of 1Password Connect.
    token:
        type: str
        no_log: true
        description:
            - The token to authenticate 1Password Connect calls.
    '''
