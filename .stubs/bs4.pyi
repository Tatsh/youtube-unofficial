from typing import Any, Iterable, List, Mapping, Optional, TextIO, Union


class PageElement:
    text: str


class ResultSet(List[PageElement]):
    def __init__(self,
                 source: Any,
                 result: Iterable[PageElement] = ...) -> None:
        ...


class BeautifulSoup:
    def __init__(self, content: Union[str, TextIO], parser: str) -> None:
        ...

    def select(self,
               selector: str,
               namespace: Optional[Mapping[str, str]] = ...,
               limit: Optional[int] = ...,
               **kwargs: Any) -> ResultSet:
        ...
