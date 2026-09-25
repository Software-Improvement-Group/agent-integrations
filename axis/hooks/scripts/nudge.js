#!/usr/bin/env node
// UserPromptSubmit hook: adds the context of every nudge whose plugin option
// is enabled.
const fs = require("fs");
const nudges = require("./nudges.json");

function isEnabled(option) {
  const envVar = `CLAUDE_PLUGIN_OPTION_${option.toUpperCase()}`;
  return process.env[envVar] !== "false";
}

function enabledNudgesContext() {
  return Object.entries(nudges)
    .filter(([option]) => isEnabled(option))
    .map(([, lines]) => lines.join("\n"))
    .join("\n\n");
}

function addPromptContext(context) {
  const output = {
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: context,
    },
  };
  fs.writeSync(1, JSON.stringify(output) + "\n");
}

function main() {
  const context = enabledNudgesContext();
  if (context) addPromptContext(context);
}

main();
