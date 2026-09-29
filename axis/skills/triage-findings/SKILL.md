---
name: triage-findings
argument-hint: "[security|reliability|open-source]"
description: >
  Goes over a list of Sigrid findings for a findings-based model and decides each one: false
  positive, risk accepted, needs a person, or will fix. Writes the decision back to Sigrid and lists
  the findings that need a person's decision. Never changes code or opens issues. Security and
  reliability: SAST findings. Open-source: dependency vulnerabilities, outdated, unlicensed,
  abandoned, or unmanaged libraries. Use to "triage security findings", "work through the findings
  backlog", "what should I do about this finding", "mark this as a false positive / accepted risk",
  "which dependency risks should we act on", "go over our CVEs", "OSH findings", "dependency risk".
---

# Triage findings

Triage covers the findings-based models: it goes through a list of findings and decides each. It
never changes code; `/autofix <model>` fixes what triage decided to fix. Opening issues is up
to whoever runs the skill.

## Which model

Take it from `$ARGUMENTS` or the request. None named: ask, security, reliability, or open-source.

Metrics-based models (maintainability, architecture) are a state to diagnose, not a list to go
through. Say that in one line and hand off to `/diagnose <model>`.

## Context

Customer, system, baseline branch, and the findings models come from `.sigrid/profile.md` at the
repository root, or from the request. Missing: ask, suggest `/setup`, and write the answer
back to the profile. Apply any behavior guidance the profile records.

Then follow the model's reference file:

- security: `references/security.md`
- reliability: `references/reliability.md`
- open-source: `references/open-source.md`

## Closing

Report every finding with its decision, and list separately every finding that needs a person
(finding ID or purl, file:line where there is one, the blocker) and every finding a subagent
failed to resolve. Nobody else is looking at Sigrid at the end of this run.

When there is something to fix, write and offer a handover as described in
`../autofix/references/handover.md`, carrying what the model's reference file asks for.
