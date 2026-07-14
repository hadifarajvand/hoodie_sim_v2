# ECHO-MEP-v4.3 Authoritative Amendment

## Status

This amendment is authoritative together with `ECHO_MASTER_EXECUTION_PLAN.md` v4.2.
Where they conflict, this amendment wins. Execution remains paused until the v4.3
validator passes and a fresh SRC-001 attempt is authorized.

## Source control

- Current Drive revision: `280`
- Current modified time: `2026-07-14T10:49:47.759Z`
- Current method snapshot: `research/authority/echo/live/ECHO_PROPOSED_METHOD.md`
- Expected snapshot SHA-256: `3a3382e0ab0a49fb10bda7cc1740ea3a771032d7962e1957fa105eae5a5c06cc`
- Equations: 67
- Algorithm 1 lines: 23
- Algorithm 2 lines: 14
- No tab title may be asserted.

## Global semantic overrides

1. Replace every statement that ECHO shares Q/LSTM parameters among EAs with:
   each EA has an independent learner, replay memory, online network, target network,
   optimizer state, exploration state, LSTM/forecasting state, and checkpoint.

2. Retain size-specific `N+2` action outputs and size-specific state blocks.
   Train and evaluate separately for N = 10, 15, 20, 25, 30.
   No zero-shot cross-N claim is permitted.

3. Destination estimates for Eqs. 23–25 are evaluated at the estimated destination-arrival
   slot using only decision-time information. A newest-observation fallback is allowed only
   when explicitly logged with information age.

4. Eq. 28 includes embedding, decoded next-slot prediction, supervised MSE, separate optimizer,
   detached Q-network input, validation-only checkpoint selection, and no held-out fitting.

5. Eq. 50 stores selected estimated completion, candidate ERT, selected lateness, mask, and risk.

6. Eq. 58 is:
   r_i = -T_i^sys
         - lambda_R * (I_i^R + Lambda_i(alpha_i,t_i^a)/max(1,delta_i))
         - lambda_D * I_i^D.

7. The next decision mask is stored with the next state. At a later EA decision, construct the
   arriving task descriptor, estimates, ERT vector, mask, and complete pre-action observation
   before closing the previous interval. Terminal epoch T+1 has an explicit terminal state,
   terminal flag, final sojourn, and zero continuation value.

8. Algorithm 2 contains 14 numbered lines.

## Task-card overrides

### SRC-001
Verify revision 280, snapshot SHA, 67 equations, Algorithm 1 lines 1–23,
Algorithm 2 lines 1–14, and 69 audit rows. Reject any asserted tab title.

### ECHO-005
Implement arrival-time workload/active-queue prediction for Eqs. 23–25, newest-observation
fallback with information age, and calibration outputs/tests.

### ECHO-006
Create history, forecast target, prediction horizon, report age, and training-only target records.

### ECHO-011
Persist all Eq. 50 fields, including selected estimated completion, selected ERT, selected
lateness, mask, and risk indicator.

### ECHO-013
Implement the revision-280 Eq. 58 normalized selected-lateness term.

### ECHO-014
Persist next mask in the next state; finalize the previous interval only after the complete
current pre-action observation is built; implement explicit T+1 terminal closure.

### ECHO-015
Implement one independent masked Dueling Double-DQL learner per EA. No shared ECHO parameter
server is permitted. Checkpoint identity is `(N, EA, training_seed, method, config_hash)`.

### ECHO-016
Implement Eq. 28 embedding + decoded prediction, MSE loss, separate optimizer, detached Q input,
validation checkpoint selection, clipping/early stopping, and held-out exclusion.

### ECHO-018
Match Algorithm 1's 23 lines and Algorithm 2's 14 lines exactly. Rebuild nonempty outbound queues
when relevant destination estimate or information age changes. Preserve frozen inference assets
and outcome/calibration/runtime logging.

### EVAL-001
Schemas must include prediction horizon, report age, observed-versus-forecast fallback,
estimated completion, selected ERT/lateness, next mask, terminal flag, and per-EA checkpoint IDs.

### EVAL-003 / EVAL-007 / EVAL-011
Lineage and validation must enforce one checkpoint per `(N, EA, training seed)` for ECHO,
HOODIE, and ECHO-NoLSTM where applicable.

## Out-of-band revision-278 artifacts

Revision-278 audits are historical only. They must be marked `SUPERSEDED_BY_REVISION_280`
or archived without deletion. They are not current authority.

## Execution gate

Until a fresh SRC-001 task locks revision 280 and passes the 69-row audit:

- `NEXT_TASK.task_id` must remain null;
- BASE work may not be newly authorized by this amendment;
- no ECHO implementation task may be authorized;
- the prior SRC-001 attempts remain historical evidence.
