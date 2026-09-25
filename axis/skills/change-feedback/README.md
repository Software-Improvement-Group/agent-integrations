# Change Feedback

Sigrid's verdict on local changes before you commit or push.

```
/axis:change-feedback [maintainability|architecture|open-source|security]
```

With no argument it runs maintainability, open-source, and security.

- **Maintainability, open-source, security**: runs Sigrid CI locally on the working tree.
- **Architecture**: finds new cross-directory references in the diff (default: against the
  baseline branch) and checks each against Sigrid's measured dependency graph. A reference that
  matches an existing edge is clean. One that adds a dependency, closes a cycle, or bypasses a
  facade is drift, reported with the files it should route through instead.

## Prerequisites

- Customer and system in `.sigrid/profile.md` (`/axis:setup`), or stated in the prompt
- For the Sigrid CI models:
  - `SIGRID_CI_TOKEN` or `SIGRID_TOKEN` environment variable
  - Python 3.7+
  - Network access to `github.com` to clone the sigridci scripts, or a local clone named in your
    prompt
  - Network access to `sigrid-says.com`
