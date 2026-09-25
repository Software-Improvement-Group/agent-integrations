# Sigrid profile

This file captures how this repository is set up in Sigrid and the team's conventions, so the Axis
skills produce guidance specific to this repo instead of generic output. It lives at
`.sigrid/profile.md` in the repository root and is committed, so everyone working in the repo shares
it. Write it with `/axis:setup` or edit it by hand.

**Persist what gets resolved.** This profile is the single source of truth for every setting it
covers. Whenever a skill establishes such a setting during a run, by asking or from a value the user
states inline, it writes that value back here before continuing. The next run then resolves
silently. The write is additive: never overwrite a populated field with a different value without
confirming, and never write the Sigrid token here.

---

## Sigrid system

Both values appear in the Sigrid URL: `sigrid-says.com/<customer>/<system>`.

- **Customer**: <lowercase alphanumeric, min 2 chars>
- **System**: <lowercase alphanumeric segments separated by hyphens>
- **Baseline branch**: <the branch Sigrid analyses, e.g. `main`; used for branching off and CI verification>
- **Source root**: <the system's root in Sigrid, relative to the repository root, e.g. `.`>

## Branches

- **Branch naming**: <the pattern for branches autofix creates, e.g. `fix/<area>`; blank to leave it to autofix>

## Findings models

- **Security model**: <e.g. `ow10`, `sigsec`, `pci4`, `owasvs4c`, or blank for the default (OWASP Top-10)>
- **Reliability model**: <`sigrel`, `5055rel`, or blank for the default (SIG Code Reliability Top-10)>

## Customizing behavior

Beyond the settings above, describe in plain language how the skills should behave in this repo.
There is no fixed schema; the skills read this and take it into account. For example: off-limits
code, commit message conventions.
