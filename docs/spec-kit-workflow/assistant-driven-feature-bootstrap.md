# Assistant Driven Feature Bootstrap

Future feature setup should be prepared in the repository first when it is safe.

## Purpose

The workflow should reduce repeated manual setup. Safe branch checks, spec scaffolding, workflow reference updates, and remote validation should happen through the repository connector when possible.

## Default workflow

For a clear new feature, prepare the remote branch and safe spec files first. Then provide the user with the local sync step and the next SpecKit command prompt.

For workflow hardening, update the repository workflow reference files directly.

For implementation code, prefer the local SpecKit implementation phase unless the user explicitly requests remote source changes.

## Safe remote scope

Normal feature scaffolding may include files under `specs/`.

Workflow scaffolding may include files under `docs/spec-kit-workflow/`.

## Output after preparation

Report the branch name, prepared files, local sync step, next SpecKit command, and compact prompt.

## Current project rule

`.specify/feature.json` is ignored and local-only. `AGENTS.md` is stable repository policy. Normal feature work should not require repeated cleanup of either file.
