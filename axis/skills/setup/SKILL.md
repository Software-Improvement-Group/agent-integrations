---
name: setup
description: >
  Set up (or update) the Sigrid profile for this repository. Detects the Sigrid system from the
  repo, asks the user for what's missing and any behavior preferences, then writes them to
  `.sigrid/profile.md`, which the Axis skills read. Use when first installing the plugin in a repo,
  when a skill reports the profile is missing, or when conventions change. Trigger on "set up
  Sigrid", "configure Sigrid", "Sigrid onboarding", or "my Sigrid customer/system is ...".
---

# Sigrid setup

Writes `.sigrid/profile.md` at the repository root (`git rev-parse --show-toplevel`). It is
committed, so the whole team shares one profile per repo. It holds values only; the skills that
read it know what each field means.

## Procedure

1. **Existing profile.** If `.sigrid/profile.md` exists, this is an update: show what is recorded
   and ask what to change. Never silently overwrite populated fields.

2. **Old per-user profile.** Earlier versions kept one profile per user, holding several systems,
   in `~/.claude/plugins/data/sigrid-*/CLAUDE.md`. If one exists and no repo profile does, offer to
   copy it: take the system block whose `Repo` key matches `git remote get-url origin` (or the only
   block), plus the shared sections. Leave the old file in place.
   <!-- Remove this step one release after the Axis launch. -->

3. **Detect** the Sigrid system from the repo: customer, system, baseline branch, and source root.
   Read them from a `sigrid.yaml` / `sigrid.yml` (its directory is the source root) and from CI
   pipeline configuration that runs Sigrid CI. Where nothing says otherwise, the baseline branch
   is `main` or `master`, whichever exists, and the source root is the repository root. Never
   infer customer or system from company or repo names. Infer the branch naming pattern from
   existing branches, if they share one.

4. **Interview**, in small batches, for what is still missing or unclear:
   - **Sigrid system**: whatever detection left open or found conflicting. Customer and system can
     be read off the Sigrid URL `sigrid-says.com/<customer>/<system>`. Customer is lowercase
     alphanumeric, at least 2 characters; system is lowercase alphanumeric segments separated by
     hyphens. Ask again if a value doesn't fit.
   - **Branch naming**: confirm the inferred pattern, or ask whether they want one.
   - **Findings models**, only if the user uses a non-default security model (`ow10`, `sigsec`,
     `pci4`, `owasvs4c`; default OWASP Top-10) or reliability model (`sigrel`, `5055rel`; default
     SIG Code Reliability Top-10).

   Then, lightly, ask whether they want to customize any skill behavior. Capture only what they
   volunteer; the defaults are fine.

5. **Write** `.sigrid/profile.md` with only the fields that have a value. Leave out anything
   blank or default, and add the behavior section only when the user gave preferences:

   ```markdown
   # Sigrid profile

   - **Customer**: acme
   - **System**: backend-api
   - **Baseline branch**: main
   - **Source root**: .
   - **Branch naming**: fix/<area>
   - **Security model**: sigsec
   - **Reliability model**: 5055rel

   ## Customizing behavior

   - Never touch `generated/`.
   ```

   Then show what was recorded and where each value came from, and say the file should be
   committed.

## Notes

- This skill only reads the repo and writes the profile. It never changes project code or calls
  the Sigrid MCP.
- Never store the Sigrid API token in the profile. The MCP token is plugin config in the OS
  keychain. `/axis:change-feedback` runs Sigrid CI locally and reads a separate `SIGRID_CI_TOKEN`
  (or `SIGRID_TOKEN`) environment variable the user exports themselves.
