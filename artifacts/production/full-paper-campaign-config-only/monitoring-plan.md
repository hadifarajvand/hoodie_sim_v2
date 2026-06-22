# Monitoring Plan

- **progress_log**: tail -f artifacts/production/full-paper-campaign-run/progress.jsonl
- **watch_loss_and_epsilon**: Monitor: each checkpoint row should report loss_is_finite=true and the episode-indexed epsilon (1.0 at ep0 -> 0.0 at ep2500 -> 0.0 after).
- **watch_action_distribution**: Per-checkpoint candidate eval action_distribution should begin to spread from pure-local toward a mix as epsilon decays past ~ep2500.
- **watch_reconciliation**: Every candidate/baseline row must keep reward_reconciled=true, terminal_reconciled=true, raw_vs_canonical_delta=0, coverage=1.0.
## suggested_commands
- `grep -c 'checkpoint_written' artifacts/production/full-paper-campaign-run/progress.jsonl`
- `python -m src.analysis.paper_faithful_simulation_production.runner --json  # schema check on latest metrics`