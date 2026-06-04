# Requirements Checklist: Feature 084

## Baseline Fidelity

- [ ] HOODIE is the only proposed method.
- [ ] Active baseline set includes RO, FLC, VO, HO, BCO, and MLEO.
- [ ] Active baseline set does not include MQO.
- [ ] `Minimum Queue Offloader` does not appear in active outputs.
- [ ] `ORIGINAL_HOODIE_BASELINE` does not appear in active outputs.
- [ ] `HOODIE_PROPOSED` does not appear in active outputs.

## MLEO Semantics

- [ ] MLEO is named Minimum Latency Estimation Offloader.
- [ ] MLEO chooses minimum estimated completion latency, not minimum queue length only.
- [ ] MLEO uses all implemented timing components available in the runtime state.
- [ ] Any missing timing component is documented as an approximation.

## Formula Audit

- [ ] Task completion delay is mapped to paper formula and code.
- [ ] Task drop ratio is mapped to paper formula and code.
- [ ] Reward/cost formula is mapped to paper formula and code.
- [ ] Local execution delay is mapped.
- [ ] Vertical offloading delay is mapped.
- [ ] Horizontal offloading delay is mapped.
- [ ] Private queue timing is mapped.
- [ ] Offloading queue timing is mapped.
- [ ] Public queue timing is mapped.
- [ ] DQN/DDQN/Dueling/LSTM interfaces are accurately labeled as interfaces unless trained implementations are validated.

## Artifact Validation

- [ ] Raw rows regenerated.
- [ ] Aggregate table regenerated.
- [ ] Rankings regenerated.
- [ ] Readiness report regenerated.
- [ ] Report does not overclaim full empirical reproduction.

## Testing

- [ ] Policy registry exact-set test exists.
- [ ] Artifact invalid-token test exists.
- [ ] MLEO policy-distinctness test exists.
- [ ] Formula mapping schema/status test exists.
- [ ] `python -m pytest` passes.
