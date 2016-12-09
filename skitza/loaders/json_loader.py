import json

from skitza.loaders.exceptions import *


class JSONLoader(object):
    @staticmethod
    def load(path):
        content_as_json = {}

        try:
            f = open(path, 'r')
        except IOError as error:
            raise ReadError(reason=error.strerror)

        try:
            content_as_json = json.load(f)
        except ValueError as error:
            raise ParseError(reason=error.message)
        finally:
            f.close()

        return content_as_json

    @staticmethod
    def is_supported_file_type(path):
        if path:
            return path.endswith('.json')
        else:
            return False
