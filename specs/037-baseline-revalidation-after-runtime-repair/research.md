# Research: Baseline Revalidation After Runtime Repair

## Decision 1: Reuse existing baseline registries and environment entry points

- **Decision**: Revalidate baselines through the existing policy registry and shared `HoodieGymEnvironment` pathway rather than building a new ad hoc simulator loop.
- **Rationale**: The feature is a sanity revalidation, not a simulator rewrite. Reusing the existing registry and environment path proves the baselines still run under the repaired contracts without adding another execution surface.
- **Alternatives considered**:
  - A bespoke baseline loop: rejected because it would duplicate environment logic and weaken the interface guarantee.
  - Direct policy invocation without the environment: rejected because it would bypass the shared action mask and the repaired runtime contracts.

## Decision 2: Deterministic seed set

- **Decision**: Use seeds `0`, `1`, and `2` as the minimal deterministic set; allow `0` through `4` when runtime cost is acceptable.
- **Rationale**: Three seeds are enough for reproducible sanity validation, while five seeds provide a slightly stronger check if the matrix runner can absorb the cost.
- **Alternatives considered**:
  - Single-seed validation: rejected because it is too weak to distinguish deterministic behavior from luck.
  - A larger seed sweep: rejected for this feature because it adds cost without changing the revalidation objective.

## Decision 3: Scenario scope

- **Decision**: Default to the repaired paper-default runtime configuration. If an existing reduced smoke scenario is already used by the matrix runner for deterministic validation, the feature may use it, but the report must label it as smoke revalidation.
- **Rationale**: Paper-default is the right baseline reference, but the feature explicitly allows a smaller runner-scoped smoke matrix to keep validation affordable.
- **Alternatives considered**:
  - Paper-default only: rejected because the user explicitly allowed a smaller smoke scenario for CI/runtime cost.
  - Arbitrary custom scenarios: rejected because they would weaken comparability and drift from the approved runtime context.

## Decision 4: Metrics and reporting scope

- **Decision**: Validate the existing metric schema fields for completeness and sanity, including policy name, scenario name, seed, final metrics, task counts, completion/drop ratio, throughput, average delay, and any available runtime-contract markers.
- **Rationale**: The goal is to confirm the evaluation output is structurally sound after the runtime repairs, not to compare against paper curves.
- **Alternatives considered**:
  - Curve matching against old outputs: rejected because the feature must not tune or claim reproduction.
  - New bespoke metrics: rejected because the existing schema already supports the required sanity checks.

## Decision 5: Comparative drift use

- **Decision**: Old artifacts may be used only as drift references after the runtime repairs; they are not ground truth.
- **Rationale**: Runtime repairs changed the evaluation baseline, so old results can only flag drift, not define correctness.
- **Alternatives considered**:
  - Treating old artifacts as truth: rejected because it would force repaired behavior to mimic known pre-repair defects.

## Decision 6: Report claim boundary

- **Decision**: The report must explicitly state that baseline revalidation completed or failed, that no paper reproduction claim is being made, and that no curve fitting or training occurred.
- **Rationale**: The feature’s purpose is post-repair sanity validation, not paper reproduction.
- **Alternatives considered**:
  - Implicit claim boundaries: rejected because the report would then be ambiguous and easy to misread.
