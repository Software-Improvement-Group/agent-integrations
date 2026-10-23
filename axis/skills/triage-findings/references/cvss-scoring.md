# Score a security finding (CVSS v4.0)

Used for every security finding except a false positive, before the accepted-risk decision. Output: an Impact label
and an Exploitability label, each `INFORMATION`, `LOW`, `MEDIUM`, `HIGH` or `CRITICAL`, plus a justification.
Sigrid derives the overall severity from the two. Never compute or write a severity, a CVSS score,
or a vector string.

The labels come from CVSS v4.0 Base metrics, translated by the tables below. Threat and Supplemental metrics are not assessed.

## Principles

- **Score independently.** Ignore the severity, CWE ranking or confidence the tool assigned. Use its
  description only to locate the code and the claimed weakness.
- **Verify in the code.** Trace the data flow from entry point to the flagged sink. Check
  sanitization, validation, framework protections, and reachability.
- **Assume an attacker with perfect knowledge** of the flaw and the default defenses. "Hard to
  find" does not lower Exploitability.
- **Assume the configuration the attack requires.** A safe default configuration does not lower the
  score.
- **Score the reasonable worst case you can defend from the code**, not a theoretical maximum.
- **Do not invent facts.** Where code and context are silent, take the most realistic worst case and
  say so in the justification.

## Step 1: no real finding

Set both labels to `INFORMATION` when:

- the weakness does not exist in the code;
- the code is unreachable or dead (no path from an attacker-accessible entry point);
- the code is test-only, example, fixture, or tooling that is not shipped or deployed;
- the weakness has no confidentiality, integrity, or availability consequence.

Real issue with no impact at the vulnerable and subsequent systems: Impact `INFORMATION`. Real impact with
no realistic attacker path: Exploitability `INFORMATION`.

## Step 2: Base metrics

**Attack Vector (AV)**: N network (incl. the internet), A adjacent (same local network or shared
medium), L local (console, SSH, or a victim running a local file), P physical. If it can be
launched from outside the adjacent domain, use N. Take AV from the code as if the component were
exposed: an HTTP handler or message consumer is N, a CLI argument or local file parse is L.

**Attack Complexity (AC)**: L no target-specific circumvention needed. H the attack must evade
exploit mitigations or obtain a per-target secret that reconnaissance cannot find. Not about
time, attempts, skill, or authentication.

**Attack Requirements (AT)**: N works in all or most instances. P depends on conditions the
attacker does not control (winning a race, being on-path).

**Privileges Required (PR)**: N unauthenticated; also hard-coded or default credentials, and
attacks that trick a user (reflected XSS, CSRF). L basic privileges limited to one user's own
resources. H administrative or significant control. Free self-service sign-up gives no extra
privilege.

**User Interaction (UI)**: N none. P passive and involuntary (a victim loads a page with stored
XSS). A active and conscious (imports a crafted file, dismisses a warning).

**Impact metrics C, I, A** (VC/VI/VA for the vulnerable system, SC/SI/SA for subsequent systems).
Score the final outcome and only the gain from exploitation: an attacker who already can read and
gains write gets Integrity impact only.

| | H | L | N |
|---|---|---|---|
| Confidentiality | Total loss, or limited disclosure with serious consequence (admin password, private keys, secrets, bulk sensitive data) | Some restricted information, little control over which, or not seriously harmful | No loss |
| Integrity | Total loss, or limited modification with serious consequence (code or config, privileged records); repudiation of critical actions | Modification without control over the consequence, or limited amount | No loss |
| Availability | Sustained or persistent full denial, or partial denial with serious consequence | Reduced performance or interruptions, no full denial | No impact |

Vulnerable system: the component of interest plus anything that serves it exclusively (a database
used only by this application). Subsequent system: anything outside it that suffers impact
(another application on the host, a downstream system, a container escape). Default SC/SI/SA to
N; set them only when the code shows a concrete path.

## Step 3: context

No Sigrid system metadata is available to the skill. Assume, and say so in the justification:

- **Public facing**: no attack-vector ceiling, so AV is the code-level value.
- **Business critical**: when the code evidence leaves L versus H open for C, I, or A, choose H.
  Criticality never creates impact from nothing (N stays N) and never overrides clear code
  evidence.

If the profile or the user states the deployment, apply it: the attack vector is the less remote of
the code-level AV and the deployment's (internet-facing N, connected to an internet-facing system
A, internal L, physical P). For software distributed to customers who run it themselves, use the
code-level AV.

## Step 4: lookup tables

Levels are ordered `INFORMATION` < `LOW` < `MEDIUM` < `HIGH` < `CRITICAL`.

**Exploitability**

E1, base level from PR and UI (as if AV:N):

| | UI:N | UI:P | UI:A |
|---|---|---|---|
| PR:N | CRITICAL | HIGH | MEDIUM |
| PR:L | HIGH | MEDIUM | MEDIUM |
| PR:H | MEDIUM | LOW | LOW |

E2, attack vector: move down from the E1 level by AV:N 0, AV:A 1, AV:L 2, AV:P 3.

E3, move down one level if AC:H or AT:P (one level in total, even if both).

E4, floor: never below `LOW` here. `INFORMATION` only comes from Step 1.

**Impact**

I1, level of one system from its C, I, A. First rule that matches:

1. C = H and I = H: `CRITICAL`
2. any of C, I, A = H: `HIGH`
3. two or more of C, I, A = L: `MEDIUM`
4. exactly one = L: `LOW`
5. all N: `INFORMATION`

I2, vulnerable system level (VS): I1 on VC, VI, VA.

I3, subsequent system level (SS): I1 on SC, SI, SA, then one level down (`LOW` and `INFORMATION` stay).

I4, Impact is the higher of VS and SS. If both are at least `HIGH`, move one level up (cap
`CRITICAL`).

## Worked examples

1. Unauthenticated SQL injection in a public REST endpoint. AV:N, AC:L, AT:N, PR:N, UI:N gives
   Exploitability `CRITICAL`. The attacker reads and modifies the whole database (VC:H, VI:H), so
   Impact `CRITICAL`.
2. Stored XSS on a comments page, normal user account needed. AV:N, PR:L, UI:P gives Exploitability
   `MEDIUM`. The attacker acts in the victim's session within this app (VC:L, VI:L), so Impact
   `MEDIUM`. Deployment defaults were assumed and the evidence limits the damage, so the L values
   stand.
3. Path traversal in a file-download handler, internal deployment stated. Code AV:N, deployment L,
   so AV:L. PR:L, UI:N gives `HIGH`, minus 2 for AV:L, so Exploitability `LOW`. It reads arbitrary
   files, but the data is not clearly sensitive, so VC:L and Impact `LOW`.
4. Hard-coded password in a unit-test fixture that is never packaged: both `INFORMATION` (test-only code).

## Justification

2 to 5 sentences, free text. State what the flaw is and how an attacker reaches it (entry point,
privileges, user interaction); the main reason for each label; any stated context that shaped the
result; and every assumption made, including that the default deployment and criticality were
assumed. No CVSS score, vector string, overall severity, or lists of metric values.
