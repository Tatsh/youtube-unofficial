# Markdown guidelines

- `MD033`: `<kbd>` tags are allowed. Other raw HTML is not.
- `MD024`: Headers do not have to be unique if they are in different sections.
- Line length limit is 100 characters. Does not apply to tables.
- Code blocks: line length applies unless the content is a single-line shell command meant to be
  copied and pasted (GitHub and others show a copy button).
- Word-wrap prose at 100 characters. Do not break inside inline code, links, or URLs.
- Run `yarn prettier --write` before `yarn markdownlint-cli2` - prettier fixes tables, trailing
  whitespace, and other structural issues automatically.
- Do not disable rules with `<!-- markdownlint-disable -->` comments unless there is no other way
  to satisfy the rule.
- Spell-check with `yarn cspell`.
- **GitHub Pages (Jekyll):** Jekyll runs **Liquid** on site Markdown before the Markdown renderer.
  In any file the build includes (for example root `CHANGELOG.md`), do not put Liquid or Jinja tag
  delimiters in literals—an opening brace followed by percent or by a second brace starts a tag;
  reword or use a Jekyll **raw** block if those characters must appear verbatim.
- CHANGELOG follows Keep a Changelog format with reverse-chronological versions and sections: Added,
  Changed, Fixed, Removed.
