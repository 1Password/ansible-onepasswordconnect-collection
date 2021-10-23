from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class Error(Exception):
    DEFAULT_MSG = "Error while interacting with 1Password"

    def __init__(self, message=None):
        self.message = message or self.DEFAULT_MSG
        super(Error, self).__init__(message)


class MissingVaultID(Error):
    DEFAULT_MSG = "A Vault ID is required to use this module."


class PrimaryUsernameAlreadyExists(Error):
    DEFAULT_MSG = "Only one primary username may exist for an item."


class PrimaryPasswordAlreadyExists(Error):
    DEFAULT_MSG = "Only one primary password may exist for an item."


class PrimaryPasswordUndefined(Error):
    DEFAULT_MSG = "This item category requires at least one concealed field."


class FieldNotUnique(Error):
    DEFAULT_MSG = "Provided field label is not unique. Please provide a section or a more specific field label."


class APIError(Error):
    DEFAULT_MSG = "Error while communicating with Secrets Server"
    STATUS_CODE = 400

    def __init__(self, status_code=None, message=None):
        self.status_code = status_code or self.STATUS_CODE
        super(APIError, self).__init__(message)


class NotFoundError(APIError):
    DEFAULT_MSG = "Resource not found"
    STATUS_CODE = 404


class BadRequestError(APIError):
    DEFAULT_MSG = "Invalid request body or parameters"
    STATUS_CODE = 400


class ServerError(APIError):
    DEFAULT_MSG = "Secret Server encountered an error. Please try again"
    STATUS_CODE = 500


class AccessDeniedError(APIError):
    DEFAULT_MSG = "Token invalid or access to Vault not granted by token."
    STATUS_CODE = 403
