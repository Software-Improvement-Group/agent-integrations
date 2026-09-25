---
name: autofix
argument-hint: "[maintainability|architecture|open-source|security|reliability] [handover path]"
description: >
  Fixes what /axis:diagnose or /axis:triage-findings planned, as local commits on a branch; never
  pushes or opens change requests. Maintainability: refactors the ranked candidates, verified with
  guardrails. Architecture: moves or splits files, adds a facade, reroutes calls, verified against
  Sigrid's graph numbers. Security and reliability: fixes will-fix findings and updates their status
  in Sigrid. Open-source: bumps or declares dependencies, verified with Sigrid CI. Works from a plan
  handover in .sigrid/handovers/; with none, plans first. Use for "fix this",
  "apply these improvements", "start refactoring", "implement the architecture fix", "fix these
  findings", "fix dependencies", "update vulnerable packages", "fix this CVE", "apply the handover".
---

# Autofix

Changes code and commits it on a branch. Pushing, change requests, and issues are up to whoever
runs the skill.

## Which model

Take it from `$ARGUMENTS`, the handover, or the request. None named: ask which model.

## Input

In order:

1. The handover a plan run in this chat just wrote.
2. An explicit handover path in the arguments (`.sigrid/handovers/...`).
3. Exactly one open handover for the model (not `.done.md`): use it, and say so in one line.
4. Several: ask which. List each with age and target, newest first; the last option is "run a
   fresh plan".
5. None: say so and run the plan skill for the model (`/axis:diagnose` for maintainability and
   architecture, `/axis:triage-findings` for the rest), then continue here with its handover.

A handover is read as `../../references/handover.md` describes: check staleness
before acting and update item status as you go.

## Context

Customer, system, and baseline branch come from `.sigrid/profile.md` at the repository root, or
from the request. Missing: ask, suggest `/axis:setup`, and write the answer back to the profile.
Apply any behavior guidance the profile records, such as branch naming or off-limits code.

## Branch

Clean worktree, or ask. On the baseline branch: branch off it. On a branch containing the baseline
head: stay. Otherwise ask. Never fetch or pull.

## Fix

Follow the model's reference file:

- maintainability: `references/maintainability.md`
- architecture: `references/architecture.md`, which reads
  `../../references/architecture-graph.md`
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
