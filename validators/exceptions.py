class BaseError(Exception):
    def __init__(self, **kwargs):
        self.reason = kwargs['reason']


class ReadError(BaseError):
    pass


class ValidationError(BaseError):
    pass
