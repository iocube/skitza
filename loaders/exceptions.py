class BaseError(Exception):
    def __init__(self, **kwargs):
        self.reason = kwargs['reason']


class ReadError(BaseError):
    pass


class ParseError(BaseError):
    pass


class UnsupportedFileType(Exception):
    pass


class MissingConfigFileError(Exception):
    pass


class ValidationError(Exception):
    pass
