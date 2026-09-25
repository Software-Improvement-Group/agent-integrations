# Diagnose maintainability

## Goal

Identify where maintainability can be improved and why, judge whether each candidate is really
worth fixing, then stop before implementation: that belongs in `/axis:autofix maintainability`.

Not all refactoring candidates are equal. Choosing the wrong one wastes effort on low-impact or
high-risk changes. Reject the noise so autofix only ever sees high-leverage candidates.

MCP tools: `maintainability_get_ratings`, `maintainability_get_findings`. They describe Sigrid's
last baseline analysis, never the working tree.

- A large `count` on a big system can exceed the tool-output limit and land in a file instead of
  inline; check for that before concluding a property has few findings.
- Finding `status` is `RAW`, `WILL_FIX`, or `ACCEPTED`. `ACCEPTED` means the team already triaged
  and deprioritized it.

## How to think about maintainability

There is no fixed checklist; reason from the numbers and the code. A property's low score traces
to one of two shapes:

1. **A concentrated cluster**: a handful of files or units carry a disproportionate share of the
   bad-bracket LOC (e.g. five DTOs with 20+ parameter constructors). Fixing those files is
   contained and high-leverage.
2. **A diffuse spread**: bad-bracket LOC spread thinly across many unrelated files. Usually not
   worth chasing file by file; look for one structural cause (a shared base class, a code-gen
   template, a copy-pasted pattern) that explains the spread. With no shared cause, say so and
   treat the property as low-leverage regardless of its rating.

Scoring is LOC-weighted: a finding's contribution is its LOC in a risk bracket / total system LOC.
A rating moves in exactly two ways: a metric value crosses a bracket edge (e.g. params 8 → 4), or
the LOC carrying the bad-bracket weight shrinks (e.g. a large unit split so each half weighs
less). Both are legitimate.

## Choosing the candidates

1. **Ratings.** unitSize, unitComplexity, unitInterfacing, duplication, moduleCoupling,
   componentIndependence, componentEntanglement, each 0.5–5.5 stars. Sort worst-first with the
   gap to 4.0.
2. **Findings for every property**, top 100 each, in parallel. Results are sorted by
   LOC-weighted contribution, so the first ones are the highest-impact.
3. **Cross-reference.** A finding in 2+ property lists is higher leverage than one affecting a
   single metric.
4. **Judge.** Is the pattern a concentrated cluster or a diffuse spread (see "How to think about
   maintainability")? A single finding does not move a rating much. Judge candidates against the
   language's best practices.

`componentIndependence` and `componentEntanglement` are component-level and autofix does not
change them. Only pick one when no other property has a qualifying candidate; then present it as a
suggestion and point to `/axis:diagnose architecture`, which has the graph to diagnose it properly.

## Reject rules

- A property qualifies only if its gap to 4.0 is meaningful. Within ~0.1 stars of 4.0 with no
  concentrated cluster behind it: say it's not worth chasing right now.
- Reject a candidate, and say which rule applied, when it is:
  - generated, vendored, or test code;
  - `ACCEPTED` (`WILL_FIX` may still be worth including: queued, not yet acted on);
  - only fixable by visibly worsening another property or file (e.g. a split that adds
    duplication elsewhere): note the trade-off instead of silently picking a side;
  - only fixable by changing an external interface: a public API signature, a serialized field
    name, or another wire contract that callers outside the repo depend on. A public unit whose
    fix stays internal (e.g. splitting a long endpoint body) still qualifies.
- No candidate survives for the weakest property: fall back to the next-weakest that has one.
  None of the seven qualifies: say so, one sentence per property naming the rule that removed its
  best candidate, and stop without offering a handover.

## Verification

For each candidate you report, you read the file (or, for component-level properties without a
single file, the component names), and the LOC and status you cite came from the tool response,
not inference. A flagged file that no longer exists at that path: say so
and drop it.

## Output

Problem/solution pairs, ELI5, a few sentences each: what is wrong and what a fix looks like. Talk
about the code, not the tools or metrics that found it; someone who works in the repo should think
"yes, I recognize that." Never describe a hotspot in metric language alone.

Ratings at a Glance

    <property>    <rating>    <gap to 4.0>
    ... (all 7 properties, sorted worst-first)

Primary Finding

    Problem: [what's structurally wrong, grounded in the actual file content]
    Solution: [what fixes it, in one or two sentences; no implementation detail]
    Properties affected: [list; call out if 2+, that's why it's primary]

Runner-ups (if any)

    Same shape, briefer.

Rejected candidates (only if something notable was excluded)

    One line each: candidate, rule that removed it.

Never state projected rating improvements ("+0.2 stars"): Sigrid does not expose them. Describe
impact qualitatively (e.g. "removes the largest single source of duplication").

## Handover

The plan is the primary finding, then the runner-ups. Per item, the handover carries the Sigrid
finding IDs, the property or properties it affects, file and line range, and the current metric
value (e.g. "14 parameters", "82 lines"). The rejected candidates go in as
rejected alternatives, with their rule.
