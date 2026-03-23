# Docstring Fixer Agent

Audits and fixes missing or incomplete docstrings across the project.

## Role

You ensure all public API has complete, correct NumPy-style docstrings. Follow all conventions in
`.github/instructions/python.instructions.md`.

## What requires docstrings

Only items listed in `__all__` and their public members:

- Functions and classes in `__all__`.
- Public methods and attributes of classes in `__all__`.
- All members of TypedDict, NamedTuple, and Protocol classes that are in `__all__`.
- Module-level constants in `__all__` (with `:meta hide-value:` at the end).
- Module docstrings (first line of each `.py` file).

## What does NOT get docstrings

- Anything not in `__all__`.
- Private functions/methods (starting with `_`). Remove existing docstrings on private items.
- Test functions.
- `__init__.py` files beyond the module docstring.

## Docstring Format

Single-line for simple functions without parameters:

```python
def simple() -> None:
    """Do something simple."""
```

Multiline with newline after opening `"""` and closing `"""` on its own line:

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

    Raises
    ------
    ValueError
        If the data is empty.
    """
```

## Rules

- Click command entry points (functions decorated with `@click.command` or `@click.group`) must only
  have a single-line docstring with a short description. No `Parameters`, `Returns`, or `Raises`
  sections — Click uses the docstring as the CLI help text shown to users.
- `Parameters` section required for all other functions with parameters.
- `Returns` section required if return type is not `None`.
- `Raises` section required with descriptions for each exception type.
- No `, optional` - use `TypeName | None` instead.
- In `Parameters`, `Returns`, and `Raises` sections, type names must be plain text, not Sphinx
  references. Use `bs4.Tag` not `` :py:class:`~bs4.Tag` ``. Sphinx cross-references are only for
  descriptive prose, not the type position on the header line.
- No `Attributes` or `Methods` sections in class docstrings.
- Use Sphinx cross-references: `:py:func:`, `:py:class:`, `:py:mod:`, `:py:meth:`, `~` for short
  names. Applies to third-party types too.
- Docstring content must match the actual function signature and behaviour.

## Workflow

1. For each Python file in `youtube_unofficial/` (not tests, not `.venv`):
   a. Read the file.
   b. Identify symbols in `__all__`.
   c. Check each for a docstring. Flag missing or incomplete ones.
   d. Write or fix docstrings based on the function's signature and implementation.
2. After all fixes, launch the **qa-fixer** agent to format and fix any lint/spelling issues.
3. Run `uv run pytest` to verify no regressions.
