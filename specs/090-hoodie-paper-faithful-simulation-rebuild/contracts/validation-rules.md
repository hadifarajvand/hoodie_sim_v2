# Validation Rules: Feature 090 HOODIE Paper-Faithful Simulation Rebuild

## Scope Rules

- No thesis method.
- No DCQ.
- No custom queue redesign.
- No output-sync tuning.
- No fabricated training curves.
- No fabricated LSTM ablation curves.

## Reference Rules

Implementation must cite the relevant file under:

```text
docs/hoodie/paper_simulation_reference/
```

before claiming a paper mechanism is implemented.

## Runtime Rules

- Episode slot count is 110 unless explicit test mode is declared.
- Action slots and drain slots are separated.
- Arrivals are Bernoulli per EA per action slot.
- Drain slots continue queue progression and reward collection.
- Every task ends completed, dropped, or unresolved with diagnostic.

## Queue Rules

- Private queue uses paper waiting/service logic.
- Offloading queue uses paper waiting/transmission logic.
- Public queues are source-specific.
- Active public queue count is computed per node per slot.
- Public CPU is divided across active public queues.
- Queue exit status must distinguish completion from timeout/drop.

## State and Reward Rules

- State contains task size, private wait, offloading wait, public queue footprint, and historical load matrix.
- LSTM/forecast mode is declared.
- Reward is collected at completion/drop time.
- Reward events link back to original state/action.

## Policy Rules

- Active method set is exactly HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- MQO is forbidden as paper baseline.
- ORIGINAL_HOODIE_BASELINE is forbidden.
- FLC always local.
- VO always Cloud.
- HO always another EA.
- RO randomizes as paper says.
- BCO cycles as paper says.
- MLEO estimates total latency, not queue length only.

## Metric Rules

- Drop ratio is dropped divided by arrived.
- Average delay is computed over completed tasks and reports denominator.
- Raw delay is positive.
- Paper-style negative delay is plot-only.
- Arrived/completed/dropped/unresolved counts are emitted.
- Zero-completion, all-policy-tie, and 100% drop saturation are flagged.

## Figure Rules

- Figure 8 requires real training traces or remains gated.
- Figure 9 requires trained HOODIE validation or is marked partial/non-paper-faithful.
- Figure 10 uses independent policy validation.
- Figure 10a-c use timeout 10 sec.
- Figure 10d-e use timeout 2 sec.
- Figure 10f uses timeout sweep 1.6-2.4 sec.
- Figure 11 requires real with/without LSTM traces or remains gated.
