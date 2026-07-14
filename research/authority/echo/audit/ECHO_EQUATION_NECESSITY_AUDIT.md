# ECHO Equation Necessity Audit

## Decision

The 67-equation specification is mathematically complete enough to audit, but it is not efficient or implementation-ready. The audit retains the ECHO core while removing tautologies, merging duplicated queue rules, isolating inherited baseline machinery, and blocking implementation on specific notation and estimator defects.

## Status counts

- **APPENDIX_OR_CITATION:** 1
- **APPENDIX_OR_SPEC:** 1
- **CONDITIONAL_LSTM:** 2
- **KEEP_CORE:** 18
- **KEEP_REVISE:** 12
- **KEEP_SUPPORTING:** 8
- **MERGE_GENERIC_SCHEDULER:** 8
- **MERGE_OR_INLINE:** 13
- **REMOVE_AS_NUMBERED:** 3
- **REMOVE_OR_REWRITE:** 1

## Hard implementation blockers

1. Eqs. **(23)-(25)** estimate destination waiting from decision-time workload rather than explicitly predicted workload at the task's destination-arrival slot.
2. Eq. **(28)** does not define the prediction output and supervised loss claimed in the text.
3. Eq. **(46)** has ambiguous source indexing.
4. Eq. **(49)** is undefined for local tasks.
5. Eq. **(50)** omits decision-time selected lateness/estimated completion needed by Eq. (58).
6. Eqs. **(53)-(54)** do not define candidate-ERT values for physically invalid canonical action positions.
7. Eqs. **(59)-(65)** require explicit first/terminal interval and next-mask conventions.
8. Algorithm 1 constructs/finalizes the current decision state before the task-specific ERT vector and mask are computed.
9. Algorithms 1 and 2 do not require outbound ERT reordering when destination information changes without queue membership changes.

## Equation-by-equation audit

| Eq. | Status | Necessity | Required action |
|---:|---|---|---|
| 1 | MERGE_OR_INLINE | Baseline arrival indicator; needed by the simulator but not a distinct ECHO contribution. | Define in prose or the notation table; keep the boolean field in code. |
| 2 | KEEP_CORE | Creates the absolute deadline used by every ERT and success condition. | Keep explicitly numbered and unit-test off-by-one behavior. |
| 3 | KEEP_CORE | Defines the physically available local, connected-edge, and cloud routes. | Keep explicitly; it is the root of physical masking. |
| 4 | MERGE_OR_INLINE | A convenience destination map derived directly from the action labels. | Inline as a definition beside Eq. 3 or encode as an action-to-destination helper. |
| 5 | MERGE_OR_INLINE | A direct consequence of local versus offload action selection. | Merge with queue-admission prose; no separate scientific equation is needed. |
| 6 | MERGE_OR_INLINE | Stored destination is essential, but this equation only restates the action mapping. | Keep as an implementation invariant, not a standalone numbered equation. |
| 7 | APPENDIX_OR_SPEC | Defines slot-boundary transmission completion chronology rather than ECHO novelty. | Retain in the simulator contract/appendix and test boundary timing. |
| 8 | REMOVE_AS_NUMBERED | The aggregate destination-arrival count is not used by later equations or the learning rule. | Remove from the main method unless a metric or constraint explicitly consumes it. |
| 9 | KEEP_SUPPORTING | Required to estimate local service duration and reproduce slot-level execution. | Keep; verify units and ceiling behavior. |
| 10 | KEEP_CORE | Defines local waiting under the constructive predecessor order. | Keep and link explicitly to the deterministic order-construction procedure. |
| 11 | KEEP_CORE | Produces the local candidate completion estimate used by ERT. | Keep and test one-slot and idle-CPU cases. |
| 12 | MERGE_OR_INLINE | A baseline rate selector that can be folded into transmission duration. | Merge with Eq. 13 or define in the notation table. |
| 13 | KEEP_SUPPORTING | Required for source-side offloading duration. | Keep; verify horizontal/cloud rate selection and slot rounding. |
| 14 | KEEP_CORE | Defines outbound waiting under the ERT order and stored destinations. | Keep and test heterogeneous destination rates among predecessors. |
| 15 | KEEP_CORE | Defines completion of the source transmission stage. | Keep; it is needed for destination-arrival timing. |
| 16 | MERGE_OR_INLINE | The destination arrival slot is a one-line consequence of Eq. 15 and the boundary chronology. | Inline with Eq. 25 or the lifecycle specification. |
| 17 | KEEP_SUPPORTING | Defines active source-indexed destination queues for capacity sharing. | Keep, but state whether the active head task remains included in the queue state. |
| 18 | MERGE_OR_INLINE | Cardinality is immediately derived from Eq. 17. | Merge into Eq. 17 or notation. |
| 19 | KEEP_REVISE | Cycle workload is necessary, but the queue semantics must explicitly include residual work of any active head task. | Revise before implementation; otherwise destination load can be understated. |
| 20 | KEEP_CORE | Accounts for activation of a previously inactive source-indexed queue by a candidate. | Keep; test idle destination and already-active source queue. |
| 21 | MERGE_OR_INLINE | A convenience unification of edge and cloud capacity. | Fold into Eq. 22 or notation. |
| 22 | KEEP_CORE | Defines the candidate queue's effective share of destination capacity. | Keep, while documenting the fixed-share approximation. |
| 23 | KEEP_REVISE | Destination waiting is central, but it uses decision-time workload rather than workload predicted at actual arrival. | Specify conservative semantics or estimate workload at the arrival slot; validate estimator bias. |
| 24 | KEEP_SUPPORTING | Required destination processing duration under the estimated share. | Keep and test capacity/rounding. |
| 25 | KEEP_REVISE | This is the core end-to-end offload estimate, but its validity depends on corrected arrival-time workload handling in Eq. 23. | Keep after revising and calibrating Eqs. 23-25 together. |
| 26 | CONDITIONAL_LSTM | Needed only when retaining recurrent load estimation as part of the selected ECHO configuration. | Keep in the LSTM subsection/appendix; ECHO core must remain definable without it. |
| 27 | CONDITIONAL_LSTM | History construction is an LSTM input detail inherited from the base framework. | Keep only with the LSTM configuration. |
| 28 | KEEP_REVISE | The LSTM path is used, but the equation defines only an embedding while the text also claims a decoded next-slot prediction. | Define both embedding and prediction outputs plus the supervised loss, or narrow the claim. |
| 29 | KEEP_CORE | Local queue ERT is a primary ECHO contribution. | Keep explicitly. |
| 30 | KEEP_CORE | End-to-end transfer queue ERT is a primary ECHO contribution. | Keep explicitly. |
| 31 | MERGE_OR_INLINE | A convenience wrapper over local and offload completion estimates. | Merge with Eq. 32 as a piecewise candidate-ERT definition. |
| 32 | KEEP_CORE | Candidate-level ERT drives route feasibility and masking. | Keep explicitly, preferably combined with Eq. 31. |
| 33 | MERGE_GENERIC_SCHEDULER | The feasible-set concept is necessary but duplicated for local and transfer queues. | Replace Eqs. 33-40 with one generic queue-selection rule parameterized by completion estimate. |
| 34 | MERGE_GENERIC_SCHEDULER | Necessary feasible-task selection, but it belongs in the generic scheduler. | Merge into one piecewise scheduling equation or scheduler algorithm. |
| 35 | MERGE_GENERIC_SCHEDULER | Lateness equals max(0, -ERT) and is algebraically derived. | Define once generically; do not number separately for local queue. |
| 36 | MERGE_GENERIC_SCHEDULER | Necessary all-late fallback, duplicated by the transfer-queue version. | Merge into the generic scheduler. |
| 37 | MERGE_GENERIC_SCHEDULER | Transfer feasible set duplicates the local structure. | Merge into the generic scheduler. |
| 38 | MERGE_GENERIC_SCHEDULER | Transfer feasible selection duplicates the local structure. | Merge into the generic scheduler. |
| 39 | MERGE_GENERIC_SCHEDULER | Transfer lateness is the same generic transformation of ERT. | Merge into the generic scheduler. |
| 40 | MERGE_GENERIC_SCHEDULER | Transfer all-late fallback duplicates the local rule. | Merge into the generic scheduler. |
| 41 | KEEP_SUPPORTING | Fixed output dimensionality is required for the Q-network and masks. | Keep in the learning architecture, not as a claimed novelty. |
| 42 | KEEP_CORE | Defines deadline-feasible physical routes. | Keep explicitly. |
| 43 | MERGE_OR_INLINE | Candidate lateness is max(0, -candidate ERT). | Define inline with fallback or once as a generic lateness function. |
| 44 | KEEP_CORE | Minimum-lateness fallback prevents arbitrary behavior when all routes are predicted late. | Keep explicitly and define deterministic tie-breaking. |
| 45 | KEEP_CORE | Defines the effective action set used by the policy. | Keep explicitly. |
| 46 | KEEP_REVISE | The mask is essential, but index n must be tied unambiguously to source s_i and invalid canonical ERT entries need a convention. | Revise notation and align with Eq. 54. |
| 47 | REMOVE_AS_NUMBERED | This only states that the selected action belongs to the set from which it is selected. | Remove; enforce as an invariant/test. |
| 48 | REMOVE_AS_NUMBERED | This is an admission operation, not a mathematical model relation. | Move to Algorithm 1/2 and simulator invariants. |
| 49 | REMOVE_OR_REWRITE | The metadata tuple is implementation schema and k_i is undefined for local tasks under Eq. 6. | Remove from main equations; define conditional offload metadata or set a consistent local destination convention. |
| 50 | KEEP_REVISE | A pending record is necessary for delayed outcomes, but it omits decision-time selected lateness required by Eq. 58. | Add selected estimated completion/lateness and terminal bookkeeping fields; treat as a data schema. |
| 51 | MERGE_OR_INLINE | Queue occupancies are straightforward state features. | Move to the state-element table or combine with Eq. 52. |
| 52 | KEEP_SUPPORTING | Remaining source workloads are informative state features and implementation observables. | Keep, but combine with state definition if space is constrained. |
| 53 | KEEP_REVISE | The DRL observation is essential, but undefined values for physically invalid candidate ERT positions must be specified. | Keep after defining normalization, clipping bounds, missing-value encoding, and exact dimension. |
| 54 | KEEP_REVISE | Fixed candidate ERT vector is needed by Eq. 53, but ERT is undefined for disconnected/source canonical positions. | Define a deterministic fill value plus mask, then merge with Eq. 53 if desired. |
| 55 | KEEP_CORE | Defines realized task duration used in reward and reporting. | Keep and test boundary/drop timing. |
| 56 | MERGE_OR_INLINE | Predicted-infeasibility indicator is needed by the reward but can be defined within the reward block. | Keep concept; separate numbering is optional. |
| 57 | KEEP_CORE | Distinguishes actual failure to achieve deadline-satisfied completion. | Keep; ensure every generated task resolves exactly once. |
| 58 | KEEP_REVISE | The reward is central, but penalty weights and interaction with delayed discounting require validation. | Keep; pre-register weight selection and test double-counting/sensitivity. |
| 59 | KEEP_REVISE | Essential if the stronger event-driven SMDP formulation is retained; it prevents overlapping delayed-reward transitions. | Keep; specify first/last interval, terminal state, and reward-timing semantics. |
| 60 | KEEP_REVISE | Supports the requested formal SMDP claim, but only for the complete simulator state under explicit Markov assumptions. | Keep proposition; move proof to appendix if needed and do not claim the compressed observation is Markov. |
| 61 | APPENDIX_OR_CITATION | Standard inherited Dueling-DQN decomposition, not an ECHO contribution. | Cite the baseline and place in appendix/implementation spec unless required by venue. |
| 62 | KEEP_CORE | Defines how deadline and physical constraints enter value-based action selection. | Keep explicitly. |
| 63 | KEEP_CORE | Ensures exploration and exploitation obey the same action mask. | Keep explicitly. |
| 64 | KEEP_SUPPORTING | Required for masked Double-DQL next-action selection. | Keep in the learning update block. |
| 65 | KEEP_REVISE | Core SMDP Double-DQL target, contingent on a valid next-state mask and terminal convention. | Keep after Algorithm 1 ordering and terminal-state fixes. |
| 66 | MERGE_OR_INLINE | The online prediction is a direct term in the loss. | Inline into Eq. 67. |
| 67 | KEEP_SUPPORTING | Standard mini-batch loss required for implementation, though not novel. | Keep or combine with Eq. 66; cite standard DQL practice. |

## Recommended compact scientific formulation

A defensible paper does not need 67 separately numbered equations. The core can be reduced to approximately **30-36 equations** by:

- combining action mapping and queue admission definitions;
- combining local and outbound scheduling into one generic ERT scheduler;
- defining lateness once as `max(0, -ERT)`;
- moving record tuples and slot-boundary indicators to the executable specification;
- moving inherited LSTM and Dueling/Double-DQL formulas to an appendix or citation;
- combining prediction and loss equations.

This reduction does **not** remove ECHO functionality. It separates scientific contribution from implementation bookkeeping.

## Final gate

**Do not implement or rewrite the manuscript from this specification yet.** First correct the blocking equations and rewrite both algorithms while preserving the locked source as the immutable pre-audit baseline.
