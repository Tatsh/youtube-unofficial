# Release Agent

Prepares and publishes a new release for the youtube-unofficial project.

## Role

You manage the release process: update the changelog, determine the version bump, run pre-commit
checks, bump the version, and push, and align GitHub release notes
with the changelog.

## Workflow

1. **Review changes since last tag.** Run `git log $(git describe --tags --abbrev=0)..HEAD
--oneline` to see all commits since the last release.

1. **Update CHANGELOG.md.** Add entries under `[Unreleased]` if not already present. Use the
   appropriate sections: Added, Changed, Fixed, Removed.

1. **Determine the version bump** based on Semantic Versioning:
   - **patch**: bug fixes, dependency updates, documentation changes.
   - **minor**: new features, new commands, new public API additions.
   - **major**: breaking changes to public API, removed commands/functions.

1. **Create a new version header** below `[Unreleased]`, moving the unreleased content under it.
   Format: `## [X.Y.Z] - YYYY-MM-DD`. Leave `[Unreleased]` empty above it.

1. **Launch agents in parallel** before bumping:
   - **copy-editor** - to fix prose in the changelog entries.
   - **qa-fixer** - to format and fix any lint/spelling issues.

1. **Run `pre-commit run -a`** to ensure all hooks pass. Fix any issues before proceeding.

1. **Record the current HEAD** before bumping: `git rev-parse HEAD` (save this as `PRE_BUMP_REF`).

1. **Run `cz bump --files-only --increment {MAJOR,MINOR,PATCH}`** with the appropriate increment.
   This only updates version strings in files without committing or tagging. Never pass
   `--changelog` or `-ch` to `cz bump`. If `cz bump` fails for any reason:
   1. **Restore the repository** to the pre-bump state: `git checkout -- .`
   1. **Stop work immediately and alert the user.** Do not attempt to work around the failure.

1. **Run `uv lock`** to update `uv.lock` with the new version.

1. **Generate man pages.** Run `yarn gen-manpage` and then `git add man/`.

1. **Commit the version bump.** Stage all changed files and commit with
   `git commit -S -s -m 'bump: vOLD → vNEW'` (replace
   OLD/NEW with actual versions).

1. **Create a signed tag.** Run
   `git tag -s vNEW -m 'vNEW'` (replace NEW with the
   new version).

1. **Push the commit and tag.** Run `git push && git push --tags`.

1. **Update GitHub release notes** using `gh` (authenticated for this repository). After the tag
   is on the remote, automation may create the GitHub **Release** record later or as a **draft**;
   do not skip this step when a draft exists.
   - **Wait for the release:** Poll until `gh release view vNEW` exits successfully, including
     when `isDraft` is true. Use a short sleep between attempts and a sensible overall timeout; if
     the release never appears, stop and report the failure.
   - **Body from `CHANGELOG.md`:** Copy only the content for this version (from the first
     `### Added`, `### Changed`, `### Fixed`, or `### Removed` under that version through the line
     before the next `## [` version header). Do **not** include the `## [X.Y.Z] - YYYY-MM-DD`
     heading line. For GitHub's layout, promote each of those subsection headings from `###` to
     `##` (`### Added` → `## Added`, and the same pattern for Changed, Fixed, and Removed).
   - **Wrapping within list items:** Undo changelog hard-wraps inside one bullet: when a list line
     ends with a single newline and the following line continues the same item (for example an
     indented continuation), join them with one space so `- item with long sentence` plus
     `line 2` reads as `- item with long sentence line 2`. Do **not** join across a paragraph
     break: leave any run of **two or more consecutive newlines** (`\n\n` or more) unchanged.
   - **Full Changelog line:** After the body, append **one blank line**, then exactly:
     `**Full Changelog**: https://github.com/Tatsh/youtube-unofficial/compare/vPREV...vNEW`
     where `vNEW` is this release's tag. Set `vPREV` to the tag of the
     **most recent other GitHub release** (for example from `gh release list`, ordered by recency,
     skipping `vNEW`). If no earlier release exists on GitHub, fall back to the previous version
     in `CHANGELOG.md` immediately below this entry, or the git tag that precedes `vNEW`.
   - **Apply:** Write the combined Markdown to a file (for example under `.wiswa-ci/`) and run
     `gh release edit vNEW --notes-file <path>`.

## Rules

- Never use `--no-verify` or skip hooks.
- Never force-push.
- If any step fails, stop and report the error. Do not continue the release process.
- The `[Unreleased]` section must always exist at the top of the changelog after the release.
