# How to contribute to youtube-unofficial

Thank you for your interest in contributing to youtube-unofficial! Please follow these guidelines to
help maintain code quality and consistency.

## General Guidelines

- Follow the coding standards and rules described below for each file type.
- Ensure all code passes linting and tests before submitting a pull request.
- Write clear commit messages and document your changes in the changelog if relevant.
- Contributors are listed in `package.json` and `pyproject.toml`.
- Update relevant fields in `.wiswa.jsonnet` such as authors, dependencies, etc.
- All contributed code must have a license compatible with the project's license (MIT).
- Add missing words to `.vscode/dictionary.txt` as necessary (sorted and lower-cased).

## Development Environment

- Use [Poetry](https://python-poetry.org/) to manage Python dependencies:
  - Install dependencies: `poetry install`
  - Add a dependency: `poetry add <package>`
  - Add a dev dependency: `poetry add --group dev <package>`
  - Add a test dependency: `poetry add --group tests <package>`
  - Add a docs dependency (rarely needed): `poetry add --group docs <package>`
- Use [Yarn](https://yarnpkg.com/) to install Node.js based dependencies:
  - Install Node.js dependencies: `yarn`
- Install [pre-commit](https://pre-commit.com/) and make sure it is enabled by running
  `pre-commit install` in the repository checkout.

## Quality Assurance & Scripts

The following scripts are available via `yarn` (see `package.json`):

- `yarn qa`: Run all QA checks (type checking, linting, spelling, formatting).
- `yarn test`: Run the test suite.
- `yarn test:cov`: Run tests with coverage report.
- `yarn ruff` / `yarn ruff:fix`: Run Ruff linter (and auto-fix).
- `yarn mypy`: Run Mypy type checker.
- `yarn check-formatting`: Check code formatting (Python, Markdown, etc).
- `yarn format`: Auto-format code (Python, Markdown, etc).
- `yarn check-spelling`: Run spell checker.
- `yarn gen-docs`: Build HTML documentation.
- `yarn gen-manpage`: Build man page documentation. If you update documentation, please run this and
  commit the updated manpage file.

The above all need to pass for any code changes to be accepted.

## Python Code Guidelines

- Follow Ruff linting rules, with specific exceptions (see the [Python instructions]).
- Always use type hints in function and method signatures, including tests.
- Use 4 spaces for indentation.
- Use `snake_case` for variables and functions, `CamelCase` for classes, and `UPPER_SNAKE_CASE` for
  constants.
- Use single quotes for strings and double quotes for docstrings only.
- Add `from __future__ import annotations` at the top of every file (this will be done by Ruff in
  VS Code if you have the extension installed).
- Keep imports sorted and grouped: future, standard library, third-party, local (also done by Ruff).
- Prefer latest Python features (3.10+).
- For subprocess, avoid `shell=True` and `check=False`.
- Alias subprocess as `import subprocess as sp`.
- Add public facing API elements to `__all__`. Prefer not to use underscore-prefix except in 'private'
  method names. Do not create class attributes that invoke name mangling.
- See [Python instructions] for full details.

## Python Tests Guidelines

- Use `pytest` for testing.
- All test functions must start with `test_` and test files as `test_*.py`.
- Always add type hints, including return values.
- Use fixtures from `tests/conftest.py` only.
- Use `@pytest.mark.parametrize` for parameterized tests and `@pytest.mark.asyncio` for async tests.
- Do not add docstrings to test functions.
- Mock external dependencies and I/O operations.
- Strive to keep the coverage level the same or higher.
- Use `# pragma: no cover` when appropriate.
- See [Python tests instructions] for more details.

## Markdown Guidelines

- `<kbd>` tags are allowed.
- Headers do not have to be unique if in different sections.
- Line length rules do not apply to code blocks.
- See [Markdown instructions] for more.

## JSON, YAML, TOML, INI Guidelines

- JSON and YAML files should generally be recursively sorted by key.
- In TOML/INI, `=` must be surrounded by a single space on both sides.
- See [JSON/YAML guidelines] and [TOML/INI guidelines] for more details.

## Submitting Changes

Do not submit PRs solely for dependency bumps. Dependency bumps are either handled by running Wiswa
locally or allowing Dependabot to do them.

1. Fork the repository and create your branch from `master`.
2. Ensure your code follows the above guidelines.
3. Run all tests (`yarn test`) and QA scripts (`yarn qa`). Be certain pre-commit runs on your
   commits.
4. Submit a pull request with a clear description of your changes.

[Markdown instructions]: .github/instructions/markdown.instructions.md
[Python instructions]: .github/instructions/python.instructions.md
[Python tests instructions]: .github/instructions/python-tests.instructions.md
[JSON/YAML guidelines]: .github/instructions/json-yaml.instructions.md
[TOML/INI guidelines]: .github/instructions/toml-ini.instructions.md
