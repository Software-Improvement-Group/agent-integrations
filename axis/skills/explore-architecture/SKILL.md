---
name: explore-architecture
disable-model-invocation: true
argument-hint: "[question about the codebase structure]"
description: >
  Explore the codebase structure with the architecture-explorer agent, which combines Sigrid's
  measured dependency graph with file reading. Use for "explore this codebase", "show me the
  architecture", "where is X used", "what does this directory depend on".
---

# Explore Architecture

Hand the user's question (`$ARGUMENTS`, or "give an overview of the codebase structure" if empty)
to the `architecture-explorer` agent and relay its answer.
