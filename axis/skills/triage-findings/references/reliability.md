# Triage reliability findings

Reliability findings (anti-patterns, error-prone constructs) triage exactly like security findings:
follow `security.md` next to this file, with these differences.

- MCP tools: `reliability_get_findings` instead of `security_get_findings`; `get_finding` with
  `finding_type: "reliability"`. Pass the profile's reliability model as `model`; omit it when
  blank.
- **Accepted risk** is about impact, not attack surface: name why the failure mode can't occur or
  is harmless here (e.g. "the collection is never empty, built from a constant list at
  `config.py:12`"). The waived-confirmation guard asks for a severity ceiling and the
  acknowledgement, not reachability facts.
- **Needs a person**: the security blockers that apply (design decision, action outside the working
  tree, unlocatable code path, exported signature, more than 3 files), plus a fix that would change
  observable behavior callers may rely on, such as error types or retry and timeout semantics.
