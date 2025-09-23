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
- When importing `subprocess`, alias it: `import subprocess as sp`.
- All test function names must start with `test_`.
- Test files must be named `test_*.py`.
- Use `pytest` for testing.
- Use `@pytest.mark.parametrize` for parameterized tests.
- Use `@pytest.mark.asyncio` for asynchronous tests.
- Use `pytest.raises` for testing exceptions.
- Use `@pytest.fixture` decorator for fixtures.
- Do not create new fixtures inside test files. All fixtures must be defined in the `conftest.py`
  file.
- Ruff rules do not apply to files inside a `migrations` directory.
- Call `.encode()` without arguments if the encoding is expected to be UTF-8.
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
  name.
- By default, sort collections alphabetically.
- If a function accepts a collection of items and returns it, prefer to return a modified copy of
  the collection instead of modifying it in place.
