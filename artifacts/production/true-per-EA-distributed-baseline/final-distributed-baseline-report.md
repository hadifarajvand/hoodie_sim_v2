# Per-EA Distributed Baseline — Report

- **Verdict:** `true_per_EA_distributed_baseline_ready_for_full_campaign`  | Next: `prepare_paper-output-report`
- Mode: full | Executed 5000: True | Proposed method: NONE

## Distributed candidate vs comparators (final)
- Distributed final: 0.221 compl / -28.07 rwd
- Distributed best: 0.295 compl / -25.66 rwd
- Shared-parameter final completion: 0.2545454545454545
- fixed_local: 0.246 compl / -28.99 rwd
- capacity_split: 0.257 compl / -28.64 rwd
- random_legal: 0.243 compl / -29.11 rwd

## Learning health
- Local-dominant: False | distinct dominant signatures: 2
- Horizontal used: True | Vertical used: True
- Mixed behavior emerged across checkpoints/agents: True (vertical observed during smoke: True)
- Final aggregate greedy policy horizontal-dominant: False | final balanced H/V/L mix: False | vertical usage final: True
- Distributed vs shared (completion): -0.033129846559973586
- Distributed vs capacity_split (completion): -0.035795243989768966

## Reconciliation
- Reconciled all: True | delta max: 0.0

## Claim safety
- No paper-reproduction / exact-numerical / performance / baseline-superiority claims; no proposed method.