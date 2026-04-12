# Agents and AI guidance

All agent definitions, skills, and project rules live under **`.claude/`**. Use that tree whether you
use Claude Code, Cursor, GitHub Copilot, or another assistant: open or reference the files directly,
and use each product's own mechanics for attaching repo context where needed.

- **Hard prerequisite before any repository edit:** Read [.claude/rules/general.md](.claude/rules/general.md)
  in full (including _Before editing repository files_), then every other relevant
  `.claude/rules/*.md` for the paths you will change, and any applicable `.claude/agents/*.md` or
  `.claude/skills/*/SKILL.md` (for example when the task follows CI, regen, or another named
  workflow, or the user names an agent or skill). Do this **before** creating, modifying, or deleting
  tracked files.
- If the user is only adding instructions for the assistant, **do not edit the repository** unless
  they ask for a concrete change.

## Rules (`.claude/rules/`)

| File                                          | Scope                                 |
| --------------------------------------------- | ------------------------------------- |
| [general](.claude/rules/general.md)           | Project-wide conventions              |
| [python](.claude/rules/python.md)             | Python coding (`**/*.py`, `**/*.pyi`) |
| [python-tests](.claude/rules/python-tests.md) | Test conventions (`tests/**/*.py`)    |
| [json-yaml](.claude/rules/json-yaml.md)       | JSON and YAML files                   |
| [toml-ini](.claude/rules/toml-ini.md)         | TOML and INI files                    |
| [markdown](.claude/rules/markdown.md)         | Markdown files                        |

## Skills (`.claude/skills/`)

Skills are folders with a `SKILL.md` file (for example [ci](.claude/skills/ci/SKILL.md) when
present).

## Agents (`.claude/agents/`)

| Agent                                                        | Purpose                                                     |
| ------------------------------------------------------------ | ----------------------------------------------------------- |
| [click-auditor](.claude/agents/click-auditor.md)             | Validate Click command consistency.                         |
| [coverage-improver](.claude/agents/coverage-improver.md)     | Identify coverage gaps and write tests.                     |
| [docstring-fixer](.claude/agents/docstring-fixer.md)         | Audit and fix missing/incomplete docstrings.                |
| [mypy-fixer](.claude/agents/mypy-fixer.md)                   | Fix mypy errors and eliminate `Any`.                        |
| [python-expert](.claude/agents/python-expert.md)             | General expert-level Python coding (includes mypy/typing).  |
| [python-moderniser](.claude/agents/python-moderniser.md)     | Upgrade code to modern Python features.                     |
| [test-writer](.claude/agents/test-writer.md)                 | Generate tests following project patterns.                  |
| [markdownlint-fixer](.claude/agents/markdownlint-fixer.md)   | Fix markdownlint-cli2 issues.                               |
| [qa-fixer](.claude/agents/qa-fixer.md)                       | Run `yarn format` and `yarn qa` until clean.                |
| [workflow-shellcheck](.claude/agents/workflow-shellcheck.md) | ShellCheck embedded Bash in workflow YAML.                  |
| [badge-sync](.claude/agents/badge-sync.md)                   | Sync `docs/badges.rst` with `README.md`.                    |
| [changelog](.claude/agents/changelog.md)                     | Update CHANGELOG.md with entries since last release.        |
| [copy-editor](.claude/agents/copy-editor.md)                 | Fix prose style, grammar, and spelling in comments/strings. |
| [regen](.claude/agents/regen.md)                             | Run Wiswa, post-process, verify, and commit.                |
| [release](.claude/agents/release.md)                         | Changelog, version bump, push.                              |
| [wiswa-sync](.claude/agents/wiswa-sync.md)                   | Reflect managed file changes back to `.wiswa.jsonnet`.      |
