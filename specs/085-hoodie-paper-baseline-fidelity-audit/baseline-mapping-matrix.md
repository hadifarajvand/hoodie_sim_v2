# Baseline Mapping Matrix — Feature 085

| Paper Baseline | Canonical Policy ID | Meaning | Expected Simulation | Code Location | Status | Required Fix |
|---|---|---|---|---|---|---|
| HOODIE | `HOODIE` | Feature 080 proposed method | Use the proposed-method runtime path | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/analysis/hoodie_proposed_method/` | implemented | none |
| Random Offloader | `RO` | Randomly choose local, vertical, or horizontal offload | Seed-controlled random selection with uniform horizontal destination choice | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/ro.py` | implemented | none |
| Full Local Computing | `FLC` | Execute all tasks locally | Always select the local family when legal | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/flc.py` | implemented | none |
| Vertical Offloader | `VO` | Offload all tasks vertically to cloud | Always select vertical/cloud when legal | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/vo.py` | implemented | none |
| Horizontal Offloader | `HO` | Offload all tasks horizontally | Always select a legal horizontal destination when one exists | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/ho.py` | implemented | none |
| Balanced Cyclic Offloader | `BCO` | Cycle local, vertical, horizontal in balanced order | Repeat the paper-defined family cycle | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/bco.py` | implemented | none |
| Minimum Latency Estimate Offloader | `MLEO` | Select the placement with minimum estimated latency | Rank legal candidates by total estimated delay | `src/analysis/hoodie_runtime_evaluation_runner/policies.py`, `src/policies/mleo.py` | implemented | Replace legacy `MQO` labels with `MLEO` in all audit outputs |
| Legacy `MQO` label | `MQO` | Historical mislabel of the MLEO baseline | Must not appear in active audit outputs | historical outputs only | retired | remove from active artifacts and reports |

## Audit Rule

The active baseline set for Feature 085 is exactly:

- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

`MQO` is a legacy label and must be treated as retired.
