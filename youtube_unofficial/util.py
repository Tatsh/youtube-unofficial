from html.parser import HTMLParser
from typing import (Any, Callable, Dict, Mapping, Optional, Sequence, Type,
                    Union)
import re

from typing_extensions import overload

from .typing.history import DescriptionSnippetDict

__all__ = (
    'extract_attributes',
    'extract_keys',
    'get_text_runs',
    'html_hidden_inputs',
    'path',
    'remove_start',
    'try_get',
)


class HTMLAttributeParser(HTMLParser):  # pylint: disable=abstract-method
    """Trivial HTML parser to gather the attributes for a single element"""
    def __init__(self) -> None:
        self.attrs: Dict[Any, Any] = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag: Any, attrs: Any) -> None:
        self.attrs = dict(attrs)


def extract_attributes(html_element: str) -> Mapping[str, str]:
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
    parser.feed(html_element)
    parser.close()
    return parser.attrs


def try_get(src: Any,
            getter: Union[Sequence[Callable[..., Any]], Callable[..., Any]],
            expected_type: Type[Any] = None) -> Any:
    if not isinstance(getter, (list, tuple)):
        getter = [getter]  # type: ignore[list-item]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v


@overload
def remove_start(s: str, start: str) -> str:
    pass


@overload
def remove_start(s: None, start: str) -> None:
    pass


def remove_start(s: Optional[str], start: str) -> Optional[str]:
    return s[len(start):] if s is not None and s.startswith(start) else s


def html_hidden_inputs(html: str) -> Dict[str, str]:
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


def extract_keys(keys: Sequence[Any], obj: Mapping[Any,
                                                   Any]) -> Mapping[Any, Any]:
    new = {}
    for key in keys:
        new[key] = obj[key]
    return new


def path(s: str, obj: Any) -> Any:
    for prop in s.split('.'):
        if isinstance(obj, list):
            try:
                int_prop = int(prop)
            except TypeError:
                raise TypeError('Property for a list must be an integer')
            obj = obj[int_prop]
        else:
            obj = obj[prop]
    return obj


def get_text_runs(desc: DescriptionSnippetDict) -> str:
    return ''.join(x['text']
                   for x in desc['runs']).strip().replace('\n', ' - ')
