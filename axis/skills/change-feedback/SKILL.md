---
name: change-feedback
argument-hint: "[maintainability|architecture|open-source|security]"
description: >
  Sigrid's verdict on local changes before committing or pushing, checked locally without
  publishing anything to Sigrid. Covers maintainability, open-source health, security, and
  architecture (new dependencies, bypassed facades, cycles). Use for "run Sigrid on my changes",
  "check this before I push", "sigrid ci", "does this change introduce bad coupling", "check my diff
  for architecture drift", "is this new dependency safe".
---

# Change feedback

## Which models

Take the models from `$ARGUMENTS` or the request; phrasing is flexible ("for security problems").
With none named, run maintainability, open-source, and security, not architecture.
<!-- Include architecture in the default once architecture runs in Sigrid CI. -->

Customer, system, and baseline branch come from `.sigrid/profile.md` at the repository root, or
from the request. Missing: ask, suggest `/setup`, and write the answer back to the profile.

## How

- **maintainability, open-source, security**: one Sigrid CI run covering all of them; follow
  `references/sigrid-ci.md`. `<SKILL_DIR>` there is this skill's directory.
- **architecture**: follow `references/architecture.md`. It uses the Sigrid graph until
  architecture runs in Sigrid CI.

When both apply, run them in parallel and report per model.
