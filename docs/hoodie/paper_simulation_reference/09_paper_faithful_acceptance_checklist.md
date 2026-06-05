# 09 — Paper-Faithful Acceptance Checklist

Feature 090 and later implementations must satisfy this checklist before claiming paper-faithful simulation.

## Runtime Checklist

- [ ] Uses time-slotted runtime.
- [ ] Uses 110 slots per episode.
- [ ] Separates 100 action slots and 10 drain slots.
- [ ] Generates Bernoulli arrivals per EA per action slot.
- [ ] Stores task ID, source EA, arrival slot, size, density, timeout.
- [ ] Maintains pending task registry.
- [ ] All tasks end as completed, dropped, or explicitly unresolved with diagnostic.

## Queue Checklist

- [ ] Private queue waiting follows paper formula.
- [ ] Private queue exit records completed vs dropped status.
- [ ] Offloading queue waiting follows paper formula.
- [ ] Transmission uses horizontal/vertical rate correctly.
- [ ] Offloading exit is separated from final task completion.
- [ ] Public queues are source-specific.
- [ ] Public active queue set is computed each slot.
- [ ] Public CPU is shared across active public queues.
- [ ] Cloud public CPU uses Cloud capacity.
- [ ] Queue length units are documented.

## State/Reward Checklist

- [ ] State includes task size.
- [ ] State includes private waiting time.
- [ ] State includes offloading waiting time.
- [ ] State includes public queue footprint.
- [ ] State includes historical load matrix.
- [ ] LSTM mode is declared.
- [ ] Rewards are delayed until completion/drop.
- [ ] Drop penalty is `C=40` unless explicitly overridden.
- [ ] Experience tuples link original action to delayed reward.

## Policy/Baseline Checklist

- [ ] Active method set is HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- [ ] No MQO active baseline.
- [ ] No ORIGINAL_HOODIE_BASELINE.
- [ ] FLC always local.
- [ ] VO always Cloud.
- [ ] HO always another EA.
- [ ] RO randomizes as paper defines.
- [ ] BCO cycles as paper defines.
- [ ] MLEO estimates total latency, not queue length only.
- [ ] HOODIE mode is declared: trained, substitute, or interface-only.

## Training/Validation Checklist

- [ ] Training configuration is emitted.
- [ ] Epsilon schedule is emitted.
- [ ] Replay memory behavior is emitted if training exists.
- [ ] Figure 8 remains gated unless real training traces exist.
- [ ] Figure 11 remains gated unless real with/without LSTM traces exist.
- [ ] Figure 9 uses trained HOODIE validation or is explicitly marked non-paper-faithful.
- [ ] Figure 10 uses independent policy validation runs.
- [ ] Figure 9/10 use 200 validation episodes unless in documented test mode.

## Metric Checklist

- [ ] Delay uses original arrival to final completion.
- [ ] Average delay uses completed tasks and reports denominator.
- [ ] Drop ratio is dropped / arrived.
- [ ] Paper-style negative delay is only a plotting transform.
- [ ] Arrived/completed/dropped counts are emitted for each sweep and policy.
- [ ] Zero-completion traces are flagged.
- [ ] 100% drop saturation is flagged.
- [ ] All-policy ties are flagged.

## Figure Checklist

- [ ] Figure 10a-c use timeout 10 sec.
- [ ] Figure 10d-e use timeout 2 sec.
- [ ] Figure 10f uses timeout sweep 1.6-2.4 sec.
- [ ] Figure 9b preserves probability groups.
- [ ] Figure 9d changes both task-size range and P.
- [ ] Figure 9e changes data-rate settings.

## Final Verdicts

Use one of:

```text
paper_faithful_simulation_ready
paper_faithful_simulation_partial
paper_faithful_simulation_blocked
```

Do not use `ready` unless runtime, queue, reward, baseline, validation, and metric checks pass.
