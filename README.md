# Skitza
Creating new module / package / component / whatever you call it in your project -- takes time and its error prone,
usually, when you want to do this you'll have three options:
- creating all the files and directories on your own, writing each time same module declaration code over and over again
- copy-pasting an existing module structure and then deleting everything except for the declaration
and then changing file names / variable names etc.
- using a scaffolding tool to automate this process

skitza falls in the third category, it is a scaffolding tool and it is not tied to a particular framework,
you decide on the name, destination and content of the scaffold.

You should create configuration file (see example in `examples/angular` directory) that describes what CLI commands
are available, where the templates are located and what will be generated as a result.
skitza depends on this, because the CLI is actually generated on the fly from your configuration.

By default, skitza looks for `skitza.json` / `skitza.yaml` files in current directory, however, you can specify an
arbitrary configuration file using the `--config` argument:
```bash
$ skitza --config='/path/to/config.json'
```

## Installation
```bash
$ pip install git+https://github.com/iocube/skitza.git
```

install from specific branch:
```bash
$ pip install git+https://github.com/iocube/skitza.git@branch_name
```

## Configuration
### Constants
Property: `constants`
Define constants that will be available in your templates.
```json
{
    "constants": {
        "constName": "constValue"
    }
}
```

Then, use it in your templates as:
```html
{{constants.constName}}
```

### Command
Property: `commands`
Commands are declared inside `commands` array, each command is an object.

```json
{
  "command": "controller",
  "help": "Generate new controller",
  "short_help": "new controller",
  "arguments": [
    {"name": "name", "help": "controller name"}
  ],
  "templates": [
    {
        "destination": "{{skitza.cwd}}/{{name|first_lower}}"
    },
    {
        "source": "{{skitza.cwd}}/controller.js.jinja",
        "destination": "{{skitza.cwd}}/{{name|first_upper}}.controller.js"
    }
  ]
}
```

This command declaration will allow you to run `controller` command with `name` argument:

`$ skitza controller --name MyCtrlName`

What will happen?
- new directory under the name `myCtrlName` will be created
- `MyCtrlName.controller.js` from `controller.js.jinja` template will be processed and saved in newly created directory

### Filters
Since skitza uses [jinja2](http://jinja.pocoo.org/) to process your templates, take a [look at the docs](http://jinja.pocoo.org/docs/dev/templates/#builtin-filters) for available filters.
In addition, skitza includes following filters:
- `first_upper` - make first letter uppercase
- `first_lower` - make first letter lowercase

### Built-in variables
Inside your template you have access to the following variables:
- `skitza.cwd` - current working directory
- `skitza.env.<ENV_VARIABLE>` - environment variable