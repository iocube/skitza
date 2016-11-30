import os
import json
import click
import jinja2


f = open('skitza.json', 'r')
config = json.load(f)
f.close()

SKITZA_CONSTANTS = {
    'cwd': os.getcwd()
}

@click.group()
def cli():
    pass


def command(com):
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


def register_commands():
    commands = []
    for idx, com in enumerate(config['commands']):
        commands.append(command(com)) # commands stores `command` functions
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

if __name__ == '__main__':
    register_commands()
    cli()