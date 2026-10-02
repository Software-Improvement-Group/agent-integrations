---
name: autofix
argument-hint: "[maintainability|architecture|open-source|security|reliability] [handover path]"
description: >
  Fixes Sigrid findings as local commits on a branch, for any model; never pushes or opens change
  requests. Security and reliability fixes also update the finding status in Sigrid. Works from
  findings in the chat or a /diagnose or /triage-findings plan, and plans first when there is
  neither. Use for "fix this", "fix these findings", "start refactoring", "implement the
  architecture fix", "fix dependencies", "fix this CVE", "apply the handover".
---

# Autofix

Changes code and commits it on a branch. Pushing, change requests, and issues are up to whoever
runs the skill.

## Which model

Take it from `$ARGUMENTS`, the handover, or the request. None named: ask which model.

## Input

In order:

1. A handover or findings already in this chat: fix exactly those; given findings count as will-fix.
2. An explicit handover path in the arguments (`.sigrid/handovers/...`).
3. Exactly one open handover for the model (not `.done.md`): use it, and say so in one line.
4. Several: ask which. List each with age and target, newest first; the last option is "run a
   fresh plan".
5. None: say so and run the plan skill for the model (`/diagnose` for maintainability and
   architecture, `/triage-findings` for the rest), then continue here with its handover.

A handover is read as `references/handover.md` describes: check staleness
before acting and update item status as you go.

## Context

Customer, system, and baseline branch come from `.sigrid/profile.md` at the repository root, or
from the request. Missing: ask, suggest `/setup`, and write the answer back to the profile.
Apply any behavior guidance the profile records, such as branch naming or off-limits code.

## Branch

Clean worktree, or ask. On the baseline branch: branch off it. On a branch containing the baseline
head: stay. Otherwise ask. Never fetch or pull.

## Fix

Follow the model's reference file:

- maintainability: `references/maintainability.md`
- architecture: `references/architecture.md`, which reads
  `../diagnose/references/architecture-graph.md`
- security: `references/security.md`
- reliability: `references/reliability.md`
- open-source: `references/open-source.md`

## Commits

Commit as the reference file says. Every commit message ends with the trailer:

```
Generated-by: Sigrid Axis autofix
```

Never push, open a change request, or open an issue.

## Report

The branch; per commit, what changed and why, with the Sigrid finding IDs or metrics it addresses;
what was not verified; every item skipped and why; and every item that needs a person, with its
blocker.
