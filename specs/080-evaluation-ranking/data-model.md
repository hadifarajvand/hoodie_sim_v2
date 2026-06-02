# Data Model for Feature 080 — HOODIE Proposed Method Implementation

This file defines all the core data structures needed to implement and track the HOODIE proposed method, strictly aligned with the base paper.

## Entities

- **Task**: unique identifier, size, type, deadline, arrival time
- **Edge Agent (EA)**: node id, queue states, CPU slots, local/offloaded task counts
- **Queues**: private, offloading, public
- **Action**: `[local/offload decision, destination EA]`
- **Reward/Cost**: Phi_priv(t), Phi_pub(t), drop cost C

## Relationships

- Tasks belong to vehicles; vehicles generate tasks per time slot
- EAs hold private and public queues
- Offloaded tasks move between EAs or to cloud

## Notes

- All data fields are aligned for simulation fidelity only; no thesis/DCQ extensions.