---
applyTo: 'tests/**/*.py'
---

# Python test guidelines

- Always add type hints including the return value.
  - The type of the `mocker` fixture is `MockerFixture`. It is imported as
    `from pytest_mock import MockerFixture`.
- All test function names must start with `test_`.
- Test files must be named `test_*.py`.
- Use `@pytest.mark.parametrize` for parametrised tests.
- Use `@pytest.mark.asyncio` for asynchronous tests.
- Use `pytest.raises` for testing exceptions.
- Use `@pytest.fixture` for fixtures.
- Do not create new fixtures inside test files.
- All fixtures must be defined in the `tests/conftest.py` file.
- Do not add docstrings to test functions or methods.
- Mock external dependencies and IO operations in tests.
- If a parameter must exist in a callback, use `_` as the identifier if it is not a keyword
  argument.
- Use the `runner` fixture (type `CliRunner`) from `conftest.py` for testing Click commands.
- Test Click commands by checking `result.exit_code` and `result.output`.
- Use `mocker.patch` for complex mock setups; `monkeypatch.setattr` for simple attribute
  replacement.
