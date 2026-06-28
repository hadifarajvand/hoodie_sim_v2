# Decisions

## Orchestration Boundary

- Ruflo is the active conductor for memory, swarm coordination, and decision capture.
- Graphify is the repository intelligence map.
- OpenCode is the cockpit.
- MCPs are controlled tools.
- ECC remains inactive/passive reference only.

## Setup Status

- Project-local OpenCode config already contains the Ruflo MCP entry and `ask` permissions for `edit` and `bash`.
- Ruflo CLI access is blocked in this environment because `npx ruflo@latest ...` cannot reach `registry.npmjs.org`.
- Ruflo memory seeding is deferred until the MCP backend is reachable.

## Phase Ordering

- Phase 0 remains read-only baseline fidelity verification.
- No simulator source implementation starts before approval.
- One integrator edits only during implementation phases.
- Specialist agents inspect and propose only.
