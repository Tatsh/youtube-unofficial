# Commit

Create high-quality Git commits for all pending changes.

## Gathering context

Run these in parallel:

1. `git diff` - unstaged changes.
2. `git diff --cached` - staged changes.
3. `git status` - untracked files and overall state.
4. `git log --no-merges --format='%s%n%b---' -20 | grep -v '^bump:' | grep -iv dependabot` -
   recent commit message style examples.

## Running agents

After gathering context but before committing, determine which agents to run based on the changed
files. Launch each agent sequentially using the Agent tool with subagent_type `general-purpose`,
telling it to follow the corresponding `.claude/agents/<name>.md` file. Scope each agent to only the
changed files, not the entire project.

You must skip any agents that are not relevant to the changed files (e.g. if no Click command files
changed, skip the click-auditor).

### When Python code is being committed

If any changed files are under `youtube_unofficial/` or `tests/`, run the following
agents **in order**:

1. **python-moderniser** - upgrade to modern Python features.
1. **click-auditor** - validate Click command consistency. **Only run if files under
   `youtube_unofficial/commands/` changed.**
1. **docstring-fixer** - fix missing or incomplete docstrings.
1. **copy-editor** - fix prose in comments, docstrings, and strings.
1. **test-writer** - generate/update tests for new/changed code. **Skip if the only changes are in
   `tests/`.**
1. **qa-fixer** - format and fix lint/spelling issues.

### When user-facing changes are being committed

- **changelog** - update `CHANGELOG.md` only for **user-facing** changes (behaviour, CLI, public
  API, security, or meaningful dependency constraints that affect installs). After it completes,
  check if `CHANGELOG.md` was modified (`git diff CHANGELOG.md`). If it was, stage it with the
  relevant commit. Follow `.claude/agents/changelog.md`, including its skip list.

  Files under `youtube_unofficial/`, `tests/`, or version changes in `pyproject.toml` are **candidates**
  for the changelog agent only when they **change what users see or
  how the software behaves**. Editing those paths is not sufficient on its own.

  **Skip the changelog agent** for workflows, CI config, `.claude/`, documentation-only churn,
  cruft or generator clean-up (for example replacing template placeholders such as `unknown` in
  repository URLs, badges, packaging metadata, or `CODEOWNERS` with the real project identity),
  internal refactors with no behaviour change, and other non-user-facing work.

## Analysing changes

Group changed files by component. Determine if one commit or multiple
logical commits are needed.

### Incidental files

The following files do not count when determining the component prefix, unless they are the **only**
file in a commit:

- `CHANGELOG.md`
- `.vscode/dictionary.txt`

For example, if a commit contains `youtube_unofficial/commands/main.py`,
`tests/test_main_command.py`, and `CHANGELOG.md`, the component is determined by
the source files only. `CHANGELOG.md` is simply staged alongside them.

If `CHANGELOG.md` is the only file being committed, use the `changelog:` prefix. If
`.vscode/dictionary.txt` is the only file, use `dictionary:` prefix.

### When to split into multiple commits

- Changes span unrelated components.
- A refactor and a bug fix in the same file should be separate commits.
- New tests for existing code should be separate from the code changes they test only if the code
  changes are themselves separate.
- Dictionary updates (`.vscode/dictionary.txt`) should be committed first with message
  `dictionary: update`.

### Cruft updates

When all changes are from re-running Wiswa (the project generator) and
no hand-written code changed, this is a **cruft update**. Indicators:

- Only Wiswa-managed files changed (workflows,
  `package.json`, `pyproject.toml`, `.pre-commit-config.yaml`, `.claude/agents/`, `.claude/rules/`,
  `CITATION.cff`, `.vscode/dictionary.txt`, `uv.lock`,
  `.wiswa.jsonnet`, etc.).
- No files under the primary module or `tests/` changed.

Commit everything in a single commit with the subject `cruft: update`. Include a body summarising
what changed (e.g. new/updated workflows, updated agent files, dependency version bumps, new managed
files). Do not run any agents. Do not split into multiple commits. Do not update the changelog.

### When a single commit is fine

- All changes serve the same purpose within a closely related set of files.
- A bug fix and its test.

## Commit message format

```text
component.name: short description

Optional longer description explaining the why, not the what. Wrap at 72
characters.

Signed-off-by: Author Name <email>
Closes: #123
```

### Subject line rules

- Format: `component.name: short description`. Component name must be lowercase and must skip the
  first period if present (`vscode` not `.vscode`, `README.md` -> `readme` not `README`), and must
  omit the period with extension.
- Lowercase after the colon (unless a proper noun).
- No period at the end.
- Maximum 72 characters.
- Use imperative mood: 'add', 'fix', 'update', 'remove', not 'added', 'fixes', 'updated'.

### Component prefix rules

For Python files, strip the `youtube_unofficial/` prefix and replace `/` with `.` (like module imports).

- Python file `youtube_unofficial/media.py` → `media:`.
- Multiple files under `youtube_unofficial/commands/` → `commands:`.
- Single command file `youtube_unofficial/commands/admin.py` → `commands.admin:`.
- Workflow file `.github/workflows/qa.yml` → `workflows/qa:`.
- Multiple workflows → `workflows/*:`.
- Agent files `.claude/agents/*.md` → `.claude:` or specific agent name.
- Instruction files across all 3 locations → `project:` (since they span Copilot/Cursor/Claude).
- Test files `tests/test_media.py` → `tests/test_media:` (or `tests:` for multiple).
- Dictionary `.vscode/dictionary.txt` → `dictionary:` (only when committed alone).
- Top-level config (`pyproject.toml`, `package.json`) → `project:`.
- If changes span many unrelated areas → `project:`.
- CHANGELOG.md → `changelog:` (only when committed alone).
- CONTRIBUTING.md → `contributing:`.

### Trailers

- `Closes: #N` - when a commit closes an issue. If it is another project, use the full URI.
- `Fixes: #N` - when a commit fixes a bug reported in an issue. If it is another project, use the
  full URI.
- `Related: #N` - when a commit is related to an issue but does not fully close or fix it. If it is
  another project, use the full URI.
- `Reviewed-by:` - if applicable.
- `Co-authored-by:` - if applicable.
- `Reported-by:`: - if applicable. Could get this information from a bug report that led to the fix
  if the issue ID/URL is known.
- `Signed-off-by:` - always included on every commit. This will be added with `-s`.

## Making commits

Run commands separately. Do not chain commands with `&&` or `;`. Do not use scripts.

1. Stage files for each logical commit using `git add` with specific file paths.
2. If `CHANGELOG.md` was updated by the changelog agent, stage it with the relevant commit.
3. Create the directory if it does not exist: `mkdir -p .wiswa-ci`. Skip if it already exists.
4. Create a unique temp file with `mktemp .wiswa-ci/message-XXXXXXXX`. Write the commit message
   there using the **Write** tool (not Bash `echo` or `cat`)
5. Commit with `git commit -S -s -F <tempfile>` without using the
   sandbox.
6. If a pre-commit hook fails, fix the issue, re-stage (use appropriate agent if there is one), and
   try to commit again.
7. After all commits, run `git status` to verify clean state.

Temp commit message files under `.wiswa-ci/` do not need to be deleted after a successful commit; you
may leave them in place.

## Rules

- Never use `--no-verify` or `--no-gpg-sign`.
- Amend the previous commit when the new change is logically part of it (e.g. same file, same
  topic, fixing something just committed). Create a new commit when the change is distinct.
- Never push unless explicitly asked.
- Always use `-S` for GPG signing and `-s` for sign-off.
- If there are no changes, do nothing.
- Stage specific files, never use `git add -A` or `git add .`.
