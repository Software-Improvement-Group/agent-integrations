# Triage Findings

> Pairs with `autofix`: triage first, then fix.

Decides each Sigrid finding for a findings-based model: false positive, risk accepted, needs a
person, or will fix. It never changes code or opens issues; the report lists what needs a person,
for you or your pipeline to act on.

```
/axis:triage-findings [security|reliability|open-source]
```

1. Takes a finding ID, a pasted finding, or a backlog to work through.
2. Reads the flagged code (security, reliability) or researches the dependency in public
   advisories and registries (open-source), then classifies it. A false positive or accepted risk
   needs a file:line and a reason.
3. Writes the decision back to Sigrid, after you confirm false positives and accepted risks
   (security, reliability; Sigrid has no status API for open-source).
4. Lists every finding that needs a person's decision, with the blocker.
5. Writes a handover for `/axis:autofix` and offers to fix the will-fix findings now, later, or
   not at all.

## Prerequisites

- Sigrid customer and system in `.sigrid/profile.md` (`/axis:setup`), plus the security or
  reliability model if you don't use the default

For open-source, the research agent queries package registries and advisory databases. You can
pre-allow these hosts in `.claude/settings.json`:

```
pypi.org, npmjs.com, mvnrepository.com, central.sonatype.com,
crates.io, nuget.org, github.com, rustsec.org
```

## Example

```
/axis:triage-findings security under src/payments/
```
