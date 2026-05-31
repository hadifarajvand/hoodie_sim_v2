# Validation Rules

- Required policy/method coverage must include all seven IDs from Feature 076.
- Required scenario coverage must include all seven IDs from Feature 076.
- Seed count must be greater than zero.
- Workload levels must be complete and limited to `low`, `medium`, `high`.
- Deadline pressure levels must be complete and limited to `relaxed`, `moderate`, `tight`.
- Topology mode must equal `paper_figure_7`.
- Runtime mode must equal `paper`.
- `compatibility_mode_used` must remain `False`.
- No execution artifacts may be created.
- No final claims may be made.
- Feature 076 must pass before Feature 077 is considered ready.
- No `src/**` edits are allowed during the Spec Kit-only phase.
- No `tests/**` edits are allowed during the Spec Kit-only phase.
- No `artifacts/**` edits are allowed.
- No `resources/**` edits are allowed.
- No dependency files may be edited.
- No lock files may be edited.
