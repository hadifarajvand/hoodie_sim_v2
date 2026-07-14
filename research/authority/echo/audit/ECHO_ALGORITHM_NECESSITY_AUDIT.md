# ECHO Algorithm Necessity Audit

## Verdict

Both algorithms are necessary as executable contracts, but **neither is implementation-ready in the locked revision**. They must be revised before coding because the training procedure contains a decision-state ordering contradiction and both procedures under-specify when outbound ERT orders must be rebuilt.

## Algorithm 1 — Training procedure

**Necessity:** KEEP, REVISE BEFORE IMPLEMENTATION.

### Blocking defects

1. **Current-state construction is ordered incorrectly.** Line 10 says to construct `s_n(τ_{n,m})`, but Eq. (53) includes the arriving task descriptor, candidate ERT vector, and action mask, which are not computed until line 12. The previous SMDP transition in line 11 therefore cannot safely use the state claimed in line 10.

   **Required order:** create task descriptor and deadline → estimate candidates → compute candidate ERT and mask → construct the complete current observation → finalize the previous interval transition with this observation → select the current action → admit the task.

2. **Pending record is incomplete.** Eq. (50) does not store the selected action's decision-time lateness or estimated completion, yet Eq. (58) requires that value when the task resolves later. Recomputing it later would use a changed environment and would be wrong.

3. **Outbound queues are not rebuilt on load-estimate changes.** Line 15 rebuilds “changed” queues, but transfer ERT depends on destination workload and active-queue estimates, which may change every slot even when queue membership is unchanged.

4. **Terminal-state convention is missing.** Line 22 must define the terminal observation, terminal mask, final sojourn, and whether unresolved active tasks remain resource-occupying before being marked dropped.

5. **Replay readiness and next-mask persistence are under-specified.** Training should start only when at least one complete mini-batch exists. The next decision state's mask must be stored in the state or transition and used by Eqs. (64)-(65).

6. **LSTM training contract is incomplete.** The algorithm mentions an update but does not define the supervised loss, optimizer schedule, checkpoint selection, or strict separation of training/validation/evaluation traces.

### Required disposition

Retain Algorithm 1, but rewrite it after Eqs. (23), (28), (46), (50), (53)-(54), and (59)-(65) are corrected. It is the authoritative implementation sequence and should be backed by chronology and accounting tests.

## Algorithm 2 — Inference procedure

**Necessity:** KEEP, REVISE BEFORE IMPLEMENTATION.

### Blocking defects

1. **Outbound ERT refresh trigger is incomplete.** Destination reports and LSTM estimates can change candidate completion and transfer-queue priority without a queue insertion/removal. Nonempty transfer queues must be re-estimated when relevant destination information ages or changes.

2. **Frozen inference assets are not stated.** The selected Q-network checkpoint, LSTM checkpoint, normalization bounds, clipping bounds, topology-specific action ordering, and mask convention must be immutable during evaluation.

3. **Outcome logging is omitted.** Inference does not learn, but it must still resolve every task once and record decision-time estimate, realized completion/drop, false-feasible status, route, information age, and runtime overhead.

4. **No-arrival state convention is unnecessary at decision-only inference.** The algorithm should not invoke a learned no-op action; it should simply advance the environment when no task arrives.

5. **Destination service rule needs one executable reference.** “Frozen source-indexed queue rule” must point to the exact FIFO/capacity-sharing implementation used by all compared methods.

### Required disposition

Retain Algorithm 2 as the evaluation/runtime contract. Rewrite it in lockstep with Algorithm 1 so training and inference share one environment-step function and differ only in exploration, replay, gradient updates, and metric logging.

## Overall algorithm decision

- Algorithm 1: **KEEP — BLOCKED UNTIL REVISED**
- Algorithm 2: **KEEP — BLOCKED UNTIL REVISED**
- Implementation gate: **CLOSED**
