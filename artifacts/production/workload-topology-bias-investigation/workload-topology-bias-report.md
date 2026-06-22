# Workload / Topology Bias Investigation

**Verdict:** `local_dominance_is_genuine_paper_faithful_consequence`
**Parameter repair needed:** False
**Recommended next step:** `inspect_algorithm_fidelity_against_paper`

## Parameter fidelity (vs Table 4)
- All Table 4 parameters match implementation: **True**
- R_H > R_V constraint holds: **True**
- Adjacency G: recovered_assumption (20 nodes, 30 edges, degree 3)

## Capacity / feasibility
- Offered load: 10.39 Gcycle/slot
- Capacity: private=10.0, public=10.0, cloud=3.0 Gcycle/slot

| strategy | utilisation | best-case delay (slots) |
|---|---|---|
| fixed_local | 103.9% | 3 |
| fixed_horizontal | 103.9% | 5 |
| fixed_vertical | 346.5% | 5 |
| mixed_balanced | 45.2% | n/a |

- Predicted pure ordering (best→worst): ['local', 'horizontal', 'vertical']
- Measured pure ordering (best→worst): ['local', 'horizontal', 'vertical']
- Predicted matches measured: **True**

## Conclusion
NONE — task-size H, density rho, link rates R_H/R_V, CPU frequencies, and adjacency degree all match Table 4. fixed_local saturates the private pool (util ~104%), public is equal-capacity but pays transmission + degree-3 contention, and cloud is a single 3 Gcycle/slot pool (util ~347%). A MIXED policy is feasible (util ~45%); discovering it is a learning/training-budget problem (paper N_E=5000), not a parameter problem.