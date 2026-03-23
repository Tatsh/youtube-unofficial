# Youtube-unofficial Memory

See @README.md for an overview of this project, and view @AGENTS.md for the agents.

## Avoiding Permission Prompts

Bash commands containing `$()` subshells trigger interactive permission prompts. Avoid these:

- **Git commits**: use `mktemp /tmp/commit-msg-XXXXXXXX` to create a unique temp file, write the
  message there with the **Write** tool, then run `git commit -S -s -F <tempfile>` via Bash.
  Multiple Claude instances may run concurrently, so never use a fixed `/tmp/commit-msg` path.
  Never use `-m "$(cat <<'EOF' ...)"` or `cat > /tmp/commit-msg` in Bash (both trigger permission
  prompts).
- **Command substitution**: prefer chaining with `&&` and temp files over `$()` inline.
- **Backticks**: same issue as `$()` — avoid `` `command` `` in Bash tool calls.
- **Pipes into commands** are fine (`echo foo | git commit --stdin` etc.).
