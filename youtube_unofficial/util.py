__all__ = ['compat_str', 'try_get', 'remove_start', 'html_hidden_inputs']

try:
    compat_str = unicode  # Python 2
except NameError:
    compat_str = str


def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v


def remove_start(s, start):
    return s[len(start):] if s is not None and s.startswith(start) else s


def html_hidden_inputs(html):
    html_ = re.sub(r'<!--(?:(?!<!--).)*-->', '', html)
    hidden_inputs = dict()
    for input in re.findall(r'(?i)(<input[^>]+>)', html_):
        attrs = extract_attributes(input)
        if not input:
            continue
        if attrs.get('type') not in ('hidden', 'submit'):
            continue
        name = attrs.get('name') or attrs.get('id')
        value = attrs.get('value')
        if name and value is not None:
            hidden_inputs[name] = value
    return hidden_inputs
