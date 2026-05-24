# SpecKit Workflow Reference

This directory is the repository-level reference for how we run SpecKit in this project. Future ChatGPT/Codex conversations should point here instead of rebuilding the same operating rules from memory.

The purpose is simple: keep feature work fast, bundled, auditable, and free of recurring dirty-worktree failures.

## Files

- `operating-contract.md` — non-negotiable project rules for every SpecKit feature.
- `phase-prompts.md` — compact prompt templates for each SpecKit command.
- `command-matrix.md` — which command to run, when to run it, what it must produce, and what must block.
- `severity-policy.md` — which analyzer findings block implementation and which should not waste another loop.
- `dirty-path-policy.md` — exact handling for `.specify/feature.json`, `AGENTS.md`, prior artifacts, staging, commit, and push.

## How to use in future conversations

Start future implementation conversations with this reference:

```text
Use the repository SpecKit workflow reference in docs/spec-kit-workflow/ as the operating contract for this feature.
Do not repeat the full hygiene rules unless the feature deviates from them.
```

Then provide only the feature-specific purpose, expected artifacts, allowed paths, and report verdict logic.

## Core principle

SpecKit should be a controlled pipeline, not a manual bureaucracy loop:

```text
/speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.analyze -> /speckit.implement
```

Only block on real contract, scope, artifact, or validation failures. Do not burn cycles on low-value cosmetic duplicates unless they can produce schema/test drift.
