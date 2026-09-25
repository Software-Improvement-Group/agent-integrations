# Autofix reliability findings

Reliability findings are fixed exactly like security findings: follow `security.md` next to this
file, with `get_finding` using `finding_type: "reliability"`. From `guardrails_quality_check`,
fix anything new it flags on the changed code. A fix that would change behavior callers may rely
on, such as error types or retry and timeout semantics, is a blocker like the ones listed there.
