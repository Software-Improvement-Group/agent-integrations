# Autofix

> Pairs with `diagnose` and `triage-findings`: plan first, then fix.

Fixes what was planned, as local commits on a branch.

```
/axis:autofix [maintainability|architecture|open-source|security|reliability] [handover path]
```

- **Maintainability**: refactors the ranked candidates and checks each with the guardrails.
- **Architecture**: moves or splits files, adds a facade, or reroutes calls, then recounts the call
  sites against the numbers diagnose predicted.
- **Security, reliability**: fixes the will-fix findings, one commit each, and offers to set them
  to `FIXED` in Sigrid.
- **Open-source**: one commit per dependency. A dependency that needs a person goes in the report,
  with the researched options.

It works from a handover in `.sigrid/handovers/`, which the plan skills always write. Pass a
path, or it picks the only open one and asks if there are several. With none, it plans first.

## Prerequisites

- Sigrid customer and system in `.sigrid/profile.md` (`/axis:setup`)
- Build and test commands for the repo
