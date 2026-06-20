# Feature 068 - Completion Path and Deadline Feasibility Repair

## Goal

Diagnose why completion remains at zero after Feature 067 even though terminal and reward reconciliation now pass.

## Scope

- Use the accepted Feature 067 branch as the base.
- Keep training lightweight: budgets `[50, 100]` only.
- Do not modify reward semantics, policy semantics, or state representation.
- Do not run 5000 episodes.
- Produce feasibility and runtime-path diagnostics that distinguish infeasible workloads from runtime capture bugs.

## Required outputs

- Feasibility summary for tasks and actions.
- Runtime event-path audit for candidate and fixed policies.
- 50 vs 100 comparison of completion, drop, latency, and reward metrics.
- Diagnostic decision identifying the next repair target.

## Acceptance criteria

- The report explicitly states whether all tasks are infeasible under the current deadline envelope.
- The report explicitly states whether the completion path is blocked by deadline/timeout configuration or by runtime capture.
- The report does not claim model superiority or paper reproduction.
- The report stays inside the approved 068 scope.
