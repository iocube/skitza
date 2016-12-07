import os
import json
import click
import jinja2
import sys
import yaml
import jsonschema
import constants

from loaders.loader import Config
from loaders.exceptions import *
from validators import jsonschema_validator, validator
from validators.exceptions import *
import filters


@click.group()
def cli():
    pass


def command(config, com):
    def inner(*args, **kwargs):
        # kwargs contain arguments that were passed to the command
        kwargs['constants'] = config['constants']
        kwargs['skitza'] = constants.TEMPLATE_CONSTANTS

        for template in com['templates']:
            if 'directory' in template:
                create_directory(template['directory'], kwargs)
            else:
                write(template['source'], template['destination'], kwargs)

    return inner


def register_commands(config):
    commands = []
    for idx, com in enumerate(config['commands']):
        commands.append(command(config, com)) # commands stores `command` functions
        for arg in com['arguments']:
            commands[idx] = click.option('--{option}'.format(option=arg['name']), help=arg['help'])(
                commands[idx]
            )

        help = com.get('help', '')
        short_help = com.get('short_help', '')

        cli.add_command(
            click.command(name=com['command'], help=help, short_help=short_help)(
                commands[idx]
            )
        )


def write(source, destination, context):
    splitted = source.split('/')
    template_dir = '/'.join(splitted[0:-1])

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    jinja_env.filters.update(filters.filters)

    file_name_template = jinja_env.from_string(splitted[len(splitted)-1]).render(context)
    destination_template = jinja_env.from_string(destination).render(context)

    jinja_env.get_template(file_name_template).stream(**context).dump(destination_template)

    click.echo('{template}: {destination}'.format(
        template=file_name_template,
        destination=destination_template)
    )


def create_directory(path, options):
    rendered_path = jinja2.Template(path).render(options)

    if not os.path.exists(rendered_path):
        os.makedirs(rendered_path)


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


if __name__ == '__main__':
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
                 '\n\nUsage: skitza.py [OPTIONS]'
                 '\n\nOptions:\n  --config   Path to skitza *.json or *.yaml config file')
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

    register_commands(config)
    cli()