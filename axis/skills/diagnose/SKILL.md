---
name: diagnose
argument-hint: "[maintainability|architecture]"
description: >
  Finds the one thing most worth fixing in a Sigrid system, or reports that nothing qualifies.
  Maintainability: the property and the candidates driving it. Architecture: the directory and the
  concrete fix. Never changes code; /autofix acts on its plan. Use for "what is our biggest
  maintainability problem", "where should we start improving code quality", "why is our
  architecture rating low", "diagnose the architecture of <directory>".
---

# Diagnose

Diagnose covers the metrics-based models: it reports the system's state and names the one fix
most worth making.

## Which model

Take it from `$ARGUMENTS` or the request. None named: ask, maintainability or architecture.

Findings-based models (security, reliability, open-source) are a list to go through, not a state to
diagnose. Say that in one line and hand off to `/triage-findings <model>`.

## Context

Customer, system, and baseline branch come from `.sigrid/profile.md` at the repository root, or
from the request. Missing: ask, suggest `/setup`, and write the answer back to the profile.
Apply any behavior guidance the profile records.

Then follow the model's reference file:

- maintainability: `references/maintainability.md`
- architecture: `references/architecture.md`, which reads
  `references/architecture-graph.md`

## Closing

When there is something to fix, write and offer a handover as described in
`../autofix/references/handover.md`, carrying what the model's reference file asks for.
