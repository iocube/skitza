import os
import json
import click
import jinja2
import sys


SKITZA_CONSTANTS = {
    'cwd': os.getcwd(),
    'env': os.environ
}

SKITZA_DEFAULT_CONFIG = 'skitza.json'


@click.group()
def cli():
    pass


def command(config, com):
    def inner(*args, **kwargs):
        # kwargs contain arguments that were passed to the command
        kwargs['constants'] = config['constants']
        kwargs['skitza'] = SKITZA_CONSTANTS

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
            commands[idx] = click.option('--{option}'.format(option=arg))(
                commands[idx]
            )

        cli.add_command(
            click.command(name=com['command'])(
                commands[idx]
            )
        )


def write(source, destination, context):
    splitted = source.split('/')
    template_dir = '/'.join(splitted[0:-1])
    file_name_template = jinja2.Template(splitted[len(splitted)-1]).render(context)
    destination_template = jinja2.Template(destination).render(context)

    click.echo('{template}: {destination}'.format(
        template=file_name_template,
        destination=destination_template)
    )

    jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir)
    ).get_template(file_name_template).stream(**context).dump(destination_template)


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

    if config_opt:
        # remove config path from sys.argv so click module won't process it.
        sys.argv.remove(config_opt)
        (option_name, option_value) = get_value_from_option(config_opt)
        config_path = option_value
    else:
        # fall back to default config name that may reside in current directory
        config_path = SKITZA_DEFAULT_CONFIG

    try:
        f = open(config_path, 'r')
    except IOError as error:
        if config_path == SKITZA_DEFAULT_CONFIG:
            sys.exit('Unable to find local skitza.json and `--config` was not specified, aborting.\n\nUsage: skitza.py '
                     '[OPTIONS]\n\nOptions:\n  --config   Path to skitza *.json config file')
        else:
            sys.exit('ERROR: Could not read `{path}` config file. Reason: {reason}'.format(
                path=error.filename,
                reason=error.strerror
            ))
    try:
        config_json = json.load(f)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=config_path,
            reason=error.message
        ))
    finally:
        f.close()

    register_commands(config_json)
    cli()