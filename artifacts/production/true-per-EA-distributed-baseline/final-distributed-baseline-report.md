# Per-EA Distributed Baseline — Report

- **Verdict:** `true_per_EA_distributed_full_campaign_completed` | Next: `prepare_paper_output_report`
- Mode: full | Executed 5000: True | Proposed method: NONE
- Runtime commit: `8ed90e6e7d8697d7f99cee51079cc019d8151bf4` | Results commit: `8ed90e6e7d8697d7f99cee51079cc019d8151bf4`

## Distributed candidate vs comparators (final)
- Distributed final: 0.221 compl / -28.07 rwd
- Distributed best: 0.295 compl / -25.66 rwd
- Shared-parameter final completion: 0.2545454545454545
- fixed_local: 0.246 compl / -28.99 rwd
- capacity_split: 0.257 compl / -28.64 rwd
- random_legal: 0.243 compl / -29.11 rwd

## Learning health
- **Mixed behavior emerged during training:** True (horizontal and vertical both used across checkpoints)
- **Final policy vertical-dominant:** True (final aggregate greedy: L=0, H=0, V=1.0)
- **Final balanced mixed policy:** False (final is 100% vertical, not balanced H/V/L)
- **Local dominance reduced vs shared:** True (distributed=0% local vs shared=local-dominant in final)
- **Distributed underperformed shared on completion:** True (-0.033 delta, 0.2214 vs 0.2545)
- **Distributed underperformed capacity_split on completion:** True (-0.036 delta, 0.2214 vs 0.2572)
- Per-agent learning: 18/20 agents chose local when available; 2 chose vertical (per-EA autonomy observed)

## Reconciliation
- Reconciled all: True | delta max: 0.0

## Claim safety
- No paper-reproduction / exact-numerical / performance / baseline-superiority claims; no proposed method.