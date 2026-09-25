# Sigrid CI run (maintainability, open-source, security)

## Preflight checks

Verify these in order before running. If any check fails, stop and ask the user.

1. **Python** — Try `python3 --version`; if that command isn't found, try `python --version` and confirm it reports Python 3.x. Capture whichever command worked as `<PYTHON>` — every step below runs its script via `<PYTHON> <script>.py`. If neither yields Python 3, stop and tell the user to install Python 3.7+.
2. **Token** — Run `<PYTHON> <SKILL_DIR>/scripts/check_token.py`. Verifies that `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` is set, and reports its length — nothing else — without reading the value. Note: this is a shell environment variable the user exports themselves — it is **separate** from the MCP `sigrid_token` set via `/plugin` config (that one lives in the OS keychain and is not accessible to this local script). If the check fails, ask the user to `export SIGRID_CI_TOKEN=<their Sigrid token>`; do not point them at the keychain token. This script's output is the complete diagnostic for the token — including later, if `agents.py` itself rejects the token as invalid or too short. There is nothing more to learn by inspecting the environment yourself, and doing so risks leaking the token into the transcript — so don't, even to debug an unexpected error.
3. **Sigrid CI scripts** — Run `<PYTHON> <SKILL_DIR>/scripts/ensure_sigridci.py`. Fetches the sigridci repository into a persistent cache (`sigrid/sigridci` in the user's cache directory), pulling the latest commit if already cached rather than re-cloning. The script prints the path to the cached directory; capture it as `SIGRIDCI_DIR`.
4. **Source root** — Use the path the user stated explicitly, else the profile's **Source root** resolved against the repository root, else the repository root.
5. **Customer and system** — Must match what is registered in Sigrid. Use values the user stated explicitly, else read them from `.sigrid/profile.md`. If the values are only implied (inferred from a company name, repo name, or directory), confirm them before running.
6. **Capabilities** — A comma-separated string from the models requested: `maintainability` → `maintainability`, `open-source` → `osh`, `security` → `security`. Example: `maintainability,osh`.

## Running the analysis

`agents.py` prints feedback to stdout as one `Inline results: <capability>` line followed by one JSON line, per capability, interleaved with progress logging.

```bash
<PYTHON> "$SIGRIDCI_DIR/sigridci/agents.py" \
  --customer <CUSTOMER> \
  --system <SYSTEM> \
  --source <SOURCE_ROOT> \
  --capability <CAPABILITIES>
```

`<PYTHON>` is from the Python preflight check, `<SIGRIDCI_DIR>` from `ensure_sigridci.py`. The run blocks until analysis completes (up to ~30 minutes); read the JSON straight from the command's output.

There's no `--publish`/`--publishonly` support here — this skill is feedback-only. That also means on-boarding never occurs: if the run reports the system isn't on-boarded, that's expected, so report it and don't retry rather than treating it as a crash. If the user asks to publish results or show them on the dashboard, tell them this skill doesn't do that.

## Avoid

- **NEVER** print, echo, or log the `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` value — this includes indirectly, via `env`, `printenv`, `env | grep ...`, `echo $SIGRID_CI_TOKEN`, or quoting it in a response to the user. If `agents.py` reports a token problem, relay its message; `check_token.py`'s presence/length output is the only thing worth inspecting on your own — tool results and your own responses both persist to the transcript, so "just debugging" leaks the token exactly as much as showing it to the user on purpose.
- **NEVER** guess customer or system names — always ask the user when unclear.
