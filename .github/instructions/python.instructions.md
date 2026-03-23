---
applyTo: '**/*.py, **/*.pyi'
---

# Python guidelines

- Follow all rules given by Ruff, with the following exceptions:
  - `ANN401`: Allow use of the `typing.Any` type.
  - `ARG001`, `ARG002`, and `ARG004`: Allow unused arguments in functions and methods, primarily in
    cases where a method is overridden or a function must be compatible with an interface.
  - `COM812`: Do not automatically assume trailing commas are wanted.
  - `CPY001`: Never add copyright notices in files.
  - `D107`: Docstrings in `__init__` methods are not required.
  - `D203`: A blank line is not required after the class declaration.
  - `D212`: Summary lines are not required to be positioned on the first physical line of the
    docstring directly after the `"""`.
  - `N818`: Exception names may exist without the `Error` suffix.
  - `S101`: `assert` statements are allowed in tests and for type narrowing.
  - `S404`: Importing `subprocess` is allowed.
  - `S603`: This rule is disabled because it conflicts with `S602`, which is enabled.
  - `TD002`: Do not add an author in `TODO` comments.
  - `TD003`: Do not add a link in `TODO` comments.
  - `TD004`: Do not add a colon in `TODO` comments.
- When creating a function or method, always write the parameters horizontally without a trailing
  comma (except when the line exceeds 100 characters). Example:

  ```python
  def my_function(param1: int, param2: str, param3: bool) -> None:
      pass
  ```

- Calling `subprocess` functions with `shell=True` is highly discouraged.
- Calling `subprocess.run()` with `check=False` is highly discouraged.
- Call `zip` with `strict=True`. Otherwise, use alternatives like `itertools.zip_longest()` or
  enforce iterable length with `itertools.islice()`.
- Variables must use `snake_case` naming style.
- Class names must use `CamelCase` naming style.
- Constants must use `UPPER_SNAKE_CASE` naming style.
- Function and method names must use `snake_case` naming style.
- Use single quotes for strings except where it would be inconvenient to do so.
- Use double quotes for docstrings.
- Always add type hints in function and method signatures, even in tests.
- Use 4 spaces for indentation.
- Use async/await for asynchronous code.
- Prefix private class members with underscore (\_).
- Prefer latest Python features and syntax (3.12+).
- Always add `from __future__ import annotations` at the top of every file.
- Always place `from` import statements before `import` statements.
- Keep imports sorted alphabetically (case-sensitive).
- Group imports into 4 sections:
  1. Future statements.
  2. Standard library imports.
  3. Third-party imports.
  4. Local application imports.
- When using `ctypes.Structure` or `ctypes.Union`, add an `if TYPE_CHECKING:` section inside the
  class with field declarations so type checkers know the attribute types:

  ```python
  class CDROMMSF0(ctypes.Structure):
      if TYPE_CHECKING:
          minute: int
          second: int
          frame: int
      _fields_: ClassVar[list[tuple[str, Any]]] = [
          ('minute', ctypes.c_ubyte),
          ('second', ctypes.c_ubyte),
          ('frame', ctypes.c_ubyte),
      ]
  ```

- When documenting constants, add `:meta hide-value:` at the end of the docstring:

  ```python
  MY_CONSTANT = 42
  """The constant value.

  :meta hide-value:
  """
  ```

- Typing helpers (TypedDicts, type aliases, `Annotated` types, helper functions) go in a
  module-level `typing.py` file.
- When importing `subprocess`, alias it: `import subprocess as sp`.
- Always use `pathlib.Path` over equivalent `os` and `os.path` functions.
- Keep local variable use to a minimum unless a variable improves clarity.
- Use the walrus operator (`:=`) when appropriate.
- Use `match` over many `if`/`elif`/`else` statements whenever possible:

  ```python
  # Before
  def handle_response(status: int, body: dict[str, str]) -> str:
      if status == 200 and 'data' in body:
          return body['data']
      elif status == 301 or status == 302:
          return body.get('location', '')
      elif status == 404:
          raise FileNotFoundError
      elif status >= 500:
          raise RuntimeError(body.get('error', 'Unknown'))
      else:
          return ''

  # After
  def handle_response(status: int, body: dict[str, str]) -> str:
      match status:
          case 200 if 'data' in body:
              return body['data']
          case 301 | 302:
              return body.get('location', '')
          case 404:
              raise FileNotFoundError
          case s if s >= 500:
              raise RuntimeError(body.get('error', 'Unknown'))
          case _:
              return ''
  ```

- All test function names must start with `test_`.
- Test files must be named `test_*.py`.
- Use `pytest` for testing.
- Use `@pytest.mark.parametrize` for parametrised tests.
- Use `@pytest.mark.asyncio` for asynchronous tests.
- Use `pytest.raises` for testing exceptions.
- Use `@pytest.fixture` decorator for fixtures.
- Do not create new fixtures inside test files. All fixtures must be defined in the `conftest.py`
  file.
- Ruff rules do not apply to files inside a `migrations` directory.
- Call `.encode()` without arguments if the encoding is expected to be UTF-8.
- All functions with parameters must have a NumPy-style docstring with a `Parameters` section. If
  the return value is not `None`, include a `Returns` section.
- Multiline docstrings must have a newline after the opening `"""` and the closing `"""` on its
  own line:

  ```python
  def process(data: str, *, verbose: bool = False) -> int:
      """
      Process the input data.

      Parameters
      ----------
      data : str
          The data to process.
      verbose : bool
          Enable verbose output.

      Returns
      -------
      int
          The number of items processed.
      """
  ```

- Follow all Numpy-style docstring conventions for functions and methods, with the following
  exceptions:
  - `ES01`: Extended summary is not required.
  - `EX01`: Examples are not required.
  - `GL08`: Variables are not required to have docstrings.
  - `RT03`: Documenting return values is not required if the return type is trivial or obvious.
  - `SA01`: See Also sections are not required.
  - Do not add `, optional` to parameters that are optional.
- If a function accepts only certain values for a parameter, use `Literal` from the `typing`
  module to specify those values.
- Use `LiteralString` from the `typing_extensions` module for string literals that are not
  expected to be formatted or interpolated.
- Always add `TypeAlias` type hint for type aliases imported from `typing_extensions`.
- Prefer to create generators instead of returning lists or other collections, unless the
  collection is small or the performance impact is negligible.
- Prefer to use tuples instead of lists for fixed-size collections or when the collection is
  immutable.
- Prefer to accept abstract base classes or interfaces as parameters instead of concrete classes.
  For example, accept `Mapping` instead of `dict`, or `Iterable` instead of `list`.
- Avoid using `Any` type in type hints, but if necessary, use it only when the type is truly unknown
  or dynamic.
- Use type variables (`T`, `U`, `K`, `V`, etc) in type hints where appropriate such as
  `Mapping[K, V]`. Example: If a function calls to accept a collection of items where all items are
  of type `T` and returns an item from that list, use the return type `T`.
- Use generic types in the function signature. Do not use `TypeVar`.
- Return values should be concrete types such as `dict[K, V]` and not generic types like
  `Mapping[K, V]`. Therefore, in the function body, type conversions may be required.
- Do not override Python built-in identifiers such as `id`. Suffix these with `_` to avoid
  conflicts (e.g. `id_`).
- Do not use the `SimpleNamespace` type and instead use dataclasses or namedtuples.
- When using namedtuples, always use `typing.NamedTuple` to declare them.
- When specifying keyword arguments to a function call, sort them alphabetically by the keyword
  name unless it would affect clarity.
- Class body ordering: attributes first (sorted alphabetically: dunder, public, private), then
  methods (sorted alphabetically: dunder, public, private). Exception: in Django models, follow
  Ruff rule DJ012 (Django Style Guide ordering) instead.
- By default, sort collections alphabetically.
- If a function accepts a collection of items and returns it, prefer to return a modified copy of
  the collection instead of modifying it in place.
- All public facing functions, methods, objects, class attributes, and classes must have docstrings.
- Never add an "Attributes" section in class docstrings. Document class attributes using docstrings:

  ```python
  class MyClass:
      """Class for doing some useful work."""

      attr1 = 42
      """The attr1 attribute."""
      attr2 = 'default'
      """The attr2 attribute."""
  ```

- Never place a newline after class attribute docstrings.
- In docstrings, for optional parameters, do not add `, optional` to the parameter
  description.
- Do not make useless string interpolations. Example: Use `var_name` instead of `f'{var_name}'`. If
  `var_name` is not a string, use `str(var_name)`.
- All modules must define `__all__` as a tuple listing all public exports.
- All private members, methods, and functions must start with `_`.
- `__init__.py` files must only contain dunder variables (`__version__`, `__all__`, etc.), imports,
  and `__all__` re-exports. No logic, classes, or function definitions.
- All code and comments must be word-wrapped at 100 characters.
- Comments that are complete sentences must end in a period.
- Never create a `Methods` section in class docstrings. Methods are documented like functions with
  their own docstring.
- If a function raises exceptions, include a `Raises` section with a description for each exception
  type.
- In docstrings, use Sphinx cross-references when referring to other types, modules, or functions:
  `:py:mod:`, `:py:func:`, `:py:class:`, `:py:meth:`. Use `~` to shorten the displayed name. This
  applies to third-party types as well (e.g. `` :py:class:`~pathlib.Path` ``).
- Use Click for CLI commands.
- Logging is set up by `bascom`. Only call `setup_logging` in entry points (commands), never in
  library code:

  ```python
  from bascom import setup_logging

  @click.command()
  @click.option('-d', '--debug', is_flag=True)
  def my_command(debug: bool = False) -> None:
      """Do something."""
      setup_logging(debug=debug, loggers={'myproject': {}})
  ```

- In library modules, define a module-level logger (not exported):
  `log = logging.getLogger(__name__)`.
- Always use `%`-style formatting in log calls, never f-strings or `.format()`.
- Log messages that are complete sentences must end in a period. Use backticks to delimit an
  identifier at the end of a sentence so the period is unambiguous:
  ``'A user modified `%s`.'``
- `click.Path` must always include `path_type=Path` to get `pathlib.Path` objects.
- Use `click.Abort` for graceful failure (exit code 1). Chain from exceptions:
  `raise click.Abort from e`.
- Use `click.exceptions.Exit(code)` to exit with a specific non-zero exit code without printing an
  "Aborted!" message (unlike `click.Abort`).
- Rename Click parameters that shadow builtins: `@click.option('--all', 'all_', ...)`.
- `click.option` help strings must end in a period.
- Always pass `check=True` to `sp.run` unless exit code handling is explicit.
- Pre-compile regex patterns as module-level constants (not inside functions).
- Prefer `@functools.cache` over `@functools.lru_cache` for unbounded caches.
- Prefer to use `indent=2, sort_keys=True` when dumping JSON for human-readable output.
- Chain exceptions with `raise ... from e` to preserve context.

## Typing

When fixing mypy errors or eliminating `Any` usage, follow these strategies in order of preference:

1. **TypedDict** for dictionary shapes - place shared ones in a `typing.py` module and add to
   `__all__`.
2. **PEP 695 generic type variables** (`def func[T](items: Sequence[T]) -> T`) - do not use
   `TypeVar` directly.
3. **ParamSpec** for decorators and callable wrappers
   (`def decorator[**P, R](fn: Callable[P, R]) -> Callable[P, R]`).
4. **Unpack** with TypedDict for `**kwargs` typing.
5. **Union types** (`str | bytes | Path`) when the set of types is known.
6. **Protocol** for structural typing when the caller only needs specific methods.

### Acceptable `Any`

Keep `Any` only when:

- The type is truly dynamic (e.g. JSON from unknown input, `plistlib.load` return).
- Third-party libraries have untyped APIs with no stubs.
- ctypes `_fields_` definitions require it.
- A `cast('Any', ...)` is needed for an untyped third-party API.

### Rules

- `# type: ignore` must always include specific error code(s), e.g. `# type: ignore[assignment]` -
  bare `# type: ignore` is never acceptable.
- `# type: ignore[...]` is only acceptable when `cast()` is not suitable and a limitation in
  Python's type system causes the error. Always add a brief comment explaining the limitation.
- In all other cases, fix the root cause instead of suppressing the error.
- Never weaken types to silence errors.
- New `TypedDict`/`Protocol`/`NamedTuple` classes need docstrings (NumPy style), and every member
  must have an individual docstring on the line immediately after its declaration:

  ```python
  class Config(TypedDict):
      """Application configuration."""

      name: str
      """Name of the application."""
      count: int
      """Number of items to process."""
  ```
