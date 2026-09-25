# Autofix open-source health

Fixes the will-fix dependencies from the plan (purl, manifests, risks to clear, target version,
direct/transitive/override, the researcher's alternatives). Needs `/axis:change-feedback` for
verification.

Process dependencies one at a time. Each ends as exactly one commit, or reverted and reported as
needing a person. Open Source Health has no status API: never try to mark findings resolved in
Sigrid.

## Implement

1. Apply the bump or fix with ecosystem-appropriate mechanics, in every manifest listed.
2. Run tests if a test command is available.
3. **Verify with Sigrid CI** (mandatory): `/axis:change-feedback open-source` on the working
   tree. It is the only way to confirm the finding is actually gone; unverified fixes are never
   committed. Still reported: try the next alternative version. None left: spawn the
   `osh-researcher` agent with the library, ecosystem, the versions already tried, and an
   actionable description of each risk still open (no internal system details), and try what it
   finds. Still nothing, or the researcher or registries unreachable: needs a person.

**Needs a person** when the change becomes widespread (many files, large diff), tests fail
and the fix isn't obvious, the resolution introduces new dependency conflicts, or research finds
no single version that clears every risk. Reason about risk rather than following a rigid
threshold: a patch bump in a well-tested npm package is low risk; a minor bump in a Maven library
with no semver guarantees deserves more caution. The commits get human review before they merge,
so moderate uncertainty is acceptable.

## Commit and report

- **Commit** message: the bump in the subject line; in the body the dependency purl, CVEs and
  risks cleared, old → new version, direct/transitive/override, advisory references, residual
  risk, and what was NOT verified.
- **Needs a person**, in the report: why the dependency is included the way it is, the concrete
  options with source URLs, and the attempted diff if there was one. Lean — only genuinely useful
  content.
