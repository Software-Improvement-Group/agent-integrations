# Diagnose architecture

Find the one directory whose structure is most worth fixing and name the concrete fix, or
report that nothing qualifies. Read the shared `architecture-graph.md` first — it defines what Sigrid measures
and how each change moves each number.

## How to think about architecture

A directory is a module boundary. Use the tools and principles below to find the worst directory
and diagnose *why* its structure is bad. There is no fixed checklist; reason from the numbers and
the code. **Fix boundaries before enforcing them** — when boundaries are wrong, fixing coupling
just moves the hub around.

A good boundary has two properties. When one breaks, it looks like this:

1. **Cohesion** — the files inside form one connected cluster of related work and call each other
   more than they call outside. The graph's cohesion % and `architecture_get_internal` tell you
   this directly; an `architecture-explorer` describer confirms what each child does.
   *Broken:* low cohesion, or disconnected clusters in `get_internal` — the directory contains
   two unrelated things, or a child belongs in a neighbor. Fix is structural: split, merge, or
   move children. Dependency cycles (bidirectional edges) are a signal the boundary between two
   children is wrong; which is a pointer to a boundary fix.

2. **Information hiding** — external callers reach the directory through a small surface, not
   scattered across its internals. Centralization measures this as % of LOC in files with no
   external edge — low centralization means too much of the directory's code is directly exposed.
   *Broken:* many internal files have external callers. A facade or gateway consolidates the
   surface.

Also common: **loose root files** (breakdown) — files sitting at a directory's root when
subdirectories exist. They belong somewhere; figure out where from calls and responsibility.
**Excessive coupling** (high edge count or adjacency to many neighbors) — but only after
confirming the boundary itself is right.

A directory's rating changes in exactly two ways: files change directory, or calls change. The
mechanism (move, split, facade, reroute call sites) follows from which property is broken and the
numbers in `architecture-graph.md`. Use the ratings as a sanity check, not the goal.

## Tools

Tools describe Sigrid's last baseline analysis, never the working tree. Read source where
the graph is silent and the answer decides the fix — a missing edge is unmeasured, not absent.

Gotchas:
- `architecture_get_worst_directories`: default `min_volume` (0.2 py) hides leaf dirs on small
  systems — lower to 0.01. Sigrid paths can differ from local layout; check `example_paths` if a
  path returns nothing.
- `architecture_get_internal`: names are bare — resolve to full paths before comparing across
  results.
- `architecture_get_external_dependencies`: capped at 50. If `truncated`, query per child —
  arithmetic on a capped list is wrong.
- `architecture-explorer`: describe what each child does, don't judge.

## Targets and reject rules

- Ratings run 0.5 to 5.5 stars. Judge a directory on its **structure** rating; the five
  sub-ratings say *what* to fix, never *whether*.
- Candidate below **3.5**. Between 3.5 and 4.0 only if nothing below 3.5 survives. Never at 4.0
  or above.
- Reject, and say which rule applied, when the directory is:
  - generated, vendored, or test code;
  - only fixable by visibly worsening a sibling, parent, or destination
- A utility-role directory (`null` coupling and adjacency) is not scored on coupling, so never
  propose cutting its dependencies. It can still have loose root files, a wrong boundary, or
  scattered call sites.
- A directory that acts as a helper or utility but isn't auto-detected as one (see
  `architecture-graph.md`) can be marked as utility — read `utility-role.md` next to this file.
  A helper has no outgoing dependencies to its callers.
- Pick the directory that owns the problem: a parent whose rating is just the aggregate of its
  children is not the target — its children are. A parent whose children are individually at
  target but whose own rating is low is the target.

## Verification

Before proposing a fix, confirm the edges you rely on exist in the tool output and the change
doesn't worsen a neighbor (pushing a sibling, parent, or destination below target).

## Output

State each finding as a problem/solution pair, ELI5, in a few sentences: what is wrong with the
architecture, and what fixes it. Talk about the architecture of the code, not the tools, metrics,
or process used to find it. Someone who works in the repo should think "yes, I recognize that."
One primary finding, some runner-ups if found. No code changes.

If nothing qualifies, say so in one sentence per candidate considered, naming the rule or
objection that removed it, and offer no handover.

Otherwise, write and offer a handover (the shared `handover.md`).

## Handover

The reader is `/axis:autofix architecture`. It reads the code, chooses how to make the change, and
checks its own work against the numbers you give it, so it looks these sections up by name, in
this order:

1. **Goal** — two sentences, imperative, naming local paths: what should be true of the target
   directory afterwards, and which sub-metric that fixes.
2. **System** — the target's Sigrid and local path, and the baseline branch.
3. **Evidence** — verdict (`breakdown` / `boundary` / `enforcement`), structure rating, failing
   sub-rating with its rating, and what the graph and describers showed: the responsibility
   groups with their members, the loose root files, or the neighbor the calls all run to. Then
   the baseline numbers per file involved: calls with the destination, with current siblings,
   elsewhere, from `architecture_get_external_dependencies`. Note edges you expect the graph to
   be missing and whether the source confirmed them.
4. **Plan** — the fix you predicted, as numbered steps, each with the expected effect on the
   numbers above. Mechanisms: move, split, facade with real calls, reroute or consolidate call
   sites, per `architecture-graph.md`. Full paths, and for a split the units that leave. The reader may
   choose a different mechanism if the code makes yours wrong; it must reach the same numbers.
   Every step must be executable as written — no conditional branches, no "decide between A or
   B". If you cannot commit to a step, the finding is not ready to hand over; diagnose further or
   drop it.
5. **Done when** — the target's numbers after the change (`cohesion above 70% internal`,
   `at most 3 files in the target with external edges`). Never predict a star-rating delta;
   Sigrid does not expose projected scores.
6. **Do not** — the sibling, parent, or destination that must not get worse and what would push
   it there; fixes the reject rules excluded that a reader might try next.
7. **Not covered** — the sub-metrics this fix does not touch.

Numbers are what let the reader verify; a section without them is an opinion.
