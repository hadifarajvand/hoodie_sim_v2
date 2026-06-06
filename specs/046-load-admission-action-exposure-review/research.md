# Research: Load, Admission, and Action-Exposure Review

## Decisions

### 1. Diagnostic scope remains passive
- **Decision**: Feature 046 will not change simulator behavior, policies, reward timing, or deadlines.
- **Rationale**: Feature 045 already established that runtime repair is not supported by the current evidence. Feature 046 exists to explain the observed weakness, not to alter outcomes.
- **Alternatives considered**: Runtime repair or policy redesign. Rejected because they violate the feature’s diagnostic-only scope.

### 2. Evidence sources are Feature 044 traces and the Feature 045 report
- **Decision**: The review will ingest Feature 044 passive trace artifacts and the Feature 045 diagnostic report as primary evidence.
- **Rationale**: Feature 044 provides lifecycle traces, while Feature 045 adds a verdict and evidence framing that should be reused rather than re-derived.
- **Alternatives considered**: New instrumentation or fresh runtime probes. Rejected because they would alter the evidence boundary.

### 3. Paper-default runtime remains `T = 110`, `P = 0.5`, `N = 20`
- **Decision**: The review will use the same paper-default horizon and environment constants as the prior diagnostic features.
- **Rationale**: The purpose is to explain the existing completion weakness under the recovered paper-default configuration.
- **Alternatives considered**: Changing the horizon or load to probe a different regime. Rejected because that would no longer diagnose the paper-default case.

### 4. Same seed/strategy grid is reused
- **Decision**: Use seeds `[0, 1, 2]` and the approved five probe strategies.
- **Rationale**: Reusing the same grid preserves comparability with Features 042–045 and prevents a new experimental regime from being introduced.
- **Alternatives considered**: Adding more seeds or strategies. Deferred because this feature should quantify the existing regime first.

### 5. Action exposure must include legal-but-unselected actions
- **Decision**: Track legal action availability versus selected action frequency, including legal-but-unselected counts.
- **Rationale**: Without legal-but-unselected counts, action exposure bias cannot be distinguished from lack of opportunity.
- **Alternatives considered**: Only counting selected actions. Rejected because it cannot quantify underexposure.

### 6. Admission serialization must be measured explicitly
- **Decision**: Measure same-slot generated tasks, same-slot admission counts, and admission lag.
- **Rationale**: The project’s serialization constraint is one plausible cause of backlog and must be quantified directly.
- **Alternatives considered**: Inferring serialization from terminal outcomes alone. Rejected because it obscures the mechanism.

### 7. Recommendation routing stays diagnostic
- **Decision**: The report will recommend the next diagnostic feature type, not runtime repair.
- **Rationale**: Current evidence says runtime repair is not recommended. Follow-up should target load, admission, or action-exposure analysis.
- **Alternatives considered**: Always recommending repair if drops are high. Rejected as unjustified.

### 8. Older pointer-sensitive tests remain excluded
- **Decision**: Validation will use committed artifacts and safe tests only.
- **Rationale**: Pointer-sensitive report tests are outside scope and can create false failures unrelated to Feature 046.
- **Alternatives considered**: Including all historical report tests. Rejected because it is not a stable validation set for this feature.
