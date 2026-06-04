# System Model Gap Matrix: HOODIE Paper vs Simulator

Status values: `exact`, `approximate_documented`, `missing`, `wrong`, `not_exercised`.

| Mechanism | Expected Simulator Behavior | Code/Artifact Evidence | Status | Required Fix / Evidence |
|---|---|---|---|---|
| Three-tier topology | Represent task source/IoT or MD layer, edge agents, and cloud | runtime config/model/scenarios | approximate_documented | Verify explicit representation and document simplifications. |
| Edge Agent set | Multiple EAs can compute locally and receive offloaded work | runtime model/config | approximate_documented | Add mechanism coverage evidence for local EA and remote EA behavior. |
| Cloud node | Cloud accepts vertical offloaded tasks | runtime scenarios/model | approximate_documented | Add vertical/cloud path evidence. |
| Horizontal connectivity | Legal EA-to-EA destinations constrained by topology or legality model | runtime model/scenarios | approximate_documented | Make adjacency/legality explicit or document existing legality model. |
| Vertical connectivity | EA-to-cloud path modeled | runtime model/scenarios | approximate_documented | Add cloud transmission/execution evidence. |
| Task ID | Each task is traceable through lifecycle | raw rows/model | approximate_documented | Verify stable task IDs in raw rows. |
| Task size/data | Data size contributes to transmission/execution where modeled | runtime model | approximate_documented | Verify unit and formula mapping. |
| CPU demand/density | Execution delay depends on compute demand/capacity | runtime model | approximate_documented | Verify computation delay formula. |
| Timeout/deadline | Completion beyond deadline causes timeout/drop where modeled | runner/scenarios/metrics | approximate_documented | Add timeout/drop evidence. |
| Workload arrivals | Workload matches paper or deterministic approximation is documented | scenarios | approximate_documented | Document deterministic approximation if no stochastic generator. |
| Private queue | Local tasks wait/execute in local/private queue | queue timing/model | approximate_documented | Add queue timing evidence. |
| Offloading queue | Offloaded tasks have offload path timing/queue effect | queue timing/model | approximate_documented | Add offloading queue evidence. |
| Public/cloud queue | Public/cloud path has queue/capacity effect | queue timing/model | approximate_documented | Add cloud/public queue evidence. |
| Local delay | Completion includes local wait and execution delay | runner/model/metrics | approximate_documented | Assert decomposition in tests/artifacts. |
| Horizontal transmission delay | Horizontal offload includes transmission delay | runner/model | approximate_documented | Assert horizontal delay contribution. |
| Vertical transmission delay | Cloud offload includes transmission delay | runner/model | approximate_documented | Assert vertical delay contribution. |
| Remote/cloud execution delay | Remote destination contributes execution time | runner/model | approximate_documented | Add remote/cloud execution evidence. |
| Waiting time | Queue waiting is nonnegative and contributes to completion | runner/model | approximate_documented | Add evidence for nonnegative waiting and queue accumulation. |
| Completion time | Metric uses paper-compatible completed-task delay semantics | metrics/runner | approximate_documented | Verify denominator and filtering. |
| Drop behavior | Timeout/unavailable/deadline drops are counted | metrics/scenarios | approximate_documented | Add scenario coverage for represented drop types. |
| Hybrid actions | local/horizontal/vertical candidates/actions exist | policies/runner | approximate_documented | Add action coverage artifact. |
| Two-stage decision boundary | Local-vs-offload and destination selection represented or documented | proposed-method/runtime | approximate_documented | Document if runtime collapses into single action choice. |
| HOODIE method | HOODIE is the only proposed method | Feature 080/085 runtime | approximate_documented | Preserve interface/training claim boundary. |
| Baselines | RO, FLC, VO, HO, BCO, MLEO only | policy registry/artifacts | exact | Keep invalid-label tests. |
| MLEO | Select minimum estimated total latency, not queue length | `src/policies/mleo.py` and adapter | not_exercised | Add numeric non-queue-only test. |
| Reward/cost | Reward follows paper or documented approximation | reward/runtime/report | approximate_documented | Verify coefficients/sign/signature. |
| Output metrics | Metrics classified for paper comparison or diagnostics | report/artifacts | approximate_documented | Add metric readiness matrix. |
| LSTM/forecast | Trained forecast only claimed if actually implemented | Feature 080 components | approximate_documented | Keep interface-only boundary unless trained implementation exists. |
| Paper figures/results | Figure reproduction only claimed if generated from matching setup | artifacts/report | missing | Keep for later output-comparison phase unless implemented here. |
