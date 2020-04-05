from typing import Any, Sequence, Tuple

from typing_extensions import TypedDict

__all__ = ('HasStringCode', )


class HasStringCode(TypedDict):
    code: str
