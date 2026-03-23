# QA Fixer Agent

Runs formatting and QA checks, then iteratively fixes all issues until both pass cleanly.

## Role

You ensure the project passes all formatting and QA checks. Follow all conventions in the
instruction files under `.github/instructions/`.

## Workflow

1. Run `yarn format`. Fix any issues it reports.
2. Run `yarn qa`. Parse the output for errors.
3. For each error:
   a. Read the file.
   b. For docstring violations (Ruff D1xx, DOC501, etc.), follow the rules in
   `.claude/agents/docstring-fixer.md` - only document items in `__all__`, use plain-text types
   in Parameters/Returns/Raises headers, NumPy style.
   c. For all other issues, fix following the relevant instruction file (Python, Markdown,
   JSON/YAML, TOML/INI, general).
4. Repeat from step 1 until both `yarn format` and `yarn qa` exit with code 0.

## Rules

- Never suppress or disable linter rules to make checks pass. Fix the root cause.
- Follow all project conventions when fixing issues (see `.github/instructions/`).
- Click command entry points must only have a single-line docstring (no `Parameters`/`Returns`/
  `Raises` sections). Click uses the docstring as CLI help text.
- Use `http.HTTPStatus` constants (e.g. `HTTPStatus.FORBIDDEN`) instead of bare integer status codes.
- Wrap long conditions in `if`, `elif`, `while`, and `for` statements with parentheses for line
  continuation. Do not use `\` or split the line inside `{}`, `()`, or `[]` literals that are part
  of the expression.

  Correct:

  ```python
  if (response is not None
          and response.status_code in {HTTPStatus.FORBIDDEN, HTTPStatus.TOO_MANY_REQUESTS}):
  ```

  Wrong:

  ```python
  if response is not None and response.status_code in {
          HTTPStatus.FORBIDDEN, HTTPStatus.TOO_MANY_REQUESTS
  }:
  ```

- If a fix introduces new errors, fix those too before re-running.
- If stuck in a loop (same error persists after 3 attempts), stop and alert the user.
