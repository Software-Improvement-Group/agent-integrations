---
name: explore-architecture
disable-model-invocation: true
argument-hint: "[question about the codebase structure]"
description: >
  Explore the codebase structure with Sigrid's measured dependency graph and the
  architecture-explorer agent. Use for "explore this codebase", "show me the 
  architecture", "what does this directory/file depend on"
---

# Explore Architecture

Hand the user's question (`$ARGUMENTS`, or "give an overview of the codebase structure" if empty)
to the `architecture-explorer` agent and relay its answer. If your tool has no such agent, answer it
yourself by combining the Sigrid architecture MCP tools with reading the files they point to.
