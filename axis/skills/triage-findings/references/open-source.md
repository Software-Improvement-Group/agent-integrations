# Triage open-source health findings

MCP tools: `opensourcehealth_get_risks` (all six risk dimensions) and
`opensourcehealth_get_vulnerabilities` (CVE detail). Use findings already in context when the user
gave them; otherwise query, scoped to what the user asked for.

Open Source Health has no status API: `update_finding_status` does not work for it. The decisions
live in the handover and the report — never try to mark findings in Sigrid.

## Group

Group findings by dependency (purl). One dependency may carry several CVEs or risks; the unit of
decision is the dependency, since one version bump can clear several findings. A dependency in
several manifests stays one unit: a bump may need code changes in every module that uses it, so
they land together.

## Research

Earlier handovers in `.sigrid/handovers/` record user decisions not to act on a dependency. Keep
them unless the user asks to revisit; they are not researched again.

Vulnerability-only dependencies whose finding data names a patch or minor next version need no
research: classify them will-fix with that version. Autofix researches if the bump turns out
insufficient.

For the rest, spawn the `osh-researcher` agent per dependency with the library name, ecosystem, and
an actionable description of each risk. It has web access only — no project files, no MCP, no
internal context. A CVE ID is self-explanatory, but Sigrid-specific risks need context it can't
look up: not "freshness risk" but "current version is 2.3.1, latest available is 4.0.0, last
updated 3 years ago". Give it enough without exposing internal system details. Research
dependencies in parallel. Researcher unreachable: the dependency needs a person, with that as
the reason.

## Classify

| Risk type | Typical resolution | Will fix? |
|-----------|--------------------|-----------|
| Vulnerability | Bump to patched version | Yes |
| Freshness | Bump to latest | Yes |
| License | Add missing license declaration, or replace library | Only when declaring a license |
| Activity | Replace abandoned library | No, needs a person |
| Stability | Pin stable version or replace | No, needs a person |
| Management | Declare in package manager | Yes, if trivial (e.g. adding to manifest) |

Also needs a person: conflicting fix ranges (no single version satisfies every risk), no fix
available, or an upgrade the research flags as major with breaking changes. When several upgrade
paths exist, present them to the user as code impact ("patch bump, no code changes" vs "minor
bump, one deprecated call to update"), not version numbers; waived, pick the smallest sufficient
bump.

The user may also decide not to act on a dependency. Record that as a user decision in the
handover and the report; there is nowhere in Sigrid to record it.

## Needs a person

In the report, a dependency that needs a person carries why it is included the way it is, the
concrete options with the researcher's source URLs, and nothing else.

## Handover

Per will-fix dependency: purl, manifests, risks and CVEs to clear, target version, whether the
dependency is direct, transitive, or needs an override, and the researcher's alternative versions
and source URLs, if any.
