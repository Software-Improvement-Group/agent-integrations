# Marking a directory as utility in `sigrid.yaml`

Only for architecture: when a directory serves a utility role but its name doesn't match Sigrid's
utility pattern (`architecture-graph.md`), propose marking it in `sigrid.yaml`, the scope file.

## Location

`sigrid.yaml` lives at the profile's source root (default: the repository root). If one doesn't
exist yet, create it there. If one already exists, add to it — never overwrite existing entries.

## Entry

```yaml
architecture:
  component_roles:
    - role: utility
      include:
        - "<regex matching component path>"
```

- `include` patterns are regexes matched against Sigrid component paths.
- The role is inherited by all child components.
- Utility components skip Component Coupling and Component Adjacency scoring, and edges to them
  don't count toward other components' coupling.
