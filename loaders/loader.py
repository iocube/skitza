import os

import constants
from loaders.exceptions import UnsupportedFileType, MissingConfigFileError
from json_loader import *
from yaml_loader import *


class Config(object):
    def __init__(self, path=None):
        self.path = path
        self.path_fallback_list = [
            constants.DEFAULT_CONFIG_PATH_JSON,
            constants.DEFAULT_CONFIG_PATH_YAML
        ]
        self.loaders = [
            JSONLoader,
            YAMLLoader
        ]
        self.is_path_exists = os.path.exists(self.path)

    def load(self):
        path = None
        if not self.path:
            existent_paths = filter(lambda p: os.path.exists(p), self.path_fallback_list)
            if existent_paths:
                path = existent_paths[0]
            else:
                raise MissingConfigFileError()

        if not self.is_path_exists:
            raise MissingConfigFileError()

        for loader in self.loaders:
            if loader.is_supported_file_type(path):
                return loader.load(path)

        raise UnsupportedFileType()