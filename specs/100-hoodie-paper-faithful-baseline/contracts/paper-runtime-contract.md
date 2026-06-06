# Paper Runtime Contract

The simulator runtime must be slot-based and must separate action slots from drain slots.

## Required Lifecycle Order

1. Arrivals
2. Action selection
3. Local/private queue insertion
4. Offloading queue insertion
5. Transmission
6. Public queue insertion
7. Processing
8. Completion
9. Timeout/drop
10. Reward attribution
11. Drain phase processing

## Contract Requirements

- arrivals are generated only in action slots
- no new arrivals are generated during drain slots
- pending work continues during drain slots
- completion and timeout must be separately observable
- reward attribution must be traceable back to the originating task and action

