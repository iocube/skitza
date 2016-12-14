import os
import jinja2

from skitza import constants, template_filters


class TemplateIsMissingError(Exception):
    def __init__(self, **kwargs):
        self.reason = kwargs['reason']


def attach_behavior_to_command(config, command):
    def behavior(*args, **kwargs):
        # kwargs contain arguments that were passed to the command
        kwargs['constants'] = config['constants']
        kwargs['skitza'] = constants.TEMPLATE_CONSTANTS

        for template in command['templates']:
            if 'directory' in template:
                make_directory(template['directory'], kwargs)
            else:
                render_template_to_destination(template['source'], template['destination'], kwargs)

    return behavior


def render_template_to_destination(source_path, destination_path, context):
    jinja_env = jinja2.Environment()
    jinja_env.filters.update(template_filters.filters)

    source_path = jinja_env.from_string(source_path).render(context)
    source_template_location = extract_template_directory_from_path(source_path)
    source_file_name = extract_file_name_from_path(source_path)

    jinja_env.loader = jinja2.FileSystemLoader(source_template_location)

    destination_path = jinja_env.from_string(destination_path).render(context)

    if os.path.exists(destination_path):
        print 'File already exists: {destination}, skipping.'.format(destination=destination_path)
        return

    try:
        jinja_env.get_template(source_file_name).stream(**context).dump(destination_path)
    except jinja2.exceptions.TemplateNotFound:
        raise TemplateIsMissingError(
            reason='Could not find following template: \'{template_name}\' from \'{template_directory}\''.format(
                template_name=source_file_name,
                template_directory=source_template_location)
            )

    print '{source} -> \n\t{destination}'.format(
        source=source_template_location + '/' + source_file_name,
        destination=destination_path
    )


def make_directory(path, context):
    jinja_env = jinja2.Environment()
    jinja_env.filters.update(template_filters.filters)

    path = jinja_env.from_string(path).render(context)

    if not os.path.exists(path):
        os.makedirs(path)
        print '{directory}'.format(directory=path)


def extract_template_directory_from_path(path):
    directories = path.split('/')
    return '/'.join(directories[0:-1])


def extract_file_name_from_path(path):
    return path.split('/')[-1]
