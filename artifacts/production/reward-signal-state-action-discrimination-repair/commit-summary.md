# Commit summary

fix: repair reward signal and state-action discrimination

- Root cause: per-step aggregate reward mis-attributed to single decision broke credit assignment.
- Fix: per-task delayed-reward credit assignment (paper Algorithm 1 lines 20-21), training-only.
- Raw reward semantics, environment, and dependencies unchanged; reconciliation still passes.
