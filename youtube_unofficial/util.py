import re

try:
    compat_str = unicode  # Python 2
    from HTMLParser import HTMLParser as compat_HTMLParser
except NameError:
    compat_str = str
    from html.parser import HTMLParser as compat_HTMLParser

try:  # Python 2
    from HTMLParser import HTMLParseError as compat_HTMLParseError
except ImportError:  # Python <3.4
    try:
        from html.parser import HTMLParseError as compat_HTMLParseError
    except ImportError:  # Python >3.4

        # HTMLParseError has been deprecated in Python 3.3 and removed in
        # Python 3.5. Introducing dummy exception for Python >3.5 for
        # compatible and uniform cross-version exceptiong handling
        class compat_HTMLParseError(Exception):
            pass


__all__ = ['compat_str', 'try_get', 'remove_start', 'html_hidden_inputs']


class HTMLAttributeParser(compat_HTMLParser):
    """Trivial HTML parser to gather the attributes for a single element"""

    def __init__(self):
        self.attrs = {}
        compat_HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def extract_attributes(html_element):
    """Given a string for an HTML element such as
    <el
         a="foo" B="bar" c="&98;az" d=boz
         empty= noval entity="&amp;"
         sq='"' dq="'"
    >
    Decode and return a dictionary of attributes.
    {
        'a': 'foo', 'b': 'bar', c: 'baz', d: 'boz',
        'empty': '', 'noval': None, 'entity': '&',
        'sq': '"', 'dq': '\''
    }.
    NB HTMLParser is stricter in Python 2.6 & 3.2 than in later versions,
    but the cases in the unit test will work for all of 2.6, 2.7, 3.2-3.5.
    """
    parser = HTMLAttributeParser()
    try:
        parser.feed(html_element)
        parser.close()
    # Older Python may throw HTMLParseError in case of malformed HTML
    except compat_HTMLParseError:
        pass
    return parser.attrs


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
