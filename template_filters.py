# Read: http://jinja.pocoo.org/docs/dev/templates/#builtin-filters

filters = {
    'first_upper': lambda s: s[0].upper() + s[1:],
    'first_lower': lambda s: s[0].lower() + s[1:]
}