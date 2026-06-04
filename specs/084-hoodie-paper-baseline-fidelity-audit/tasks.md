# Tasks: Feature 084 HOODIE Paper Baseline and Formula Fidelity Audit

## A. Baseline Repair Tasks

- [ ] A001 Search repository for active `MQO` references.
- [ ] A002 Search repository for `Minimum Queue Offloader` references.
- [ ] A003 Search repository for `ORIGINAL_HOODIE_BASELINE` references.
- [ ] A004 Search repository for `HOODIE_PROPOSED` references.
- [ ] A005 Replace active `MQO` policy ID with `MLEO`.
- [ ] A006 Replace active baseline display name with `Minimum Latency Estimation Offloader`.
- [ ] A007 Ensure active policies are exactly `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- [ ] A008 Ensure `HOODIE` is the only proposed method.
- [ ] A009 Ensure `ORIGINAL_HOODIE_BASELINE` is absent from active reports, rankings, policy registries, and artifacts.

## B. MLEO Policy Semantics Tasks

- [ ] B001 Locate current MQO implementation in runtime evaluation policy adapters.
- [ ] B002 Determine whether current implementation is queue-length-only, latency-estimation-based, or mixed.
- [ ] B003 Replace queue-length-only behavior with minimum estimated completion latency behavior.
- [ ] B004 Include local execution latency in candidate estimates.
- [ ] B005 Include vertical offloading latency in candidate estimates.
- [ ] B006 Include horizontal offloading latency in candidate estimates.
- [ ] B007 Include queueing delay components where implemented.
- [ ] B008 Include remote/cloud execution timing where implemented.
- [ ] B009 Document unavailable paper components as approximations.

## C. Formula Mapping Tasks

- [ ] C001 Extract task completion delay formula obligation from HOODIE OCR/PDF.
- [ ] C002 Extract task drop ratio formula obligation.
- [ ] C003 Extract reward/cost formula obligation.
- [ ] C004 Extract local execution timing obligation.
- [ ] C005 Extract vertical offloading timing obligation.
- [ ] C006 Extract horizontal offloading timing obligation.
- [ ] C007 Extract private queue timing obligation.
- [ ] C008 Extract offloading queue timing obligation.
- [ ] C009 Extract public queue timing obligation.
- [ ] C010 Extract DQN/DDQN/Dueling obligations.
- [ ] C011 Extract LSTM recovery/forecast obligation.
- [ ] C012 Extract baseline policy definitions.
- [ ] C013 Extract simulation/evaluation output and figure obligations.
- [ ] C014 Map each item to concrete code locations.
- [ ] C015 Assign each row status: `exact`, `approximate`, `missing`, `wrong`, or `out_of_scope`.
- [ ] C016 Add required fix for each `approximate`, `missing`, or `wrong` item.

## D. Artifact and Report Tasks

- [ ] D001 Regenerate deterministic raw rows with `MLEO` replacing `MQO`.
- [ ] D002 Regenerate aggregate table.
- [ ] D003 Regenerate policy rankings.
- [ ] D004 Regenerate readiness report.
- [ ] D005 Ensure no active generated artifact contains `MQO`.
- [ ] D006 Ensure no active generated artifact contains `Minimum Queue Offloader`.
- [ ] D007 Ensure no active generated artifact contains `ORIGINAL_HOODIE_BASELINE`.
- [ ] D008 Ensure no active generated artifact contains `HOODIE_PROPOSED`.
- [ ] D009 Ensure generated artifacts contain `MLEO`.

## E. Test Tasks

- [ ] E001 Add unit test for active policy registry exact set.
- [ ] E002 Add unit test for absence of active MQO.
- [ ] E003 Add unit test for absence of `ORIGINAL_HOODIE_BASELINE`.
- [ ] E004 Add unit test for absence of `HOODIE_PROPOSED` in paper-fidelity outputs.
- [ ] E005 Add unit test for MLEO policy distinctness.
- [ ] E006 Add artifact validation test for aggregate rows.
- [ ] E007 Add validation test for formula mapping matrix schema and statuses.
- [ ] E008 Run full test suite with `python -m pytest`.

## F. Review Gate Tasks

- [ ] F001 Mark PR #24 / Feature 083 as blocked for final merge until Feature 084 repair is complete.
- [ ] F002 Report final branch SHA.
- [ ] F003 Report regenerated artifact paths.
- [ ] F004 Report remaining fidelity gaps honestly.
- [ ] F005 Do not claim full empirical HOODIE paper reproduction unless trained DRL/LSTM and paper figure reproduction are actually validated.
