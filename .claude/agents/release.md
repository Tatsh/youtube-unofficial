---
name: release
description: Drives the release process for the youtube-unofficial project: changelog, version bump, pre-commit checks, push, and GitHub release notes. Use when the user asks to cut a release.
---

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

1. **Sync repo state back to `.wiswa.jsonnet`.** Run the **wiswa-sync** agent so every hand
   edit to a Wiswa-managed file since the last regen is reflected in `.wiswa.jsonnet`. Any
   release-time discoveries (for example a `version_files` entry that was missing) must
   round-trip so the next regen reproduces them.

1. **Run `pre-commit run -a` outside the sandbox** to ensure all hooks pass. The hooks write
   across the worktree, which the sandbox's read-only mount blocks. Fix any issues before
   proceeding.

1. **Record the current HEAD** before bumping: `git rev-parse HEAD` (save this as `PRE_BUMP_REF`).

1. **Pre-scan `version_files` for collision risk.** Note OLD (the current
   `[tool.commitizen].version`) and NEW (the post-bump version for the selected increment).
   For each entry in `[tool.commitizen].version_files`, run
   `rg --fixed-strings --line-number 'OLD' <file>` (or `grep -nF 'OLD' <file>`). Exactly one
   match is the canonical version field cz is meant to bump. Every other match is a
   **collision candidate**: cz uses plain string substitution, so any substring `OLD` in the
   file is replaced with `NEW`, regardless of context. Save the candidate list (file, line
   number, full pre-bump line) so the matches can be reverted after the bump. The classic
   example: OLD `0.0.0` and NEW `0.0.1` rewrite a `"some-dep": "10.0.0"` line into
   `"some-dep": "10.0.1"` even though `10.0.0` is unrelated to the project version.

1. **Run `cz bump --files-only --increment {MAJOR,MINOR,PATCH}`** with the appropriate increment.
   This only updates version strings in files without committing or tagging. Never pass
   `--changelog` or `-ch` to `cz bump`. If `cz bump` fails for any reason:
   1. **Restore the repository** to the pre-bump state: `git checkout -- .`
   1. **Stop work immediately and alert the user.** Do not attempt to work around the failure.

1. **Revert accidental bump collisions.** For every collision candidate recorded in the
   pre-scan, open the same `file:line` and confirm whether cz rewrote a substring inside an
   unrelated value (for example `10.0.0` → `10.0.1`). If so, restore that line to its
   pre-bump content; leave the canonical version-field match in its post-bump state. If you
   are unsure whether a change is intended, prefer to revert and stop with a report rather
   than ship the bump with a corrupted dependency or transitive version.

1. **Verify version-bound and source-bound files.** Stop and report if any check fails:
   - **`CITATION.cff`** if present: `version` matches `NEW` and `date-released` equals today's
     date. If `cz bump` did not update either, the file is missing from
     `[tool.commitizen].version_files` - add it, rerun **wiswa-sync**, and restart the bump.
   - **Flatpak manifest** (`flatpak/**`, any `*.flatpak.{json,yaml}`) if present: every version
     reference is updated to `NEW` (cz must drive this through `version_files` - fix the
     configuration as above if it did not), and every `sources` entry pointing at this
     repository uses `tag: vNEW` with a fresh `commit:` SHA where applicable. No local `path:`
     sources, no moving branch.
   - **Snapcraft** (`snap/snapcraft.yaml` or top-level `snapcraft.yaml`) if present: every
     version reference and every part's `source-tag:` equal `NEW` / `vNEW`. `source:` points at
     the remote repository, never a local path. Same `version_files` rule for cz.

1. **Run `uv lock`** to update `uv.lock` with the new version.

1. **Generate and verify man pages.** Run `yarn gen-manpage` and then `git add man/`. Confirm
   the embedded `.TH` line shows version `NEW` and today's date; if not, stop and report.

1. **Commit the version bump outside the sandbox.** Stage all changed files and commit with
   `git commit -S -s -m 'bump: vOLD → vNEW'` (replace
   OLD/NEW with actual versions). Run outside the sandbox because the pre-commit hooks invoked
   by the commit need to write across the worktree.

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

1. **Monitor CI until the release is undrafted.** On GitHub, the release pipeline triggered
   by the tag push un-drafts the GitHub Release on success. Poll runs created **at or after
   the push** (use `gh run list --branch vNEW` and/or per-workflow filters; ignore older
   runs) on a short sleep until every post-push run reaches a terminal status and
   `gh release view vNEW --json isDraft -q .isDraft` returns `false`. Cap the loop with a
   sensible overall timeout. On all-green and undrafted, report the release URL and stop.

   If any post-push run **failed**, recover as follows:
   1. **Alert the user** with the failing run URLs and a one-line summary of the workflow
      and job that failed.
   1. **Fetch the failing logs** with `gh run view <run-id> --log-failed` (or `--log` for
      the full transcript) and read them to identify the root cause.
   1. **Delete the broken release and tag.** Run `gh release delete vNEW --yes`,
      `git push origin :refs/tags/vNEW`, and `git tag -d vNEW`.
   1. **If the release was already un-drafted before the failure surfaced**, do **not**
      reuse `vNEW` after the cleanup; a published release is part of the public history.
      Bump one more patch level so the recovery release is `vNEW+1`, leaving the failed
      tag as a recorded mistake.
   1. **Apply the fix** if the logs make the root cause clear, as a normal commit
      (separate from the original bump commit). Then restart from the version-bump step
      with the same OLD→NEW (or OLD→NEW+1 in the premature-undraft case).
   1. **If the cause is unclear**, stop and hand back to the user with the logs and the
      cleanup state.

## Rules

- Never use `--no-verify` or skip hooks.
- Never force-push.
- If any step fails, stop and report the error. Do not continue the release process.
- The `[Unreleased]` section must always exist at the top of the changelog after the release.
- Run `pre-commit run -a` and the version-bump `git commit` outside the sandbox; both need
  write access across the worktree.
- Flatpak manifests and `snapcraft.yaml` at release time always build from the about-to-be
  pushed tag, never from a local path or moving branch.
- Never hand-patch a version reference in `CITATION.cff`, a flatpak manifest, or
  `snapcraft.yaml` to compensate for a missing `[tool.commitizen].version_files` entry. Fix
  the configuration, run **wiswa-sync** so the fix reaches `.wiswa.jsonnet`, then restart the
  bump.
- `cz bump --files-only` is plain string substitution, not pattern-aware. Always pre-scan
  every `version_files` entry for OLD substrings before bumping, and revert non-canonical
  matches afterwards so unrelated literals like `10.0.0` are not corrupted into `10.0.1`.
- A release is not complete until every post-push CI run reaches a terminal status and the
  GitHub Release is un-drafted. If recovery requires deleting a release that was already
  un-drafted, bump one more patch level instead of reusing the failed tag - a published
  release is part of the public history and must not be silently replaced.
