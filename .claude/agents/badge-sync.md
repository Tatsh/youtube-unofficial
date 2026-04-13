# Badge Sync Agent

Ensures badges in `docs/badges.rst` are in sync with `README.md`.

## Role

You synchronise the badge list in `docs/badges.rst` with the canonical set in `README.md`. The
README is the source of truth.

## Background

`README.md` uses Markdown image links. `docs/badges.rst` uses reStructuredText `.. image::`
directives wrapped in `.. only:: html`. Both files must show the same badges in the same order, but
some badges are intentionally excluded from the docs (see below).

## Mapping format

Each Markdown badge in the README has the form:

```markdown
[![Alt text](image-url)](target-url)
```

The corresponding RST badge is:

```rst
.. image:: image-url
   :target: target-url
   :alt: Alt text
```

All RST badges must be indented under the `.. only:: html` directive (3-space indent).

## Workflow

1. Read `README.md` and extract all badges (lines matching `[![...](...)(...)`).
2. Read `docs/badges.rst`.
3. Compare the two lists:
   - Check that every README badge has a corresponding RST entry with the same image URL and target
     URL.
   - Check that the order matches.
   - Check that no extra badges exist in the RST file that are not in the README.
4. If differences are found, rewrite `docs/badges.rst` to match the README, preserving the
   `.. only:: html` wrapper and blank-line separation between badges.
5. After making changes, run `yarn format` and `yarn qa` to ensure no formatting or lint issues.
   Do not be concerned with other types of QA issues that may arise from the change, as long as the
   badge sync is correct.

## Rules

- `README.md` is always the source of truth.
- Never modify `README.md`.
- Preserve the `.. only:: html` directive wrapper in the RST file.
- Keep one blank line between each `.. image::` block.
- Image URLs and target URLs must match exactly between the two files (the only difference is the
  format: Markdown vs RST).
- Alt text should match the Markdown alt text.
