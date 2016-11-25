import click
import jinja2
import json

f = open('skitza.json', 'r')
config = json.load(f)
f.close()


@click.group()
def cli():
    pass


def command(template):
    def inner(*args, **kwargs):
        kwargs['constants'] = config['constants']
        write(template['source'], template['destination'], kwargs)

        # generate child templates
        for innner_template in template['template']:
            write(innner_template['source'], innner_template['destination'], kwargs)

    return inner


def register_commands():
    commands = []
    for idx, template in enumerate(config['template']):

        commands.append(command(template))
        for arg in template['arguments']:
            commands[idx] = click.option('--{option}'.format(option=arg))(
                commands[idx]
            )

        cli.add_command(
            click.command(name=template['command'])(
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


if __name__ == '__main__':
    register_commands()
    cli()