# Regen Agent

Regenerates the project by running Wiswa and post-processing steps, then commits if safe.

## Role

You re-run the Wiswa project generator to update all managed files, apply post-processing fixes,
and verify nothing is broken before committing.

## Prerequisites

- Wiswa must be installed and available as `wiswa` on the PATH.
- `.wiswa.jsonnet` must exist in the project root.

## Workflow

1. Run the wiswa-sync agent skill to ensure `.wiswa.jsonnet` is up to date with the latest schema
   and settings.

1. **Record pre-existing `tests/test_main.py`.** Check if `tests/test_main.py` exists before
   running Wiswa. If it does not exist, remember this: if Wiswa creates it, it must be removed
   after.

1. **Run Wiswa.** User-level `defaults.jsonnet` is merged when `uses_user_defaults` is `true` in
   `.wiswa.jsonnet` (see Wiswa's built-in defaults for the fallback). When that is enabled, the file
   must exist in the Wiswa user configuration directory.

   Prefer `yarn regen`; it is the usual way to invoke Wiswa in Python projects.

   ```shell
   yarn regen
   ```

   For debug logging, run `wiswa` directly:

   ```shell
   wiswa -d
   ```

1. **Lock dependencies.** If `uv.lock` exists, run `uv lock`. If `poetry.lock` exists, run
   `poetry lock`.

1. **Update the dictionary.** Run `yarn dict:update`.

1. **Post-process `docs/conf.py`.** If `docs/conf.py` exists, remove any `'hoverxref.extension',`
   entry from it (this extension is no longer used).

1. **Format.** Run `yarn format`.

1. **Clean up unwanted files.** If `tests/test_main.py` did not exist before the Wiswa run but
   exists now, delete it (Wiswa creates it for `want_main` projects but multi-entry-point projects
   do not want it).

1. **Install Node dependencies.** Run `yarn`.

1. **Review changes.** Run `git diff --stat` and `git diff` to inspect what changed. Check for
   issues that could break the build:
   - Python syntax errors in generated workflow scripts.
   - Missing or malformed YAML in workflow files.
   - Removed dependencies that are still imported in source code.
   - Changed entry points that do not match actual code.
   - Large sections of changes made to any file.

   If any issues are found, **stop and alert the user** with a description of the problem. Do not
   commit broken changes.

1. **Commit.** If everything looks safe, run the `/ci` skill to commit the changes (this will be a
   cruft update).

## Rules

- Never modify source code under `youtube_unofficial/` or `tests/`. This agent only updates
  managed/generated files.
- If Wiswa fails, stop and report the error.
- If any post-processing step fails, stop and report the error.
- Always verify changes before committing. Err on the side of caution.
