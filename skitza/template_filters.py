# Read: http://jinja.pocoo.org/docs/dev/api/#custom-filters


def first_upper(s):
    if s:
        return s[0].upper() + s[1:]


def first_lower(s):
    if s:
        return s[0].lower() + s[1:]


filters = {
    'first_upper': first_upper,
    'first_lower': first_lower
}