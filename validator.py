import json
import jsonschema


CONFIG_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "required": [
    "commands"
  ],
  "properties": {
    "constants": {"type": "object"},
    "commands": {
      "type": "array",
      "items": {"$ref": "#/definitions/command"},
      "minItems": 1
    }
  },
  "definitions": {
    "command": {
      "type": "object",
      "properties": {
        "command": {"type": "string"},
        "help": {"type": "string"},
        "short_help": {"type": "string"},
        "arguments": {"type": "array", "items": {"$ref": "#/definitions/argument"}},
        "templates": {"type": "array",
            "items": {
                "anyOf": [
                  {"$ref": "#/definitions/template"},
                  {"$ref": "#/definitions/directory"}
                ]
          }
        },
      },
      "required": ["templates"]
    },
    "argument": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "help": {"type": "string"}
      },
      "required": ["name"]
    },
    "template": {
      "type": "object",
      "properties": {
        "source": {"type": "string"},
        "destination": {"type": "string"}
      },
      "required": ["source", "destination"]
    },
    "directory": {
      "type": "object",
      "properties": {
        "directory": {"type": "string"}
      },
      "required": ["directory"]
    }
  }
}


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


schema = load_schema()

f = open('skitza.json', 'r')
content = json.load(f)
f.close()

print 'Content: ', content
print 'Schema: ', schema

try:
    jsonschema.validate(content, schema)
except jsonschema.exceptions.ValidationError as error:
    import pdb; pdb.set_trace()
    print error