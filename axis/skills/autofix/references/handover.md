# Handovers

A handover carries a plan from `/axis:diagnose` or `/axis:triage-findings` to `/axis:autofix`,
across sessions, worktrees, and people. The reader is a capable agent with zero context that cannot
ask you anything: it can act on the handover alone or it is not done.

## Offering one

At the end of a plan run, when there is something to fix, write the handover, then ask the
user:

- **Fix now** (default): continue in this chat with `/axis:autofix <model>` on this handover.
- **Save for later**: the user can review and edit it, then run `/axis:autofix <model>` whenever
  they like, in this or a fresh session. Recommend this when the run was long.
- **Stop**.

## Writing

Write to `.sigrid/handovers/<model>-<timestamp>.md` (timestamp `YYYYMMDD-HHMMSS`). Never overwrite
an existing handover: batch triage, re-diagnosis, and worktrees would lose work. Handovers are
personal; if `.sigrid/handovers/.gitignore` is missing, create it containing `*`.

Contents, as a guide rather than a template:

- **Header**: model, timestamp, and the target as concrete file paths.
- **The chosen fix and why**, in terms the reader can check against the code.
- **Rejected alternatives and user decisions**, so the next session doesn't reopen them.
- **Status per item**: done, skipped (with the reason), or remaining. Everything starts remaining.
- **Pointers back to the primary sources** to check against: Sigrid finding IDs, metric values,
  files and lines.

Use only what this run produced. Write `unknown` rather than a plausible value. Spell out paths and
directions; never "as discussed". The model's reference file says what else its handover must
carry.

Then one line in chat: the path written and the one-line goal.

## Reading

If a target no longer matches the code (moved, gone, already fixed), say so and mark it skipped.

Update the status per item as you go, including items left for a person. Never delete a handover.
Once nothing is remaining, rename it to `<model>-<timestamp>.done.md`: it stays as the record of
the run and its user decisions, and is never picked again.
