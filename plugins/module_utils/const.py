# Server-generated name for the Notes field
NOTES_FIELD_LABEL = "notesPlain"


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
