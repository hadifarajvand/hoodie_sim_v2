# Commit summary

fix: repair reward signal and state-action discrimination

- Root cause: per-step aggregate reward mis-attributed to single decision broke credit assignment.
- Fix: per-task delayed-reward credit assignment (paper Algorithm 1 lines 20-21), training-only.
- Raw reward semantics, environment, and dependencies unchanged; reconciliation still passes.

## Lineage
- Base branch: training-stability-exploration-repair
- Base SHA: d374f37a1c1f51cd5ec189f313a16c2ea4bbf8e9
- Repair commit (HEAD, embedded in artifacts): 5a045150ef00caa9c0d2a63fd7cf46315594776a
