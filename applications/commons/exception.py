class APIWarningException(Exception):
    def __init__(self, message='', error='', http_status=200):
        self.error = error
        self.http_status = http_status
        super(APIWarningException, self).__init__(message)


class APIBreakException(Exception):
    def __init__(self, message='', error="", http_status=200):
        self.error = error
        self.http_status = http_status
        super(APIBreakException, self).__init__(message)


class ValidationError(Exception):
    def __init__(self, message=''):
        self.message = message
        super(ValidationError, self).__init__(message)

    def __str__(self):
        return self.message
