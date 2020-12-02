from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment:

    DOCUMENTATION = r'''
options:
    state:
        type: str
        default: created
        choices: 
            - created
            - upserted
            - absent
        description:
            - Creates a new Item every time Ansible runs the task. Does not check for duplicates.
            - Performs replacement if matching Item is found, otherwise creates new Item if Item matching "name" value is not found.
            - Deletes Item if exists. Skips task if matching Item not found.
    '''
