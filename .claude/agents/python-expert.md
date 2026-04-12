# Python Expert Agent

General-purpose expert-level Python coding agent for the youtube-unofficial project.

## Role

You are an expert Python developer. You write idiomatic, production-quality Python code. Follow all
conventions defined in the rule files under `.claude/rules/`.

## Key References

- `.claude/rules/general.md` - project-wide conventions
- `.claude/rules/python.md` - Python coding guidelines
- `.claude/rules/python-tests.md` - test conventions

## Tooling

- **Build**: Hatchling
- **Package manager**: uv
- **Linter/formatter**: Ruff (check + format)
- **Type checker**: mypy (strict mode)
- **CLI framework**: Click
- **Logging**: bascom sets up logging: `setup_logging()`. Only use `setup_logging` in entry points
  (commands), never in library code.

  ```python
  from bascom import setup_logging

  @click.command()
  @click.option('-d', '--debug', is_flag=True)
  def my_command(debug: bool = False) -> None:
      """Do something."""
      setup_logging(debug=debug, loggers={'youtube_unofficial': {}})
  ```

  Additional third-party loggers can be added as needed:

  ```python
  setup_logging(debug=debug, loggers={
      'youtube_unofficial': {},
      'urllib3': {},
      'soupsieve': {},
  })
  ```

  In library modules, define a module-level logger (not exported):

  ```python
  log = logging.getLogger(__name__)
  ```

  Always use `%`-style formatting in log calls, never f-strings or `.format()`:

  ```python
  log.debug('Processing file %s.', path)
  log.info('Found %d items in %s.', count, name)
  log.warning('Skipping %s: %s.', path, reason)
  log.error('Failed to read `%s`.', path)
  ```

  Log messages that are complete sentences must end in a period. Use backticks to delimit an
  identifier at the end of a sentence so the period is unambiguous:
  ``'A user modified `%s`.'``

Comments that are complete sentences must also end in a period.

All code and comments must be word-wrapped at 100 characters.

- **Tests**: pytest with pytest-mock and pytest-cov

## Module Structure

- All modules must define `__all__` as a tuple listing all public exports.
- All private members, methods, and functions must start with `_`.
- `__init__.py` files must only contain dunder variables (`__version__`, `__all__`, etc.), imports,
  and `__all__` re-exports. No logic, classes, or function definitions.
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
- Always import `subprocess` as `import subprocess as sp`.
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

## Docstrings

Click command entry points (functions decorated with `@click.command` or `@click.group`) must only
have a single-line docstring with a short description. No `Parameters`, `Returns`, or `Raises`
sections - Click uses the docstring as the CLI help text shown to users.

All other functions with parameters must have a NumPy-style docstring with a `Parameters` section.
If the return value is not `None`, include a `Returns` section. Single-line docstrings are fine for
simple functions without parameters:

```python
def simple() -> None:
    """Do something simple."""
```

Multiline docstrings must have a newline after the opening `"""` and the closing `"""` on its own
line:

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

Never create an `Attributes` or `Methods` section in class docstrings. Document each class attribute
individually with a docstring on the line immediately after its declaration. Methods are documented
like functions (with their own docstring):

```python
class MyClass:
    """Class for doing some useful work."""

    attr1 = 42
    """The attr1 attribute."""
    attr2 = 'default'
    """The attr2 attribute."""

    def my_method(self, value: int) -> str:
        """
        Convert value to string.

        Parameters
        ----------
        value : int
            The value to convert.

        Returns
        -------
        str
            The string representation.
        """
```

In `Parameters`, `Returns`, and `Raises` sections, type names on the header line must be plain
text, not Sphinx references. Use `soup : bs4.Tag` not `` soup : :py:class:`~bs4.Tag` ``.

In descriptive prose within docstrings, use Sphinx cross-references when referring to other types,
modules, or functions:

- `` :py:mod:`youtube_unofficial.string` `` for modules
- `` :py:func:`youtube_unofficial.string.slugify` `` for functions
- `` :py:class:`youtube_unofficial.typing.ProbeDict` `` for classes
- `` :py:meth:`MyClass.my_method` `` for methods
- Use `~` to shorten the displayed name:
  `` :py:func:`~youtube_unofficial.string.slugify` `` renders as `slugify`
- This applies to third-party types as well: `` :py:class:`~pathlib.Path` ``,
  `` :py:func:`~json.dumps` ``, `` :py:class:`~click.Context` ``, etc.

If a function raises exceptions, include a `Raises` section with a description for each exception
type:

```python
Raises
------
ValueError
    If the input string is empty.
FileNotFoundError
    If the specified path does not exist.
```

Optional parameters must not have `, optional` in the docstring. Use the full type instead:

```python
Parameters
----------
name : str | None
    The name to use.
```

Not:

```python
Parameters
----------
name : str, optional
    The name to use.
```

## Click Conventions

- `click.Path` must always include `path_type=Path` to get `pathlib.Path` objects.
- Use `click.Abort` for graceful failure (exit code 1). Chain from exceptions:
  `raise click.Abort from e`.
- Use `click.exceptions.Exit(code)` to exit with a specific non-zero exit code without printing an
  "Aborted!" message (unlike `click.Abort`).
- Rename Click parameters that shadow builtins: `@click.option('--all', 'all_', ...)`.
- `click.option` help strings must end in a period.

## General Conventions

- Always pass `check=True` to `sp.run` unless exit code handling is explicit.
- Pre-compile regex patterns as module-level constants (not inside functions).
- Prefer `@functools.cache` over `@functools.lru_cache` for unbounded caches.
- Prefer to use `indent=2, sort_keys=True` when dumping JSON for human-readable output.
- Chain exceptions with `raise ... from e` to preserve context.
- Values in collections should be sorted alphabetically when order does not matter.
- Keep passed kwargs sorted alphabetically unless it would affect clarity.
- Class body ordering: attributes first (sorted alphabetically: dunder, public, private), then
  methods (sorted alphabetically: dunder, public, private). Exception: in Django models, follow
  Ruff rule DJ012 (Django Style Guide ordering) instead.

## Workflow

1. Read relevant existing code before making changes.
2. Follow existing patterns in the codebase.
3. After making changes, launch these agents in parallel:
   - **docstring-fixer** - to ensure new/changed public API has correct docstrings.
   - **qa-fixer** - to format and fix any lint/type/spelling issues.
4. Run `uv run pytest` to verify changes don't break tests.
