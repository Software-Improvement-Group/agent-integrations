# Sigrid Axis Agent Integrations

A Claude Code plugin marketplace for Sigrid Axis
([documentation](https://docs.sigrid-says.com/integrations/integration-sigrid-mcp.html)). Sigrid Axis
brings Sigrid's analysis to AI coding assistants, agents, and other MCP-based tools:

- *Guardrails*: Sigrid checks the code an assistant writes, so it doesn't introduce security or
  other quality issues.
- *Auto-fix agents*: agents use Sigrid's data to fix existing quality issues at scale.

## The `axis` plugin

The plugin autoconfigures the Sigrid Axis MCP server and ships the auto-fix skills. The bracketed
argument picks the model, and phrasing is flexible: `/axis:change-feedback for security problems`
works too.

| Skill | What it does |
|-------|--------------|
| `/axis:setup` | Writes the repo's Sigrid profile (`.sigrid/profile.md`: customer, system, conventions). **Run this first.** |
| `/axis:change-feedback [maintainability\|architecture\|open-source\|security]` | Sigrid's verdict on local changes before you push: Sigrid CI run locally, or architecture drift against Sigrid's graph |
| `/axis:explore-architecture` | Answers questions about the codebase structure with the `architecture-explorer` agent |
| `/axis:diagnose [maintainability\|architecture]` | Reports the system's state for a metrics-based model and names the one fix most worth making. Never changes code |
| `/axis:triage-findings [security\|reliability\|open-source]` | Goes over a list of findings: false positive, accepted, needs a person, or will fix. Never changes code |
| `/axis:autofix [maintainability\|architecture\|open-source\|security\|reliability]` | Fixes what was planned, as local commits on a branch |

Plan with `diagnose` or `triage-findings`, then fix with `autofix`, straight away or later. The plan
is saved as a handover in `.sigrid/handovers/`. The skills stop at local commits and Sigrid
statuses. Pushing, change requests, and issues are up to you or your pipeline.

### Guardrails nudge

Before Claude reports a task done, the plugin nudges it to run the guardrails check on the
production code it changed and to fix what the change made worse. It's on by default. To turn it
off: `/plugin` → `Installed` → `axis` → `Configure options` → `Nudge to run guardrails`.

## Prerequisites

- [Claude Code](https://claude.ai/code)
- A Sigrid API token ([sigrid-says.com](https://sigrid-says.com))

## Install

1. Add the marketplace:
    ```
    /plugin marketplace add Software-Improvement-Group/agent-integrations
    ```

2. Install the plugin. On first use you're asked for your Sigrid API token, which is stored in
   your system keychain.
    ```
    /plugin install axis@sigrid
    ```

3. Run setup in each repository. It detects your Sigrid system from the repo, asks for what it
   can't tell, and writes `.sigrid/profile.md`. Commit that file so your team shares it.
    ```
    /axis:setup
    ```

4. Enable auto-update: in `/plugin`, go to `Marketplaces` → `sigrid` → `Enable auto-update`.

## Usage

For MCP usage, see the
[Sigrid MCP documentation](https://docs.sigrid-says.com/integrations/integration-sigrid-mcp.html).
Each skill has a `README.md` under [`axis/skills/`](axis/skills/).

## Customization

Run `/axis:setup` or edit `.sigrid/profile.md` by hand. Besides the Sigrid settings, the profile
takes plain-language guidance on how the skills should behave in the repo, such as off-limits code
or commit message conventions.

## Upgrading from the `sigrid` plugin

The plugin is now `axis`, in a new marketplace. Remove the old one, then follow [Install](#install):

```
/plugin uninstall sigrid@sigrid-ai-toolkit
/plugin marketplace remove sigrid-ai-toolkit
```

What changed:

- Skills are called as `/axis:<skill>`.
- The skills stop at local commits and Sigrid statuses. They no longer push, open change requests,
  or create issues.
- The per-user profile is replaced by `.sigrid/profile.md` in each repository. `/axis:setup`
  offers to copy your old one.
- MCP tool permissions in your settings move from `mcp__plugin_sigrid_sigrid__*` to
  `mcp__plugin_axis_axis__*`.
- The hook options are now `Nudge to run guardrails` and `Nudge to use architecture-explorer`. If
  you had turned one off, turn it off again.
