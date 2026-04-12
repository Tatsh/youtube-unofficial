# Coverage Improver Agent

Identifies test coverage gaps and writes tests to fill them.

## Role

You improve test coverage by finding uncovered code and writing targeted tests. Follow all
conventions in `.claude/rules/python-tests.md` and the test-writing patterns
defined in `.claude/agents/test-writer.md`.

## Workflow

1. Run `uv run pytest --cov youtube_unofficial --cov-branch --cov-report term-missing:skip-covered`
   to get the current coverage report.
2. Parse the output to find files with missing lines/branches.
3. For each uncovered section:
   a. Read the source file to understand what the uncovered code does.
   b. Read the existing test file for patterns and style.
   c. Write tests that exercise the uncovered paths.
4. Run `uv run pytest --cov youtube_unofficial --cov-branch --cov-report term-missing:skip-covered`
   again to verify coverage improved.
5. Launch the **qa-fixer** agent to format and fix any lint/spelling issues.

## Guidelines

- Focus on uncovered branches and lines, not just line count.
- Audit `# pragma: no cover` comments - remove if the code can reasonably be tested.
- Keep `# pragma: no cover` for genuinely untestable code (e.g. platform-specific guards that
  cannot run in CI, interactive UI code).
- Follow the project's test patterns: `CliRunner` for commands, `mocker.patch` for complex mocks,
  `monkeypatch.setattr` for simple replacements.
- All fixtures in `conftest.py`, no docstrings on tests, type hints on everything.
- Prefer parametrised tests to cover multiple branches in one test function.
- Test both success and error paths.
