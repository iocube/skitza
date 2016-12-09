import json
import os
import jsonschema

from skitza.validators.exceptions import ReadError, ValidationError


def validate(content):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = open(os.path.join(base_dir, 'schema.json'), 'r')
    try:
        schema = json.load(f)
    except ValueError as error:
        raise ReadError(reason=error.message)
    finally:
        f.close()

    try:
        jsonschema.validate(content, schema)
    except jsonschema.exceptions.ValidationError as error:
        raise ValidationError(reason=error.message)

    return content
