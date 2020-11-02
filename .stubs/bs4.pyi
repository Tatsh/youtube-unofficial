from typing import Any, Iterable, List, Mapping, Optional


class PageElement:
    text: str


class ResultSet(List[PageElement]):
    def __init__(self,
                 source: Any,
                 result: Iterable[PageElement] = ...) -> None:
        ...


class BeautifulSoup:
    def select(self,
               selector: str,
               namespace: Optional[Mapping[str, str]] = ...,
               limit: Optional[int] = ...,
               **kwargs: Any) -> ResultSet:
        ...
