import json
import jsonschema

from validators.exceptions import ReadError, ValidationError


def validate(content):
    f = open('schema.json', 'r')
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
