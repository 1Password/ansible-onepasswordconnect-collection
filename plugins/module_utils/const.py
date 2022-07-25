from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Server-generated name for the Notes field
NOTES_FIELD_LABEL = "notesPlain"

# 1Password Connect Ansible Collection Version
# Auto-updated during release process
COLLECTION_VERSION = "2.2.1"

GENERATE_NEVER = "never"
GENERATE_ALWAYS = "always"
GENERATE_ON_CREATE = "on_create"

GENERATE_VALUE_CHOICES = (
    GENERATE_NEVER,
    GENERATE_ALWAYS,
    GENERATE_ON_CREATE,
)

# Field purposes when using certain item categories
PURPOSE_PASSWORD = "PASSWORD"
PURPOSE_USERNAME = "USERNAME"
PURPOSE_NOTES = "NOTES"
PURPOSE_NONE = ""


class FieldType:
    STRING = "STRING"
    EMAIL = "EMAIL"
    CONCEALED = "CONCEALED"
    URL = "URL"
    OTP = "OTP"
    DATE = "DATE"
    MONTH_YEAR = "MONTH_YEAR"

    @classmethod
    def choices(cls):
        return [
            v.lower()
            for k, v in vars(cls).items()
            if k.isupper() and not k.startswith("_")
        ]


class ItemType:
    LOGIN = "LOGIN"
    PASSWORD = "PASSWORD"
    SERVER = "SERVER"
    DATABASE = "DATABASE"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    SECURE_NOTE = "SECURE_NOTE"
    WIRELESS_ROUTER = "WIRELESS_ROUTER"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    EMAIL_ACCOUNT = "EMAIL_ACCOUNT"
    API_CREDENTIAL = "API_CREDENTIAL"
    CREDIT_CARD = "CREDIT_CARD"
    MEMBERSHIP = "MEMBERSHIP"
    PASSPORT = "PASSPORT"
    OUTDOOR_LICENSE = "OUTDOOR_LICENSE"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    IDENTITY = "IDENTITY"
    REWARD_PROGRAM = "REWARD_PROGRAM"
    SOCIAL_SECURITY_NUMBER = "SOCIAL_SECURITY_NUMBER"

    @classmethod
    def choices(cls):
        return [
            v.lower()
            for k, v in vars(cls).items()
            if k.isupper() and not k.startswith("_")
        ]
