---
applyTo: 'tests/**/*.py'
---

# Python test guidelines

- Always add type hints including the return value.
  - The type of the `mocker` fixture is `MockerFixture`. It is imported as
    `from pytest_mock import MockerFixture`.
- All test function names must start with `test_`.
- Test files must be named `test_*.py`.
- Use `@pytest.mark.parametrize` for parameterized tests.
- Use `@pytest.mark.asyncio` for asynchronous tests.
- Use `pytest.raises` for testing exceptions.
- Use `@pytest.fixture` for fixtures.
- Do not create new fixtures inside test files.
- All fixtures must be defined in the `tests/conftest.py` file.
- Do not add docstrings to test functions or methods.
- Mock external dependencies and IO operations in tests.
- If a parameter must exist in a callback, use `_` as the identifier if it is not a keyword
  argument.
