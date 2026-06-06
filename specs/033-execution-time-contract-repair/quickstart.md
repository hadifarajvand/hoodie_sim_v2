# Quickstart: Execution-Time Contract Repair

1. Confirm the active branch is `034-execution-time-contract-repair`.
2. Run the targeted execution tests for the environment and execution helper.
3. Verify a task requiring more than capacity spans multiple slots.
4. Verify timeout/drop still resolves after execution progress.
5. Verify reward is emitted only at terminal completion or drop.

## Validation Focus

- Local/private shortcut removed
- Public and cloud execution use the same per-slot accounting rule
- Completion slot semantics are explicit
- Reward timing is unchanged

