# Autofix maintainability

Executes the refactoring candidates from the plan, one at a time: the primary finding, then the
runner-ups. Never pick up a candidate the plan rejected. MCP tool: `guardrails_quality_check`;
without it, stop with a clear error.

## References

Read these on the following triggers, nothing else:

- **Once per run, before the first change:** [principles.md](maintainability/principles.md):
  priority when guidelines conflict, and clean-code hygiene for the code you touch.
- **When creating or editing tests:** [testing.md](maintainability/testing.md).
- **Only when fixing a finding of that property**, before touching code: the guideline, root
  cause, refactoring techniques, and bracket edges.
  - [unit-size.md](maintainability/unit-size.md): long methods/constructors (>15 LOC)
  - [unit-complexity.md](maintainability/unit-complexity.md): high branching (McCabe >5)
  - [duplication.md](maintainability/duplication.md): copy-pasted code (6+ identical lines)
  - [unit-interfacing.md](maintainability/unit-interfacing.md): long parameter lists (>4 params)
  - [module-coupling.md](maintainability/module-coupling.md): large, high-fan-in classes

Missing context before a candidate (serialization constraints, known callers, migration windows)
is a decision point: ask, or skip and log "skipped — missing context".

## For each candidate

**Read the file.** Understand the full class before touching anything.

**Run the existing tests that cover it** before the change, so a failure afterwards is known to be
yours. If nothing covers the code, add a test for the behavior you are about to move (see
[testing.md](maintainability/testing.md)).

The metric value (LOC, McCabe, parameter count, fan-in, clone size, ...) comes from the finding
data in the plan — never re-derive or hand-count it from the source. Read the matching reference
file above for *how* to fix a finding of this property; the *whether-it's-still-a-violation*
question is answered by the finding data going in and by `guardrails_quality_check` coming out.

Scoring is LOC-weighted: a finding's impact = its LOC in a risk bracket / total system LOC. A valid
fix is anything that reduces LOC carrying bad-bracket risk — either by crossing a bracket edge
(change the metric value) or by reducing the unit's/module's LOC so it weighs less in its current
bracket. Pick whichever the code structure supports.

Look at the actual finding — the specific code, the violation magnitude, the surrounding context —
and reason about the right fix.

### When to stop

A refactoring is **done** when:
- Guardrails pass with no new findings introduced.
- The tests that passed before still pass.
- The metric improved — the candidate is no longer a top offender.
- All call sites still compile and the code is readable.

Do not refactor for a perfect score. If the improvement is close enough (e.g. method went from 40
lines to 17), move on.

### Run tests and guardrails after each change

Run the tests from before the change again. Then run `guardrails_quality_check` on each changed
file (it takes the file's full contents and filename, not a path or a diff).

- No new findings: "✓ guardrails clean".
- NEW findings (not pre-existing): fix them before reporting the change done.
- Only pre-existing findings: note them but do not block progress.

Then commit the candidate on its own.

## Invariants — never violate these

- Never change an external interface: public API signatures, serialized field names, or any
  other wire contract that callers outside the repo depend on. Diagnose rejects candidates that
  need this; if a fix turns out to need it anyway, skip the candidate.
- Component-level properties (componentIndependence, componentEntanglement): make no code
  changes here. Diagnose only passes these on when nothing else qualified; surface the issue and
  point to `/axis:diagnose architecture`.
- Run the project's formatter/linter on changed files before reporting done — formatting is
  typically enforced by CI.
- When a function or type signature changes, update every call site (constructor calls, factory
  functions, instantiations) in the same change and verify they compile or type-check.

## Error handling

- File not found: skip the candidate, continue, note in the final report.
- Build or type error, or a guardrail failure that cannot be resolved: try one different
  approach; if that fails, revert the candidate, log it as "skipped — build error" or "skipped —
  guardrail failure", and continue.
- Tests fail after the change: try one different approach; if that fails, revert the candidate,
  log it as "skipped — tests fail", and continue.
- No metric improvement after a valid refactoring: try one alternative approach; if it still
  doesn't move, revert, note as "no measurable improvement", move on.
- `guardrails_quality_check` returns an error mid-run: note it, mark the candidate "⚠ unverified",
  and continue — do not block on a tool outage.
- Call sites in generated or external code that cannot be updated: note which were left unchanged
  and warn that the refactoring may need a manual follow-up.
- Empty candidate list: "No candidates found — nothing to do", and stop.

## Report

    Refactoring complete — <N> files changed, <M> skipped

    ┌───┬────────────────┬────────────┬────────────┬─────────────────────────────────┐
    │ # │ File           │ Before     │ After      │ Status                          │
    ├───┼────────────────┼────────────┼────────────┼─────────────────────────────────┤
    │ 1 │ OrderService   │ 18 params  │ 3 groups   │ ✓ guardrails clean              │
    │ 2 │ PaymentService │ —          │ —          │ skipped — guardrail failure     │
    └───┴────────────────┴────────────┴────────────┴─────────────────────────────────┘
