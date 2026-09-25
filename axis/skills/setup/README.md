# Setup

> **Run this first in each repository.** Every other Axis skill reads the profile this one writes.

Detects the repo's Sigrid system from `sigrid.yaml` or the Sigrid CI pipeline and the branch naming
from existing branches, asks for anything it can't tell and for behavior preferences, and writes the
result to `.sigrid/profile.md` at the repository root. Commit that file so the whole team shares it.
Re-run setup to change conventions, or edit the file by hand.

If you used the per-user profile from earlier versions
(`~/.claude/plugins/data/sigrid-*/CLAUDE.md`), setup offers to copy the matching system from it.

```
/axis:setup
```

## Note

Setup only writes the profile. It never touches project code, calls the Sigrid MCP, or stores your
API token. The MCP token lives in the OS keychain; `change-feedback` reads a separate
`SIGRID_CI_TOKEN` environment variable.
