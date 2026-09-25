# Diagnose

> Pairs with `autofix`: diagnose first, then fix.

Diagnoses a Sigrid system for a metrics-based model and names the highest-leverage fix. Never
changes code.

```
/axis:diagnose [maintainability|architecture]
```

- **Maintainability**: finds the property most worth fixing and the code driving it: one primary
  candidate, runner-ups, and what it rejected and why.
- **Architecture**: finds the directory whose structure is most worth fixing, based on Sigrid's
  measured dependency graph, and names the concrete fix.

If nothing qualifies, it says so. Otherwise it writes the plan as a handover in `.sigrid/handovers/`
and offers to fix it now with `/axis:autofix`, later, or not at all. For security, reliability, or
open-source findings, use `/axis:triage-findings`.

## Prerequisites

- Sigrid customer and system in `.sigrid/profile.md` (`/axis:setup`)
