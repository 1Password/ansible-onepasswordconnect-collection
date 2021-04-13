from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


# Server-generated name for the Notes field
NOTES_FIELD_LABEL = "notesPlain"

# 1Password Connect Ansible Collection Version
# Auto-updated during release process
COLLECTION_VERSION = "1.0.1"


class FieldType:
    STRING = "STRING"
    EMAIL = "EMAIL"
    CONCEALED = "CONCEALED"
    URL = "URL"
    TOTP = "TOTP"
    DATE = "DATE"
    MONTH_YEAR = "MONTH_YEAR"

    @classmethod
    def choices(cls):
        return [v for k, v in vars(cls).items() if k.isupper() and not k.startswith("_")]


class ItemType:

    # Item Types
    LOGIN = "LOGIN"
    PASSWORD = "PASSWORD"
    SERVER = "SERVER"
    DATABASE = "DATABASE"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    SECURE_NOTE = "SECURE_NOTE"
    WIRELESS_ROUTER = "WIRELESS_ROUTER"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    EMAIL_ACCOUNT = "EMAIL_ACCOUNT"

    @classmethod
    def choices(cls):
        return [v for k, v in vars(cls).items() if k.isupper() and not k.startswith("_")]
