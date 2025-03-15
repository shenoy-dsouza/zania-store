from rest_framework import status
from store import error_codes
from store.error_codes import ERRORS

errors = dict(ERRORS)


class BaseException(Exception):
    http_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = error_codes.SERVER_ERROR
    errors = {}

    def __init__(self, message=None, errors=None):
        if message is None:
            message = self.message
        super().__init__(message)

        if errors:
            self.errors = errors

    def message(self):
        return str(self)

    def get_errors(self):
        return self.errors

    def get_error_code(self):
        return self.error_code

    def get_http_status_code(self):
        return self.http_status_code
