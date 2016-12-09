import os

from skitza.loaders.exceptions import UnsupportedFileType, MissingConfigFileError
from json_loader import *
from skitza import constants
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

    def load(self):
        path_to_config = None
        if not self.path:
            existent_paths = filter(lambda p: os.path.exists(p), self.path_fallback_list)
            if existent_paths:
                path_to_config = existent_paths[0]
            else:
                raise MissingConfigFileError()

        if not os.path.exists(path_to_config):
            raise MissingConfigFileError()

        for loader in self.loaders:
            if loader.is_supported_file_type(path_to_config):
                return loader.load(path_to_config)

        raise UnsupportedFileType()
