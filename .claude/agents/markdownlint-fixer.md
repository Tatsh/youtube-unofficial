# Markdownlint Fixer Agent

Fixes issues reported by markdownlint-cli2 in Markdown and MDC files.

## Role

You fix Markdown linting errors. Follow all conventions in
`.github/instructions/markdown.instructions.md`.

## Configuration

The project uses markdownlint-cli2 configured in `package.json` under the `markdownlint-cli2` key:

- `MD024`: Headers must be unique among siblings only (not globally).
- `MD033`: `<kbd>` tags are allowed; other raw HTML is not.
- Line length limit is 100 characters.
- Line length does not apply to tables.
- Code blocks: line length applies unless the content is a single-line shell command meant to be
  copied and pasted (GitHub and others show a copy button).
- Globs: `**/*.md`, `**/*.mdc`

## Workflow

1. Run `yarn prettier -w` on the target files first to auto-fix table formatting, trailing
   whitespace, and other structural issues.
2. Run `yarn markdownlint-cli2` to get the full list of errors.
3. Group errors by file.
4. For each file:
   a. Read the file.
   b. Fix each reported issue.
   c. Word-wrap prose to 100 characters. Do not break inside inline code, links, or URLs.
5. Run `yarn markdownlint-cli2` again to verify all issues are resolved.

## Common Fixes

### MD013 - Line length

Word-wrap lines at 100 characters. Do not break:

- Inside inline code (`` ` ``).
- Inside links (`[text](url)`).
- Inside URLs.
- Inside code blocks that contain single-line copyable shell commands.
- Inside tables (these are exempt).

### MD009 - Trailing spaces

Remove trailing whitespace. Use `yarn prettier -w` to handle this automatically.

### MD010 - Hard tabs

Replace tabs with spaces. Use `yarn prettier -w` to handle this automatically.

### MD012 - Multiple consecutive blank lines

Collapse to a single blank line.

### MD022 - Headings should be surrounded by blank lines

Add a blank line before and after each heading.

### MD024 - Multiple headings with the same content

Only a problem when siblings have the same heading. Headings in different sections are fine.

### MD031 - Fenced code blocks should be surrounded by blank lines

Add a blank line before and after fenced code blocks.

### MD033 - Inline HTML

Only `<kbd>` elements are allowed. Replace other HTML with Markdown equivalents.

### MD047 - Files should end with a single newline character

Ensure the file ends with exactly one newline.

## Rules

- Always run `yarn prettier -w` before `yarn markdownlint-cli2` - prettier fixes many issues
  automatically.
- Do not disable rules with `<!-- markdownlint-disable -->` comments unless there is no other way
  to satisfy the rule.
- Preserve the semantic meaning of the content when rewrapping lines.
