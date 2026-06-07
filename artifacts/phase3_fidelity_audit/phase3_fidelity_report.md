# Phase 3.0 DRL/LSTM Fidelity Audit

## Scope

- Audit-only comparison of the current implementation against HOODIE DRL/LSTM contracts.
- Runtime behavior unchanged.
- No paper-performance claim made.

## Files Inspected

- `main.py`
- `environment/environment.py`
- `environment/server.py`
- `environment/cloud.py`
- `environment/queues.py`
- `environment/task.py`
- `environment/task_generator.py`
- `environment/action_model.py`
- `environment/matchmaker.py`
- `phase1_tracing.py`
- `phase2_mechanisms.py`
- `training/trace_dataset.py`
- `training/replay_buffer.py`
- `training/lstm_forecaster.py`
- `training/trainers.py`
- `training/train_phase3.py`
- `decision_makers/agent.py`
- `decision_makers/dummies.py`
- `hyperparameters/hyperparameters.json`
- `specs/100-hoodie-paper-faithful-baseline/contracts/paper-runtime-contract.md`
- `specs/100-hoodie-paper-faithful-baseline/contracts/paper-state-reward-contract.md`
- `specs/100-hoodie-paper-faithful-baseline/contracts/paper-lstm-training-contract.md`
- `specs/100-hoodie-paper-faithful-baseline/contracts/paper-topology-action-contract.md`
- `specs/100-hoodie-paper-faithful-baseline/contracts/paper-evaluation-figures-contract.md`
- `specs/100-hoodie-paper-faithful-baseline/checklists/system-model-ocr-122-747/system-model-checklist.md`
- `resources/papers/hoodie/ocr/merged.tex`

## Paper Contracts Used

- Section III.A.1 state space, Eq. (18)
- Section III.A.2 action space, Eq. (19)
- Section III.A.3 reward/cost, Eq. (20)–(23)
- Section III.B problem formulation, Eq. (24)
- Section IV.A HOODIE model
- Figure 4 HOODIE neural network structure
- Figure 5 LSTM load prediction model
- Algorithm 1 HOODIE training
- Eq. (25) dueling DQN
- Double-DQN target update in Algorithm 1
- Replay memory behavior in Algorithm 1
- Delayed reward collection using D_n(t), Eq. (27)

## State Contract Audit Summary

| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |
|---|---|---|---|---|---|---|---|
| eta_n(t) | Eq. (18) | task size arriving at slot t | environment/task.py, environment/task_generator.py | PASS | Task exposes input_data_size/size and TaskGenerator generates size per task. | The size field exists natively. | Keep size field explicit in runtime and traces. |
| w_priv_n(t) | Eq. (18) | private queue waiting time | environment/server.py, environment/queues.py | PARTIAL | Private waiting time is exposed by Server.get_features() and used in DQN observation vectors. | It is present as a proxy waiting-time feature, but the current state vector collapses richer paper state into a small legacy observation. | Export a paper-native state object that preserves named fields. |
| w_off_n(t) | Eq. (18) | offloading queue waiting time | environment/server.py, environment/queues.py | PARTIAL | Offloading waiting time is exposed by Server.get_features() and fed into observations. | Waiting time exists, but not as a first-class paper-state structure. | Separate paper-state export from legacy observation packing. |
| l_pub_n(t-1) | Eq. (18) | previous-slot public queue length vector | environment/environment.py, phase1_tracing.py | PARTIAL | Environment.pack_observation() appends public queue lengths to per-agent observations. | The signal exists but is packed into a legacy observation array rather than an explicit paper state field. | Expose explicit l_pub_n(t-1) as a named state component. |
| L(t) | Eq. (18), Section III.A.1 | historical load matrix W x (N+1) | environment/environment.py, training/trace_dataset.py | FAIL | The runtime does not maintain a native W x (N+1) load matrix; trace_dataset reconstructs proxy states from task lifecycle rows. | Historical load is not stored natively and the current training pipeline reconstructs approximations from traces. | Introduce a paper-state history buffer before training consumes it. |
| predicted next load | Figure 5 / Section IV.A | LSTM forecast for all nodes | training/lstm_forecaster.py, decision_makers/agent.py | FAIL | LSTMForecaster is a standalone regressor on handcrafted rows; Agent uses an LSTM hidden history, not a node-wise load forecaster. | The implemented LSTM is not the paper's W x (N+1) load predictor. | Replace the toy forecaster with the paper's load-history pipeline later. |
| state_dim | Eq. (18), Eq. (25) input | full paper-state dimensionality per agent | training/trace_dataset.py, decision_makers/agent.py | PARTIAL | TraceDataset summary reports state_dim from reconstructed transitions; DQN input_dim is this collapsed vector. | The model trains on collapsed/reconstructed state vectors, not native paper-state tensors. | Decouple trace reconstruction from paper-state training inputs. |

## Action Contract Audit Summary

| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |
|---|---|---|---|---|---|---|---|
| d_n^(1)(t) | Eq. (19) | local vs offload first-stage decision | environment/action_model.py, environment/matchmaker.py, phase1_tracing.py | PASS | TwoStageAction.first_stage_decision and d_n_1 represent local/offload explicitly; traces carry first_stage_decision. | No gap in the first-stage decision representation. | Keep the explicit contract and preserve trace fields. |
| D_n(t) | Eq. (19), Algorithm 1 | destination choice for offloaded task | environment/action_model.py, environment/matchmaker.py | PASS | TwoStageAction.d_nk_2 stores the chosen destination sparsely; local actions use an empty destination map. | The destination route is explicit, although the runtime still uses a legacy target-node compatibility mapping. | Keep the sparse route encoding and preserve compatibility mapping only as a bridge. |
| local/horizontal/vertical distinction | Section III.A.2, Eq. (19) | three route families | environment/action_model.py | PASS | destination_type distinguishes local, horizontal_edge, and vertical_cloud. | No gap in route family labeling. | Keep labels in traces and audit reports. |
| one route per task | Section III.A.2 | exactly one destination or local route | environment/action_model.py | PASS | validate_explicit_choice() rejects missing/multiple destinations and self-offload. | No gap in the legality check itself. | Preserve rejection behavior and trace invalid reasons. |
| self-offload / non-neighbor rejection | Section III.A.2 / Figure 7 | horizontal offload only to legal neighbors | environment/action_model.py, environment/matchmaker.py | PASS | TopologyAdapter checks adjacency and rejects self-offload/non-neighbor choices. | No gap in legality, but the topology provenance is still user-approved/manual rather than paper-verified. | Separate legality from topology-fidelity claims. |
| action trace semantics | Algorithm 1 / trace plumbing | trace raw action plus paper semantics | phase1_tracing.py, main.py | PASS | Action traces now include raw_action_id, first_stage_decision, destination_node_id, destination_type, validity, and d_n_1/d_nk_2. | No gap in trace field availability. | Keep trace schema stable for downstream training audits. |
| replay-training readiness | Algorithm 1 | sufficient action semantics for replay training | training/trace_dataset.py, decision_makers/agent.py | PARTIAL | Trace schema is richer, but replay training still consumes reconstructed state vectors and legacy action integers. | Training readiness is improved but not yet paper-complete. | Bridge replay buffer to paper-state and delayed reward tuples later. |

## Reward Contract Audit Summary

| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |
|---|---|---|---|---|---|---|---|
| reward timing | Eq. (20), Algorithm 1 | reward collected later at completion/drop time | environment/environment.py, phase1_tracing.py, phase2_mechanisms.py | FAIL | Runtime returns step rewards immediately from queue stepping; trace code reconstructs delayed reward post hoc from lifecycle rows. | Reward is not natively delayed per completed task in the runtime. | Move to task-completion-delayed reward collection in a later phase. |
| Phi_n(t) | Eq. (21) | local/private or public completion cost | phase2_mechanisms.py, environment/queues.py | PARTIAL | Delayed reward reconstruction distinguishes completed vs dropped tasks and can label local/private vs offloaded completion by traces. | The paper cost is reconstructable, not computed natively in runtime. | Attach Phi_n(t) to native lifecycle events. |
| Phi_priv_n(t) | Eq. (22) | private completion delay | environment/task.py, phase2_mechanisms.py | PARTIAL | Completion delay can be inferred from arrival and completion timestamps in traces. | Available only as reconstructed delay, not as a native paper variable at runtime. | Store paper completion delay directly in the lifecycle trace. |
| Phi_pub_n(t) | Eq. (23) | public/offloaded completion delay | environment/task.py, phase2_mechanisms.py | PARTIAL | Offloaded task delay can be reconstructed from task lifecycle traces, but public queue timing is not exported as the paper formula. | The paper summation is not directly computed by the runtime. | Emit public queue timing required by Eq. (23). |
| drop penalty C | Eq. (20) | constant penalty for dropped tasks | phase2_mechanisms.py, environment/task.py | PARTIAL | Drop penalty is available and reconstructed as -40.0 in trace-based reporting. | Penalty exists, but not as a native delayed reward event in the runtime loop. | Bind drop penalty to native lifecycle events. |
| task-traceable replay tuple | Algorithm 1 | (s_n(t'), a_n(t'), r_n(t'), s_n(t'+1)) stored after completion | decision_makers/agent.py, training/replay_buffer.py, training/trace_dataset.py | FAIL | ReplayBuffer stores immediate transitions and DQNTrainer.push() receives dataset rows, not completion-delayed tuples keyed by task completion. | Algorithm 1 delayed replay semantics are not implemented. | Introduce completion-keyed experience buffering. |

## LSTM Contract Audit Summary

| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |
|---|---|---|---|---|---|---|---|
| L(t) | Section III.A.1, Figure 5 | W x (N+1) historical load matrix | decision_makers/agent.py, training/lstm_forecaster.py | FAIL | No native W x (N+1) load history matrix is maintained; the forecaster is a standalone regressor on simplified rows. | This is not the paper's load-history pipeline. | Implement explicit load matrix history storage. |
| W | Figure 5 / Section IV.A | lookback window for load prediction | training/lstm_forecaster.py, decision_makers/agent.py | PARTIAL | Agent maintains an LSTM history deque and LSTMForecaster uses a sequence_length parameter. | A window exists, but it is not the paper's node-wise EC load matrix window. | Rewire the lookback window around explicit node load vectors. |
| predicted next-slot load | Figure 5 | forecast for all N+1 nodes | training/lstm_forecaster.py | FAIL | LSTMForecaster predicts a single scalar target from handcrafted features, not all node loads. | Forecast output shape is not paper-faithful. | Replace scalar target prediction with multi-node load prediction. |
| LSTM integrated into HOODIE state | Section IV.A / Eq. (25) | predicted load feeds DQN input | decision_makers/agent.py | PARTIAL | Agent concatenates an LSTM hidden-history tensor with the state before the Q-network, but that is not the paper's explicit load forecast input. | There is LSTM usage, but it is an opaque history channel rather than the paper's forecast state. | Separate forecast output from policy memory. |
| EC message delay recovery | Section IV.A / algorithm narrative | fallback when EC load messages are delayed | decision_makers/agent.py, training/lstm_forecaster.py | MISSING | No explicit message-delay recovery path is implemented. | The paper's delayed-message recovery behavior is not present. | Document and implement recovery later. |

## Training-Loop Contract Audit Summary

| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |
|---|---|---|---|---|---|---|---|
| per-agent replay memory | Algorithm 1 | N_R experience buffer per agent | decision_makers/agent.py, training/replay_buffer.py | PARTIAL | Agent maintains numpy replay arrays and DQNTrainer uses ReplayBuffer(capacity=10000). | Replay memory exists, but the training harness is not the paper's per-agent delayed replay pipeline. | Bridge replay storage to completion-delayed paper tuples. |
| Q / target-Q pair | Algorithm 1 / Eq. (25) | online network plus target network | decision_makers/agent.py, training/train_phase3.py, training/trainers.py | PASS | Agent has Q_eval_network and Q_target_network; DQNTrainer has policy_net and target_net. | Model pair exists. | Keep target-network separation explicit. |
| epsilon-greedy | Algorithm 1 | epsilon-greedy action selection | decision_makers/agent.py, training/trainers.py | PASS | Agent.choose_action() and DQNTrainer.select_action() both implement epsilon-greedy selection. | No gap in exploration policy. | Keep epsilon schedule transparent in reports. |
| Double-DQN target | Algorithm 1 | target uses online argmax with target evaluation | training/trainers.py | PASS | DQNTrainer.train_step() uses next_policy_q argmax with next_target_q for ddqn. | Double-DQN is explicitly supported. | Keep algorithm labeling accurate in outputs. |
| dueling DQN | Eq. (25) / Figure 4 | value + advantage decomposition | decision_makers/agent.py | PASS | DeepQNetwork optionally builds value_layer and advantage_layer with dueling aggregation. | Architecture exists, but paper-grade training results are not claimed. | Keep the dueling flag auditable. |
| MSE loss | Algorithm 1 | mean squared TD error | decision_makers/agent.py, training/trainers.py | PASS | Agent uses loss_function() and DQNTrainer uses np.mean(td_error ** 2) with MSELoss in the scaffold. | Loss choice is aligned. | Preserve in training metadata. |
| target network copy every Ncopy | Algorithm 1 | periodic target update | decision_makers/agent.py, training/trainers.py | PASS | Agent uses replace_target_iter and trainer uses target_update_interval. | Update cadence is present. | Record the actual interval in run metadata. |
| store experience after completion | Algorithm 1 | collect D_n(t) and then store transition | main.py, decision_makers/agent.py, training/trainers.py | FAIL | main.py stores transitions immediately from each step; no completion-keyed delay buffer exists. | The runtime does not wait for task completion before pushing the replay tuple. | Introduce a completion-aware replay staging layer. |
| paper-state vs trace approximation | Algorithm 1 / Section IV | train on paper-native state, not collapsed proxies | training/trace_dataset.py, training/train_phase3.py | FAIL | TraceDataset reconstructs state from lifecycle rows when direct RL state is unavailable. | Training uses approximations rather than the native paper state pipeline. | Separate paper-state export from approximation-based reconstruction. |
| checkpoint/reporting | Training algorithm / project scaffold | save checkpoints and reports without paper-performance claims | training/train_phase3.py | PASS | Training emits checkpoints and reports with paper_claims_made false in the scaffold. | No paper-performance claim is being made. | Keep smoke-training and paper-grade results segregated. |

## Critical Blockers Before Phase 3.1

- Native paper-state vector is not produced at runtime.
- Reward is not collected as delayed task-completion tuples.
- LSTM does not implement W x (N+1) load forecasting.
- Training does not consume paper-native delayed replay tuples.

## Non-Blocking Limitations

- Phase 2 action legality and trace semantics are already explicit.
- Checkpointing and smoke training exist, but they are not paper-grade proof.
- Trace reconstruction can support audit, but it remains an approximation.

## Exact Next Recommended Sub-Phase

Phase 3.1 paper-state and delayed-reward runtime contract repair

Runtime behavior was unchanged.
No paper-performance claim is made.
