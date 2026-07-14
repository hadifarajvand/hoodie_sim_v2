# ECHO Source Reconciliation Report — Revision 280

## Verified authority

- Document ID: `17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE`
- Proposed-method tab ID: `t.iav4589yyeo7`
- Current Google Drive revision: `280`
- Modified time: `2026-07-14T10:49:47.759Z`
- Current Google Docs revision token: `ALtnJHyI7938osdAt8YpAwYSV6VlM96iG3-QN4-SOHibBBqoA3-ShBfDFMOIWrFrA8ag7iqxiC0pdt8cVfCnee5oQZ-oOPnUyVg7QZgTMA`
- Snapshot SHA-256: `3a3382e0ab0a49fb10bda7cc1740ea3a771032d7962e1957fa105eae5a5c06cc`
- No tab title is asserted.
- Equations: `1–67`, complete and sequential.
- Algorithm 1: `23` numbered lines.
- Algorithm 2: `14` numbered lines.

## Revision 278 → 280 verdict

Revision 280 is a material corrective revision. It preserves the 67-equation numbering and the 23-line training algorithm, but it changes the executable scientific contract.

### Material changes

1. **Independent ECHO learners**
   - The current text says each EA retains its own learner and checkpoint.
   - Parameter sharing across EAs is not authoritative.
   - Separate size-specific campaigns/checkpoints remain required for `N ∈ {10,15,20,25,30}`.

2. **Arrival-time destination estimation**
   - Equations (23)–(25) now use workload and active-queue conditions predicted at the estimated destination-arrival slot.
   - Latest observed values are an explicitly logged fallback with information age.
   - Estimator calibration must include signed/absolute error, false-feasible/false-infeasible rates, route, load, horizon, and information age.

3. **LSTM contract**
   - Equation (28) now defines both the recurrent embedding and decoded next-slot prediction.
   - It includes an explicit supervised MSE loss.
   - The forecasting optimizer is separate; Q-network input is detached.
   - Validation chooses forecasting checkpoint/clipping/early stopping; held-out evaluation is excluded.

4. **Pending record**
   - Equation (50) stores state, mask, action, decision slot, deadline, selected estimated completion, candidate ERT, selected lateness, and risk indicator.
   - Delayed reward inputs must not be recomputed from a later state.

5. **Reward**
   - Equation (58) includes normalized selected-action lateness:
     `-lambda_R * (I_R + Lambda(selected)/max(1, delta))`
     in addition to duration and realized drop penalty.

6. **Event-SMDP closure**
   - The next-state mask is part of the stored next observation.
   - Current task descriptor, candidate ERT, and mask are built before closing the previous interval.
   - Terminal epoch `T+1`, terminal flag, terminal observation, and final sojourn are explicit.

7. **Algorithm 1**
   - Still 23 lines, but chronology is corrected.
   - Destination-estimate-affected outbound queues are rebuilt.
   - Replay update starts only when a complete mini-batch exists.
   - Terminal resolution is explicit.

8. **Algorithm 2**
   - Expanded from 12 to 14 lines.
   - Frozen checkpoints, normalization/clipping, action order, topology, and evaluation configuration are explicit.
   - It uses arrival-time estimates, rebuilds destination-estimate-affected outbound queues, and logs calibration/runtime fields.

## Out-of-band commit `eb302cc...`

Disposition:

- The revision-278 snapshot stored in Drive is useful historical evidence.
- The repository metadata/audits that claim revision 278 as current authority are superseded by revision 280.
- Any asserted tab title is unsupported by the approved contract and must be removed.
- The necessity audits may be retained only as historical analysis after each conclusion is reclassified against revision 280.
- They cannot block or define implementation without a revision-280 audit.

## Required plan corrections

The v4.2 plan cannot be executed unchanged. The v4.3 authority must:

- replace every within-run parameter-sharing requirement with one independent ECHO learner/checkpoint per EA;
- require per-N and per-EA checkpoint lineage;
- change Algorithm 2 expected count from 12 to 14;
- update ECHO-005 for arrival-time destination prediction and calibration;
- update ECHO-006/ECHO-016 for the explicit Eq. (28) supervised predictor contract;
- update ECHO-011 for the expanded Eq. (50) pending record;
- update ECHO-013 for the revised Eq. (58) reward;
- update ECHO-014/ECHO-018 for next-mask, pre-action interval closure, and terminal semantics;
- update ECHO-015 to independent per-EA masked Dueling Double-DQL learners;
- update EVAL-001/EVAL-003/EVAL-007/EVAL-011 schemas and lineage for per-EA, per-N checkpoints and estimator calibration;
- keep all implementation tasks blocked until the revision-280 source lock and 69-row audit pass.
