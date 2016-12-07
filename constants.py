import os


DEFAULT_CONFIG_PATH_JSON = 'skitza.json'
DEFAULT_CONFIG_PATH_YAML = 'skitza.yaml'
DEFAULT_CONFIG_NAME = 'skitza'
SUPPORTED_FILE_TYPES = ['.json', '.yaml']
TEMPLATE_CONSTANTS = {
    'cwd': os.getcwd(),
    'env': os.environ
}
