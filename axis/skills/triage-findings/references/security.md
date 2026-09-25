# Triage security findings

New finding → analysis → false positive? → (no) → accept risk? → (no) → needs a person? → (no) →
will fix (default).

MCP tools: `get_finding`, `security_get_findings`, `update_finding_status`. Pass the profile's
security model as `model`; omit it when blank.

## Entry points

- **A specific finding ID** — call `get_finding` with `finding_type: "security"`.
- **A pasted finding** (e.g. copied from the Sigrid UI, no UUID) — resolve to a `finding_id` by
  calling `security_get_findings` with `path_prefix`. No match, or more than one match: still
  analyze and classify, but skip `update_finding_status` and tell the user the finding is
  ambiguous and its status must be updated manually in Sigrid.
- **Bulk / no input given** — call `security_get_findings` with defaults for whatever is not
  defined yet, but pass `status: ["RAW", "REFINED", "WILL_FIX"]` explicitly — the tool's own
  default also includes `ACCEPTED`, which would resurface findings a human already accepted.
  Include `ACCEPTED` only if the user asks to revisit already-accepted findings. Pass
  `path_prefix` when the user scopes the request to an area.

A finding with toolName "SIG Open Source Health" belongs to the open-source model: leave it out and
say so.

## Fan out

More than one finding: fan out analysis and classification to one subagent per finding.

- Cap concurrency at ~8 subagents in flight; queue the rest.
- Brief each subagent with the `finding_id` and the profile's customer, system, and model — don't
  let it re-resolve the profile itself.
- Each subagent returns exactly one thing: the classification and its evidence sentence, the
  blocker that makes it need a person, or the fix to make for will-fix.
- A subagent that errors or returns nothing: report that finding as unresolved rather than
  dropping it silently.

## Analyze

Read the flagged code and its surrounding context. The classification depends on it — don't
classify without reading the actual file:line.

## Classify (evidence gate)

`FALSE_POSITIVE` and `ACCEPTED` each require concrete evidence — a file:line plus one sentence —
or the finding falls through to the two outcomes below. Every gate here is mechanical — a named
trigger, never a confidence score.

- **False positive**: the check itself is wrong, not the code — like steam triggering a smoke
  detector. The tell: the best fix would be to fix the check, not the flagged code. If the fix
  you'd reach for is a code change, it isn't a false positive.
- **Accepted risk**: real issue, but the residual risk is acceptable *at Sigrid's original
  severity* — name the mitigating context (e.g. "internal-only admin endpoint, no external route,
  see `routes.py:80`"). No severity override exists to lean on here.
- **Needs a person** (`REFINED`): no evidence for either of the above, *and* any one of these
  holds — the fix requires a design or product decision rather than a mechanical change; it would
  change the auth/access-control decision itself rather than harden it; remediation needs an
  action outside the working tree (secret rotation, infra or config change, dependency bump); the
  analysis could not locate the sink or data flow the finding describes; the fix would change an
  exported signature or need edits in more than 3 files. Name the blocker in one sentence.
- **Will fix** (the default): no evidence for false positive / accepted, and no blocker above.

The remark is this evidence sentence, blocker, or fix, verbatim or lightly cleaned up — don't write
it twice in different words.

## Write back to Sigrid

Write `WILL_FIX` and `REFINED` directly. Propose false positives and accepted risks with their
evidence and confirm before writing. Only the user can waive that confirmation, by asking for it
explicitly; never infer a waiver from the run being unattended, scripted, or in a loop. A waived
run still needs, in context, before suppressing anything: which parts of the system are
externally reachable, a severity ceiling (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) above which nothing
is suppressed, and the user's acknowledgement that accepted risks need a human review afterwards.
Without them, or above the ceiling, write `REFINED` with the proposed classification in the remark.

Call `update_finding_status` with:
- `status`: `FALSE_POSITIVE`, `ACCEPTED`, `REFINED`, or `WILL_FIX`. Never `FIXED`; that is
  autofix's to set once the fix is committed.
- `remark`: the remark above, prefixed with "Sigrid Auto-fix Agent:".

Skip this call when no `finding_id` could be resolved (ambiguous pasted finding) and report that
instead.

## Handover

Per will-fix finding: the `finding_id`, file:line, the finding title, and the fix to make in one
sentence.
