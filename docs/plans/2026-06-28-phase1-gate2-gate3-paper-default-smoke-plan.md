# Phase 1 — Gate 2 and Gate 3: paper_default Config and Smoke Campaign

## 1. Completed Prerequisites

| Gate | Status | Evidence |
|------|--------|----------|
| Gate 4A (simplified 3D/3A campaign viability) | ✅ Complete | Config dimension locks removed |
| Gate 4B (replay/trainer dimension layer for 74D/22A) | ✅ Complete | Replay, state window, mask tests pass |
| Gate 4C (network and CampaignPolicy for 22 actions) | ✅ Complete | Network output shape 22, policy mask 22 |
| Gate 4D (real PaperStateBuilder output wired) | ✅ Complete | 64/64 tests pass, HEAD `4e700cf` |

All four prereq gates are committed to local `main`.

## 2. Why paper_default Is Now Allowed

- Gate 4A removed dimension hard-locks (`state_dim`, `action_count` can be 74 and 22).
- Gate 4B confirmed the replay/trainer layer correctly handles 74D state windows and 22A masks.
- Gate 4C confirmed the network and `CampaignPolicy` accept `action_count=22`.
- Gate 4D confirmed real `PaperStateBuilder` output is wired into the campaign paper path.
- All required unit and integration tests pass.
- The infrastructure is now ready to create a paper-dimension config and smoke-test it.

## 3. paper_default Config Requirements

```yaml
state_dim: 74
action_count: 22
lookback_w: 10
horizontal_data_rate_mbps: 30.0
vertical_data_rate_mbps: 10.0
learning_rate: 7e-7
batch_size: 64
replay_memory_capacity: 10000
gamma: 0.99
q_network_hidden_layers: [1024, 1024, 1024]
lstm_num_layers: 1
lstm_hidden_size: 20
model_initialization_seed: 19
pilot_episode_length: 50           # Bounded smoke slot count
evaluation_episode_length: 50       # Bounded smoke slot count
full_campaign_episode_length: 110   # Unchanged paper default
readiness_probe_episode_count: 3    # Bounded smoke-only episode count
readiness_probe_episode_length: 50  # Bounded smoke slot count
full_campaign_enabled: false
readiness_manual_approval_required: true
readiness_manual_approval_status: "approved"
pilot_budget: { primary_episodes: 10, follow_up_episodes: 25 }
seed_bundle: default
```

Implementation: a `@staticmethod paper_default()` factory on `CampaignConfig` (in `src/analysis/full_training_reproduction_campaign/config.py`) returning a config with the above values.

## 4. Exact Allowed Files for Gate 2 Implementation

| File | Change |
|------|--------|
| `src/analysis/full_training_reproduction_campaign/config.py` | Add `@staticmethod paper_default()` factory returning paper-dimension config |
| `tests/unit/test_paper_default_campaign_config.py` (new) | Unit tests for paper_default factory values, field types, and smoke bounds |
| `docs/run-logs/2026-06-28-phase1-gate2.md` (new) | Gate 2 closure run log |

## 5. Exact Allowed Files for Gate 3 Implementation

| File | Change |
|------|--------|
| `tests/integration/test_paper_default_smoke_campaign.py` (new) | Integration test: instantiate trainer with paper_default config, run bounded episode, verify no crash/NaN |
| `docs/run-logs/2026-06-28-phase1-gate3.md` (new) | Gate 3 closure run log |

Optional (if needed for validation):
| File | Change |
|------|--------|
| `src/analysis/full_training_reproduction_campaign/runner.py` | Add `run_paper_default_smoke()` entry point if direct test is insufficient |

## 6. Smoke Campaign Constraints

- **Smoke only**: max 3 episodes, 50 slots each.
- **No full training**: `full_campaign_enabled` must stay `False`.
- **No figure reproduction**: baseline comparison, paper reproduction claim, and figure pipelines must not run.
- **No Phase 2**: LSTM component, DCQ-MADRL, and Phase 2 tasks must not be started.
- **Expected artifacts**: JSON + Markdown report confirming smoke pass/fail.

## 7. Expected Smoke Artifacts

```
artifacts/analysis/paper-default-smoke-campaign/
├── paper-default-smoke-campaign-report.json
└── paper-default-smoke-campaign-report.md
```

Report contains:
- `feature_id`: "045-paper-default-smoke-campaign" (or similar)
- `final_verdict`: "paper_default_smoke_passed" or failure reason
- `config`: copy of paper_default CampaignConfig
- `smoke_run_summary`: episode count, steps per episode, total steps, success
- `engine_errors`: empty list on pass

## 8. Validation Commands

```bash
# Gate 2 validation
python -m pytest tests/unit/test_paper_default_campaign_config.py -v

# Gate 3 validation
python -m pytest tests/integration/test_paper_default_smoke_campaign.py -v

# Full regression
python -m pytest tests/unit/test_paper_default_campaign_config.py tests/integration/test_paper_default_smoke_campaign.py -v

# Verify no regression (optional, if confident)
python -m pytest tests/unit/ -v --tb=short -x
```

## 9. Stop Conditions

- Any validation test fails → stop, report, fix before proceeding.
- Config values mismatch spec → stop, correct values.
- Smoke campaign exceeds 3 episodes or 50 slots → stop, bounded constraint violated.
- Smoke campaign produces NaN/Inf in engine → stop, report engine bug.
- Smoke campaign produces full training artifacts → stop, scope violation.

## 10. Rollback Strategy

| Action | Command |
|--------|---------|
| Revert Gate 2 | `git revert <commit-sha>` for Gate 2 commit |
| Revert Gate 3 | `git revert <commit-sha>` for Gate 3 commit |
| Clean working tree | `git checkout -- <file>` for dirty files |
| Throwaway smoke artifacts | `rm -rf artifacts/analysis/paper-default-smoke-campaign/` |

## 11. Acceptance Criteria

| # | Criteria | How to Verify |
|---|----------|---------------|
| 1 | `CampaignConfig.paper_default()` returns a config with state_dim=74 | Unit test asserts |
| 2 | Config has action_count=22 | Unit test asserts |
| 3 | Config bounded to smoke-only episode count/slot count | Unit test asserts full_campaign_enabled=False, episode lengths ≤ 50 |
| 4 | Config passes __post_init__ validation | Construction does not raise ValueError |
| 5 | Smoke campaign test instantiates trainer | Integration test runs without ImportError/TypeError |
| 6 | Smoke campaign test runs n bounded episodes | Integration test verifies transition_count matches expectation |
| 7 | Smoke campaign produces no NaN/Inf | Integration test checks loss/reward for NaN |
| 8 | Smoke artifacts contain pass verdict | JSON report final_verdict == "paper_default_smoke_passed" |
| 9 | No regression in existing tests | All prior Gate 4 tests still pass |

## 12. Decision: Implement Gate 2 and Gate 3 Together or Separately

**Together**, executed sequentially in a single implementation session:

1. Add `CampaignConfig.paper_default()` factory → commit ✅ (Gate 2)
2. Add smoke campaign integration test → commit ✅ (Gate 3)

Rationale:
- Gate 3 depends on Gate 2 (cannot smoke-test a config that doesn't exist).
- Both are small, well-scoped changes (one file each + tests).
- A single planning document and validation pass reduces context-switching overhead.
- Rollback is independent: each commit can be reverted separately.
