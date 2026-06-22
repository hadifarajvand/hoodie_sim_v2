# Remaining Approximations

## Shared-parameter trainer vs paper per-EA distributed models
- **Paper design:** HOODIE is distributed multi-agent: each of the N=20 EAs runs its own DRL model (theta_n), trained on its own local task traffic; agents do not share parameters and do not know other agents' decisions (paper lines 99, 401, 405, 587). Inference deploys N separate Q-models.
- **Repo implementation:** A single shared-parameter trainer (one online + one target network) selects for whichever EA's task is current. This is a centralized shared-policy approximation of the paper's per-EA distributed models.
- **Status:** `known_approximation_not_repaired`
- **Impact:** A shared policy averaged over 20 heterogeneous EAs (different topology positions/neighbors) tends toward a generic policy and cannot personalize per-EA load-spreading the way per-EA models can. This is the leading candidate explanation for residual local-collapse beyond training budget.
- **Implication for the full campaign:** Running N_E=5000 on the shared-parameter trainer tests the shared-policy ceiling, NOT the paper's per-EA distributed ceiling. If the shared agent still underperforms the capacity-split oracle after 5000, the next step is a per-EA distributed trainer (20 models), each trained to its own N_E.

**Will the full 5000 campaign test a true per-EA distributed fleet?** No. It tests the current single shared-parameter implementation only. A true per-EA distributed fleet (N=20 independent models) is not implemented and is out of scope for this config-only branch.