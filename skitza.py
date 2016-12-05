import os
import json
import click
import jinja2
import sys
import yaml
import jsonschema
import constants


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


def convert_str_to_json(data):
    try:
        jsonfied = json.loads(data)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=config_path,
            reason=error.message
        ))

    validate(jsonfied)

    return jsonfied


def convert_str_to_yaml(data):
    try:
        yamlfied = yaml.load(data)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=config_path,
            reason=error.message
        ))

    validate(yamlfied)

    return yamlfied

def load_config_from_json(path):
    try:
        f = open(path, 'r')
    except IOError as error:
        if path == constants.DEFAULT_CONFIG_PATH_JSON:
            sys.exit('Unable to find local skitza.json and `--config` was not specified, aborting.\n\nUsage: skitza.py '
                     '[OPTIONS]\n\nOptions:\n  --config   Path to skitza *.json or *.yaml config file')
        else:
            sys.exit('ERROR: Could not read `{path}` config file. Reason: {reason}'.format(
                path=error.filename,
                reason=error.strerror
            ))
    try:
        content_as_json = json.load(f)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=path,
            reason=error.message
        ))
    finally:
        f.close()

    validate(content_as_json)

    return content_as_json


def is_yaml(path):
    return path.endswith('.yaml')


def is_json(path):
    return path.endswith('.json')


def load_config_from_yaml(path):
    try:
        f = open(path, 'r')
    except IOError as error:
        if path == constants.DEFAULT_CONFIG_PATH_YAML:
            sys.exit('Unable to find local skitza.json and `--config` was not specified, aborting.\n\nUsage: skitza.py '
                     '[OPTIONS]\n\nOptions:\n  --config   Path to skitza *.json or *.yaml config file')
        else:
            sys.exit('ERROR: Could not read `{path}` config file. Reason: {reason}'.format(
                path=error.filename,
                reason=error.strerror
            ))

    try:
        content_as_yaml = yaml.load(f)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=path,
            reason=error.message
        ))
    finally:
        f.close()

    validate(content_as_yaml)

    return content_as_yaml


def load_schema():
    f = open('schema.json', 'r')
    try:
        schema = json.load(f)
    except ValueError as error:
        sys.exit('ERROR: Could not parse schema.json. Reason: {reason}'.format(
            reason=error.message
        ))
    finally:
        f.close()

    return schema

def validate(content):
    return jsonschema.validate(content, load_schema())

if __name__ == '__main__':
    config_opt = get_option_from_argv(sys.argv, '--config=')

    config_path = None
    if config_opt:
        # remove config path from sys.argv so click module won't process it.
        sys.argv.remove(config_opt)
        (option_name, option_value) = get_value_from_option(config_opt)
        config_path = option_value

    if config_path:
        if is_json(config_path):
            config_json = load_config_from_json(config_path)
        elif is_yaml(config_path):
            config_json = load_config_from_yaml(config_path)
    else:
        if os.path.exists(constants.DEFAULT_CONFIG_PATH_JSON):
            config_json = load_config_from_json(constants.DEFAULT_CONFIG_PATH_JSON)
        elif os.path.exists(constants.DEFAULT_CONFIG_PATH_YAML):
            config_json = load_config_from_yaml(constants.DEFAULT_CONFIG_PATH_YAML)
        else:
            sys.exit('Unable to find local skitza.json and `--config` was not specified, aborting.\n\nUsage: skitza.py '
                     '[OPTIONS]\n\nOptions:\n  --config   Path to skitza *.json or *.yaml config file')

    register_commands(config_json)
    cli()