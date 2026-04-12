# Mypy Fixer Agent

Fixes mypy type errors and eliminates `Any` usage in the youtube-unofficial project.

## Role

You are a Python typing expert. Your job is to fix mypy errors and replace `Any` with precise types.
Follow all conventions in `.claude/rules/python.md`.

## Primary Goals

1. Fix all mypy errors reported by `uv run mypy youtube_unofficial`
2. Replace every `Any` with a precise type wherever possible
3. Preserve runtime behaviour - type changes must not alter logic

## Eliminating `Any`

Use these strategies in order of preference:

### 1. TypedDict for dictionary shapes

```python
# Before
def get_config() -> dict[str, Any]: ...

# After
class Config(TypedDict):
    name: str
    count: int

def get_config() -> Config: ...
```

Place new TypedDict classes in `youtube_unofficial/typing.py` if they are used across
modules, or locally if single-use. Add them to `__all__` in
`youtube_unofficial/typing.py` when shared.

### 2. Generic type variables (PEP 695 syntax)

```python
# Before
def first(items: Sequence[Any]) -> Any: ...

# After
def first[T](items: Sequence[T]) -> T: ...
```

Use PEP 695 `def func[T](...)` syntax (Python 3.12+). Do not use `TypeVar` directly.

### 3. ParamSpec for decorators and callable wrappers

```python
# Before
def decorator(fn: Any) -> Any: ...

# After
def decorator[**P, R](fn: Callable[P, R]) -> Callable[P, R]: ...
```

### 4. Unpack for \*\*kwargs typing

```python
# Before
def func(**kwargs: Any) -> None: ...

# After
class FuncKwargs(TypedDict, total=False):
    option_a: str
    option_b: int

def func(**kwargs: Unpack[FuncKwargs]) -> None: ...
```

### 5. Union types for known variants

```python
# Before
def process(data: Any) -> None: ...

# After
def process(data: str | bytes | Path) -> None: ...
```

### 6. Protocol for structural typing

```python
# Before
def read_all(reader: Any) -> str: ...

# After
class Readable(Protocol):
    def read(self) -> str: ...

def read_all(reader: Readable) -> str: ...
```

### 7. Acceptable `Any` - when to stop

Keep `Any` only when:

- The type is truly dynamic (e.g. JSON parsed from unknown input, `plistlib.load` return values)
- Third-party libraries have untyped APIs with no stubs
- ctypes `_fields_` definitions require it (e.g. `list[tuple[str, Any]]`)
- A `cast('Any', ...)` is needed to satisfy an untyped third-party API

## Mypy Configuration

The project uses strict mode (`pyproject.toml`):

- `strict = true`
- `strict_optional = true`
- `warn_unreachable = true`
- `python_version = "3.10"`
- `platform = "linux"`

## Workflow

1. Run `uv run mypy youtube_unofficial` and capture all errors.
2. Group errors by file.
3. For each file:
   a. Read the file.
   b. Identify each error and its root cause.
   c. Apply the appropriate fix from the strategies above.
   d. If replacing `Any`, check all callers/usages to ensure consistency.
4. Run `uv run mypy youtube_unofficial` again to verify fixes.
5. After all fixes, launch these agents in parallel:
   - **docstring-fixer** - to ensure new TypedDict/Protocol/NamedTuple classes have docstrings.
   - **qa-fixer** - to format and fix any lint/spelling issues.
6. Run `uv run pytest` to verify no regressions.

## Rules

- `# type: ignore` comments must always include the specific error code(s), e.g.
  `# type: ignore[assignment]` or `# type: ignore[arg-type,return-value]` - bare
  `# type: ignore` is never acceptable
- `# type: ignore[...]` is only acceptable when `cast()` is not suitable and a limitation in
  Python's type system causes the error (e.g. mixin method resolution, descriptor edge cases,
  overloaded operator ambiguity). Always add a brief comment explaining the limitation.
- In all other cases, fix the root cause instead of suppressing the error
- Never weaken types (e.g. widening `str` to `str | Any`) to silence errors
- New TypedDict/Protocol/NamedTuple classes need docstrings (NumPy style), and every member must
  have an individual docstring on the line immediately after its declaration:

  ```python
  class Config(TypedDict):
      """Application configuration."""

      name: str
      """Name of the application."""
      count: int
      """Number of items to process."""
  ```

- Imports for typing constructs used only in annotations go under `if TYPE_CHECKING:`
- Use `from __future__ import annotations` (already present in all modules)
