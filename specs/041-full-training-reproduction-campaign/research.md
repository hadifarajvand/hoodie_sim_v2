# Research: Full Training/Reproduction Campaign

## Decision 1: Target-Update Unit

- **Decision**: Use `optimizer_step` as the approved target-update unit.
- **Rationale**: This is the most defensible DDQN-style interpretation for the campaign loop and it was explicitly user-approved as a campaign assumption.
- **Alternatives considered**: `environment_step`, `replay_insertion`, and `episode` were rejected because they would couple target sync to a different loop boundary without paper support.

## Decision 2: Readiness Gate

- **Decision**: Full training remains blocked until the readiness probe reports terminal/reward-bearing exposure evidence and a human manually approves progression.
- **Rationale**: The repo has sparse terminal outcomes and no fixed threshold should be invented as a paper fact.
- **Alternatives considered**: A fixed numeric exposure threshold was rejected for the first pass because it would fake precision without enough evidence.

## Decision 3: Campaign Staging

- **Decision**: Support `readiness_probe`, `pilot_training`, and `full_training_candidate`, with a gated `final_reproduction_campaign` outcome only when the evidence supports it.
- **Rationale**: Staging keeps the expensive campaign honest and prevents a blind jump to the paper budget.
- **Alternatives considered**: Immediate 5000-episode training was rejected as reckless and un-auditable.

## Decision 4: Pilot Budget

- **Decision**: Use a first pilot budget of 10 episodes and allow a follow-on 25-episode pilot if the first pilot passes cleanly.
- **Rationale**: A small pilot proves the loop without pretending to settle scientific questions.
- **Alternatives considered**: Larger pilots were rejected because they increase cost before the gate is proven.

## Decision 5: Full-Campaign Budget

- **Decision**: Keep 5000 episodes configurable but executable only behind an explicit command or flag.
- **Rationale**: This preserves the paper default while preventing accidental long training runs.
- **Alternatives considered**: Auto-executing the full budget after pilot was rejected as too risky.

## Decision 6: Replay Source

- **Decision**: Use live `HoodieGymEnvironment` rollouts only for training replay.
- **Rationale**: Smoke fixtures are validation artifacts, not simulator evidence.
- **Alternatives considered**: Replaying smoke fixtures as training data was rejected because it would fabricate evidence.

## Decision 7: Evaluation

- **Decision**: Evaluate on fixed disjoint trace banks.
- **Rationale**: Disjoint traces keep train/eval separation honest and reproducible.
- **Alternatives considered**: Evaluating on training traces was rejected because it would contaminate the result.

## Decision 8: Baseline Comparison

- **Decision**: Treat Feature 037 as reference-only baseline context and do not rerun or redesign baselines in Feature 041.
- **Rationale**: Feature 041 is about campaign execution, not baseline reconstruction.
- **Alternatives considered**: Rebuilding baselines during this feature was rejected as scope creep.

## Decision 9: Reproduction Claim

- **Decision**: Do not automatically claim paper reproduction; allow only a candidate reproduction status when metrics justify it.
- **Rationale**: Honest reporting is required even when the outcome is ugly.
- **Alternatives considered**: Automatic paper reproduction claims were rejected as dishonest.

