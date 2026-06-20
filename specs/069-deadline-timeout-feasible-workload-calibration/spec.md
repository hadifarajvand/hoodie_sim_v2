# Feature 069 - Deadline/Timeout Feasible Workload Calibration

## Goal

Calibrate the generated workload and deadline envelope so the simulator is feasible enough for later learning experiments while remaining nontrivial.

## Scope

- Keep reward semantics unchanged.
- Keep policy semantics unchanged.
- Keep state representation unchanged.
- Keep the calibration explicit and documented.
- Compare the calibrated 50 and 100 episode checkpoints against the Feature 068 baseline.

## Success Criteria

- Overall feasible ratio becomes nonzero and meaningful.
- Local, horizontal, and vertical action paths each have feasible tasks.
- At least one fixed policy completes at least one task.
- The calibration remains nontrivial; it does not trivialize the workload into all-complete or all-drop behavior.

