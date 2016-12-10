import sys
import click

from skitza import command, __version__
from skitza.loaders.exceptions import *
from skitza.loaders.loader import Config
from skitza.validators import jsonschema_validator, validator
from skitza.validators.exceptions import *


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


def register_cli_commands(config):
    registered_commands = []

    # iterate over each command
    for idx, cmd in enumerate(config['commands']):
        registered_commands.append(command.attach_behavior_to_command(config, cmd))

        # iterate over each argument that this command can accept
        for arg in cmd['arguments']:
            registered_commands[idx] = click.option('--{option}'.format(option=arg['name']), help=arg['help'])(
                registered_commands[idx]
            )

        description = cmd.get('help', '')
        short_help = cmd.get('short_help', '')

        # after all arguments are attached to the command, add it.
        cli.add_command(
            click.command(name=cmd['command'], help=description, short_help=short_help)(
                registered_commands[idx]
            )
        )


def get_option_from_argv(argv, name):
    for idx, arg in enumerate(argv):
        if arg.startswith(name):
            return argv[idx]


def get_value_from_option(opt):
    splitted = opt.split('=')

    if len(splitted) < 2:
        return splitted[0], None
    else:
        return splitted[0], splitted[1]


def main():
    config_opt = get_option_from_argv(sys.argv, '--config=')
    config_path = None

    if config_opt:
        # remove config path from sys.argv so click module won't process it.
        sys.argv.remove(config_opt)
        (option_name, option_value) = get_value_from_option(config_opt)
        config_path = option_value

    try:
        config = Config(config_path).load()
    except ReadError as error:
        sys.exit('ERROR: Could not read config file. Reason: {reason}'.format(reason=error.reason))
    except ParseError as error:
        sys.exit('ERROR: Could not parse config file. Reason: {reason}'.format(reason=error.reason))
    except MissingConfigFileError:
        sys.exit('ERROR: Unable to find config file, local skitza.json or skitza.yaml were not found too, aborting.'
                 '\n\nVersion: {version}\nUsage: skitza.py [OPTIONS]'
                 '\n\nOptions:\n  --config   Path to skitza *.json or *.yaml config file'.format(version=__version__))
    except UnsupportedFileType:
        sys.exit('ERROR: Unsupported file type')

    try:
        validator.validate(config, jsonschema_validator)
    except ReadError as error:
        sys.exit('ERROR: Could not parse schema.json. Reason: {reason}'.format(
            reason=error.reason
        ))
    except ValidationError as error:
        sys.exit('ERROR: Failed to validate config file. Reason: {reason}'.format(
            reason=error.reason
        ))

    register_cli_commands(config)

    try:
        cli()
    except command.TemplateIsMissingError as error:
        sys.exit('ERROR: {reason}'.format(reason=error.reason))
