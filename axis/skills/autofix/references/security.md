# Autofix security findings

Fixes the will-fix findings from the plan (`finding_id`, file:line, title, the fix to make). MCP
tools: `get_finding`, `update_finding_status`, `guardrails_quality_check`.

## For each finding

1. Re-read the flagged code. If it no longer matches the finding (moved, already fixed), check
   with `get_finding` and skip with the reason.
2. Write the fix in the working tree, following the plan and the finding's recommendation.
3. Run `guardrails_quality_check` on the changed code. Only the security results matter; fix
   anything new it flags before moving on.
4. Commit, one commit per finding: `Fix: <finding title> (Sigrid <finding_id>)`.

A fix that turns out to need a design decision, a change to the auth or access-control decision
itself, an action outside the working tree, an exported signature change, or edits in more than 3
files: stop on that finding, revert it, and set it to
`REFINED` with the blocker as remark, prefixed "Sigrid Auto-fix Agent:".

## Promote to `FIXED`

Committed findings stay on `WILL_FIX`. At the end, list them and ask whether to set them to
`FIXED` now. Explain the trade-off: on `WILL_FIX`, a triage run before the branch is merged picks
them up again; on `FIXED`, they must go back to `WILL_FIX` if the branch is not merged. Follow the
profile instead of asking when it records a preference; waived, leave them on `WILL_FIX` and say
so.
