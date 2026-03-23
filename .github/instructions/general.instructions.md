# Copilot Instructions

youtube-unofficial is a command line tool to access parts of your YouTube account that are not
available through the normal YouTube API. It allows a user to manage subscriptions, playlists, and
liked videos directly from the command line.

## General

- Do not explain project structure or conventions in comments or docstrings.
- Use 2 spaces for indentation except in Python.
- Files must end with a single newline character.
- Keep lines shorter than 100 characters.
- Line endings must be Unix-style (LF).
- Use UTF-8 encoding for all files.
- Use spaces instead of tabs for indentation.
- Use British spelling in comments and docstrings.
- Use American spelling for all identifiers and string literals, except in docstrings.
- Never mention the spelling or other project conventions in comments or docstrings.
- Use full sentences in comments and docstrings.
- Use the Oxford comma in lists.
- Use single quotes for strings, except where double quotes are required (e.g., JSON).
- Full words should be preferred over abbreviations, except for well-known acronyms. Some words may
  be abbreviated:
  - `config` for configuration.
- Prefer to use immutable data structures over mutable ones.
- Run `yarn format` after any changes to format all files. Must exit with code 0.
- Run `yarn qa` after any changes to type-check and run QA utilities. Must exit with code 0. Both
  commands must pass before committing.
- Use `yarn` to invoke Node-based tools (Prettier, markdownlint-cli2, cspell).
- Use `uv run` to invoke Python tools (pytest, mypy, Ruff).
- Spell-check uses cspell with British English (`en-GB`). Exception: code identifiers must use
  American English (`ColorCode` not `ColourCode`).
- Add new words to `.vscode/dictionary.txt` in lowercase and keep the file sorted. Prefer to commit
  dictionary changes separately with the message `dictionary: update`.
