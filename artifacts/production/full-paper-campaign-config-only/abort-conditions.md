# Abort Conditions

- **loss becomes NaN/Inf** → abort; inspect td-target-loss; do not continue
- **reward_reconciled or terminal_reconciled becomes false at any checkpoint** → abort; reconciliation regression must be root-caused before resuming
- **raw_vs_canonical_reward_delta != 0** → abort; reward accounting corrupted
- **terminal_event_coverage_ratio < 1.0** → abort; horizon recovery incomplete
- **wall-clock exceeds 2x upper estimate (~ >9h)** → pause; profile per-episode cost
- **checkpoint write fails / disk full** → abort; free storage, resume from last good ckpt
- **epsilon not reaching 0 by episode 2500** → abort; schedule misconfigured