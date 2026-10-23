# Triage security findings

New finding → analysis → false positive? → (no) → score impact and exploitability → accept risk at
that score? → (no) → needs a person? → (no) → will fix (default) → write status and scores in one
call.

MCP tools: `get_finding`, `security_get_findings`, `update_finding`. Pass the profile's security
model as `model`; omit it when blank.

## Entry points

- **A specific finding ID** — call `get_finding` with `finding_type: "security"`.
- **A pasted finding** (e.g. copied from the Sigrid UI, no UUID) — resolve to a `finding_id` by
  calling `security_get_findings` with `path_prefix`. No match, or more than one match: still
  analyze and classify, but skip `update_finding` and tell the user the finding is ambiguous and
  its status must be updated manually in Sigrid.
- **Bulk / no input given** — call `security_get_findings` with the status scope below and
  defaults for the rest. Pass `path_prefix` when the user scopes the request to an area.

A finding with toolName "SIG Open Source Health" belongs to the open-source model: leave it out and
say so.

### Status scope

Take the statuses from the request, or else from the profile's **Triage status scope**. Neither:
ask, listing the valid statuses (`RAW`, `REFINED`, `WILL_FIX`, `ACCEPTED`, `FIXED`,
`FALSE_POSITIVE`) and offering:

- `RAW` (recommended): only findings nobody has triaged yet, so whatever this run decides does not
  come back in the next run.
- `RAW`, `REFINED`, `WILL_FIX`: also findings still waiting for work, at the cost of triaging them
  again in every later run.
- Other: the statuses the user picks.

In the same question, ask whether to make the answer the default. Yes: write it to the profile as
**Triage status scope**. Always pass `status` explicitly: the tool's own default also includes
`ACCEPTED`, which would resurface findings a human already accepted.

## Fan out
Consider using subagents when there are multiple findings.

- Cap concurrency at ~8 subagents in flight; queue the rest.
- Brief each subagent with the `finding_id` and the profile's customer, system, and model — don't
  let it re-resolve the profile itself. It does not get the profile's deployment or business
  criticality: score with the assumptions in `cvss-scoring.md` step 3 (public facing, business
  critical) and state them in the justification.
- Each subagent returns exactly one classification with its evidence sentence, blocker, or fix to
  make, plus, for anything but a false positive, the Impact and Exploitability labels and
  justification from `cvss-scoring.md`.
- A subagent that errors or returns nothing: report that finding as unresolved rather than
  dropping it silently.

## Analyze

Read the flagged code and its surrounding context. The classification depends on it — don't
classify without reading the actual file:line.

## Score

Score every finding except a false positive with `cvss-scoring.md`, before deciding whether to
accept the risk. It yields an Impact label, an Exploitability label, and a justification. A false
positive is never scored: the check is wrong, so there is no severity to re-evaluate.

A finding scored `INFORMATION` on either label has no real security consequence (test-only code,
unreachable code, no effect). Classify it as accepted risk: the justification is its evidence.

A needs-a-person finding whose blocker is that the sink or data flow could not be located has
nothing to score: it is written without labels.

## Classify (evidence gate)

`FALSE_POSITIVE` and `ACCEPTED` each require concrete evidence — a file:line plus one sentence —
or the finding falls through to the two outcomes below. Every gate here is mechanical — a named
trigger, never a confidence score.

- **False positive**: the check itself is wrong, not the code — like steam triggering a smoke
  detector. The tell: the best fix would be to fix the check, not the flagged code. If the fix
  you'd reach for is a code change, it isn't a false positive.
- **Accepted risk**: real issue, but the residual risk is acceptable at the Impact and
  Exploitability just scored — name the mitigating context (e.g. "internal-only admin endpoint, no
  external route, see `routes.py:80`"). The scores are written with the status, so the acceptance
  stands on the re-evaluated severity, not Sigrid's original one.
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
evidence, and for accepted risks the labels, and confirm before writing. Only the user can waive
that confirmation, by asking for it explicitly; never infer a waiver from the run being unattended,
scripted, or in a loop. A waived run still needs, in context, before suppressing anything: which
parts of the system are externally reachable, a severity ceiling (`LOW`, `MEDIUM`, `HIGH`,
`CRITICAL`) above which nothing is suppressed, and the user's acknowledgement that accepted risks
need a human review afterwards. Without them, or above the ceiling, write `REFINED` with the
proposed classification in the remark.

Write each finding with one `update_finding` call, so the status never changes without its scores:

- `status`: `FALSE_POSITIVE`, `ACCEPTED`, `REFINED`, or `WILL_FIX`. Never `FIXED`; that is
  autofix's to set once the fix is committed.
- `impact` and `exploitability`: the two labels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`,
  `INFORMATION`), for every scored finding. Always send both. Write them even when they equal what Sigrid already holds: the remark is the
  record of the re-evaluation.
- `remark`: the remark above followed by the justification, as one remark prefixed with "Sigrid
  Auto-fix Agent:". An unscored finding has no justification.
- Never `severity`

A call that fails: report the finding as not written, with the decision and scores it should have
had.

Skip the call when no `finding_id` could be resolved (ambiguous pasted finding) and report that
instead.

## Handover

Per will-fix finding: the `finding_id`, file:line, the finding title, the fix to make in one
sentence, and the Impact and Exploitability labels with the justification, so a later run can
prioritize by them.
