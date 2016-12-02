import os
import json
import click
import jinja2
import sys
import urllib2


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
    file_name_template = jinja2.Template(splitted[len(splitted)-1]).render(context)
    destination_template = jinja2.Template(destination).render(context)

    if is_url(source):
        content = download_file(source)
        jinja2.Template(content).stream(**context).dump(destination_template)
    else:
        jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir)
        ).get_template(file_name_template).stream(**context).dump(destination_template)

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


def download_file(url):
    try:
        request = urllib2.urlopen(url)
    except urllib2.URLError as error:
        sys.exit('ERROR: Failed to download `{url}`\nReason: {reason}'.format(url=url, reason=error.reason))

    return request.read()


def convert_str_to_json(data):
    try:
        jsonfied = json.loads(data)
    except ValueError as error:
        sys.exit('ERROR: Could not parse `{path}` config file. Reason: {reason}'.format(
            path=config_path,
            reason=error.message
        ))

    return jsonfied


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')


def load_config_from_path(path):
    try:
        f = open(path, 'r')
    except IOError as error:
        if path == SKITZA_DEFAULT_CONFIG:
            sys.exit('Unable to find local skitza.json and `--config` was not specified, aborting.\n\nUsage: skitza.py '
                     '[OPTIONS]\n\nOptions:\n  --config   Path or URL to skitza *.json config file')
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

    return content_as_json


def load_config_from_url(url):
    content = download_file(url)
    return convert_str_to_json(content)


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

    if is_url(config_path):
        config_json = load_config_from_url(config_path)
    else:
        config_json = load_config_from_path(config_path)

    register_commands(config_json)
    cli()