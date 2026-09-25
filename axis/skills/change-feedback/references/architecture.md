# Architecture drift

Use this before committing or opening a PR, or when reviewing someone else's
branch for architecture risk before merging.

- **The diff is the source of truth for what's new.**
- **The Sigrid architecture graph is the source of truth for what already exists.** It
  describes the baseline branch as Sigrid last analysed it, never the working tree, which is
  exactly what makes it the before-picture for the diff.

A new reference that matches an edge that already exists is normal evolution —
nothing to flag.

**A new reference that doesn't match anything in the graph, or that
closes a cycle, or that skips an existing high-traffic gateway file, is a drift
signal.**

## Prerequisites

- Sigrid MCP available: `architecture_get_internal`, `architecture_get_external_dependencies`

  | MCP tool | Purpose |
  |---|---|
  | `architecture_get_external_dependencies` | Incoming callers of a touched file — blast radius if its contract changes |
  | `architecture_get_internal` | Current dependency structure anchored on the touched files/directories |

  If either tool is unavailable, state which one and stop. Don't approximate the
  dependency structure from reading code — the differentiator is Sigrid's measured
  graph.

## Step 1 — Spin up the check

Default diff scope is the profile's **Baseline branch** (`<baseline>...HEAD`); use
unstaged or staged instead if the user specifically means that, or there's no branch
divergence.

Use a Sonnet subagent, with the customer, system, and diff scope, to do the following:

1. Diff per the given scope. Read the added lines for new imports, calls,
   instantiations, and type references crossing into another directory or module, at
   any granularity from sibling files to whole subsystems. No diff, or no
   cross-directory references found → stop and say so; don't spend MCP calls on a
   change that can't drift.
2. Ground each candidate against the current structure via
   `architecture_get_external_dependencies(customer, system, path=<touched file or
   its common parent directory>, direction="all")` — one call per distinct group,
   capped at ~5 top-level directories (prioritize the groups with the most touched
   files or new references; report which directories were skipped).
3. Cross-reference: does an edge already exist between these two directories, in
   which direction, through which files?
4. Report each reference as **Clean** (matching edge and files) or **Drift**
   (file:line, the graph edge/cycle/gateway violated, and the specific existing
   file(s) it should route through instead).

## Step 2 — Relay

Relay the subagent's report to the user as-is, including any skipped directories so
they can rerun scoped to them.
