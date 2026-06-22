# Checkpoint / Resume Plan

- Cadence: every 250 episodes
- Path: `artifacts/production/full-paper-campaign-run/checkpoints/ckpt_ep{episode:05d}.pt`

## Checkpoint contents
- online_network.state_dict()
- target_network.state_dict()
- optimizer.state_dict() (Adam moments)
- cumulative_training_episode_count
- optimizer_step_count
- target_sync_count
- exploration RNG state + cumulative episode index (for epsilon schedule)
- replay buffer snapshot (optional; deterministic re-fill also acceptable)
- seed bundle (training/eval trace generation, replay sampling)

## Resume protocol
1. Locate the highest-numbered ckpt_ep*.pt.
2. Load all four state_dicts and counters; restore exploration episode index.
3. Resume train_to_budget from cumulative_training_episode_count to N_E=5000.
4. Epsilon is a pure function of the cumulative episode index, so resume is exact.
5. Re-anchor the eval trace bank by seed (disjoint from training bank).

_Determinism:_ All seeds are fixed; epsilon is episode-indexed; target sync is episode-indexed. Resume reproduces the same trajectory as an uninterrupted run if replay is snapshotted; if replay is re-filled, minor sampling drift is possible but schedule/sync stay exact.