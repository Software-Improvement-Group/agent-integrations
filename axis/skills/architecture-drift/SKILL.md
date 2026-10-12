---
name: architecture-drift
description: >
  Checks local changes for architecture drift against Sigrid's measured dependency graph: new
  dependencies between directories, bypassed facades, and cycles. Same check as
  /change-feedback architecture. Use before pushing code or opening a pull request, and for
  "check for architecture drift", "does this change introduce bad coupling", "check my diff
  against the architecture".
---

Run `/change-feedback architecture` with `$ARGUMENTS`.
