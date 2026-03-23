# Agents and Instruction Files

## Agents (Claude Code)

| Agent                                                        | Purpose                                                    |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| [python-expert](.claude/agents/python-expert.md)             | General expert-level Python coding (includes mypy/typing)  |
| [mypy-fixer](.claude/agents/mypy-fixer.md)                   | Fix mypy errors and eliminate `Any`                        |
| [python-moderniser](.claude/agents/python-moderniser.md)     | Upgrade code to modern Python features                     |
| [docstring-fixer](.claude/agents/docstring-fixer.md)         | Audit and fix missing/incomplete docstrings                |
| [test-writer](.claude/agents/test-writer.md)                 | Generate tests following project patterns                  |
| [coverage-improver](.claude/agents/coverage-improver.md)     | Identify coverage gaps and write tests                     |
| [click-auditor](.claude/agents/click-auditor.md)             | Validate Click command consistency                         |
| [markdownlint-fixer](.claude/agents/markdownlint-fixer.md)   | Fix markdownlint-cli2 issues                               |
| [qa-fixer](.claude/agents/qa-fixer.md)                       | Run `yarn format` and `yarn qa` until clean                |
| [workflow-shellcheck](.claude/agents/workflow-shellcheck.md) | ShellCheck embedded Bash in workflow YAML                  |
| [copy-editor](.claude/agents/copy-editor.md)                 | Fix prose style, grammar, and spelling in comments/strings |
| [badge-sync](.claude/agents/badge-sync.md)                   | Sync `docs/badges.rst` with `README.md`                    |
| [changelog](.claude/agents/changelog.md)                     | Update CHANGELOG.md with entries since last release        |
| [regen](.claude/agents/regen.md)                             | Run Wiswa, post-process, verify, and commit                |
| [release](.claude/agents/release.md)                         | Changelog, version bump, push                              |
| [wiswa-sync](.claude/agents/wiswa-sync.md)                   | Reflect managed file changes back to `.wiswa.jsonnet`      |

## Instruction Files

Rules are maintained in parallel across three tool locations. When adding or modifying rules, update
all three.

### Copilot (`.github/instructions/`)

| File                                                              | Scope                                 |
| ----------------------------------------------------------------- | ------------------------------------- |
| [general](.github/instructions/general.instructions.md)           | Project-wide conventions              |
| [python](.github/instructions/python.instructions.md)             | Python coding (`**/*.py`, `**/*.pyi`) |
| [python-tests](.github/instructions/python-tests.instructions.md) | Test conventions (`tests/**/*.py`)    |
| [json-yaml](.github/instructions/json-yaml.instructions.md)       | JSON and YAML files                   |
| [toml-ini](.github/instructions/toml-ini.instructions.md)         | TOML and INI files                    |
| [markdown](.github/instructions/markdown.instructions.md)         | Markdown files                        |

### Cursor (`.cursor/rules/`)

| File                                           | Scope                                 |
| ---------------------------------------------- | ------------------------------------- |
| [python](.cursor/rules/python.mdc)             | Python coding (`**/*.py`, `**/*.pyi`) |
| [python-tests](.cursor/rules/python-tests.mdc) | Test conventions (`tests/**/*.py`)    |
| [json-yaml](.cursor/rules/json-yaml.mdc)       | JSON and YAML files                   |
| [toml-ini](.cursor/rules/toml-ini.mdc)         | TOML and INI files                    |
| [markdown](.cursor/rules/markdown.mdc)         | Markdown files                        |
