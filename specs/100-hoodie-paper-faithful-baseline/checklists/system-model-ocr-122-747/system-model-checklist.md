# System Model OCR Fidelity Checklist

Scope: OCR lines 122-747 from `resources/papers/hoodie/ocr/merged.md`, covering the System Model and the adjacent HOODIE modelling sections.

Status codes:
- `COMPLETE`: the repository evidence clearly matches the paper requirement
- `PARTIAL`: some evidence exists, but the implementation is incomplete, proxy-based, or not auditable enough
- `MISSING`: the mechanism is absent
- `UNCLEAR`: the current repository evidence is insufficient to decide
- `NOT_APPLICABLE_YET`: the mechanism is a later-phase target and is not expected yet

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| SM-01 | Three-layer architecture | IoT-to-Edge-to-Cloud with `N` EAs plus one Cloud | `environment/environment.py`, `environment/cloud.py`, `main.py` | PARTIAL | Structure exists, but current branch is still legacy baseline, not paper-faithful runtime core | Keep the architecture, then instrument explicit runtime phases and auditable node roles |
| SM-02 | Edge agent responsibility | Each EA handles its own IoT area tasks | `environment/task_generator.py`, `environment/server.py` | PARTIAL | Local ownership exists, but task traceability is incomplete in legacy paths | Preserve current ownership mapping and expose task-level lifecycle fields |
| SM-03 | Non-divisible tasks | Tasks are computed as a whole by one destination | `environment/task.py`, `environment/queues.py` | PARTIAL | Non-divisible assumption appears implicit, not contractually audited | Add explicit task-level lifecycle validation in later phases |
| SM-04 | Action set | Local, horizontal, vertical actions | `environment/action_model.py`, `environment/matchmaker.py`, `main.py` | COMPLETE | Legal action families are now explicit and traceable, but paper-level topology verification remains a separate concern | Keep the explicit action contract and retain topology provenance |
| SM-05 | Topology legality | Offloading must respect Figure 7 adjacency | `environment/action_model.py`, `environment/matchmaker.py`, `environment/environment.py` | PARTIAL | Adjacency-based legality is enforced by the runtime topology matrix, but Figure 7 compliance is still not proven against the paper matrix | Keep the topology contract and document the recovered-matrix limitation |
| SM-06 | Task arrival process | Bernoulli arrivals per EA per slot | `environment/task_generator.py` | COMPLETE | Arrival process exists, but trace-level confirmation is limited by current audit data | Retain the process and export arrival diagnostics |
| SM-07 | Task size set | Discrete task sizes from the paper's set | `hyperparameters/hyperparameters.json`, `environment/task_generator.py` | PARTIAL | Size set is configurable, but OCR fidelity of the exact discrete set is not guaranteed in current evidence | Keep the configuration path and align the set explicitly to the OCR contract |
| SM-08 | Processing density | Per-task cycles/bit parameter | `hyperparameters/hyperparameters.json`, `environment/task.py` | PARTIAL | Parameter exists, but traceable paper contract is not yet formalized | Pin the parameter in a spec contract and validate units |
| SM-09 | Timeout | Per-task maximum waiting time in slots | `hyperparameters/hyperparameters.json`, `environment/task.py` | PARTIAL | Timeout exists, but completion/drop semantics are legacy and not yet paper-grade | Separate completion from drop in the runtime contract |
| SM-10 | Private queue | FIFO private queue per EA | `environment/queues.py`, `environment/server.py` | PARTIAL | Queue exists, but waiting/completion semantics are not fully paper-auditable | Add explicit queue exit status and task-level traces |
| SM-11 | Private queue service | Service time from task size, density, CPU, slot duration | `environment/queues.py` | PARTIAL | Legacy service math exists, but paper-faithful completion/drop separation is not yet auditable | Repair queue equations in the runtime core phase |
| SM-12 | Offloading queue | FIFO offloading queue per EA | `environment/queues.py`, `environment/server.py` | PARTIAL | Queue exists, but offloading exit is not yet separated from final completion in a paper-grade way | Add explicit offloading completion status and destination insertion trace |
| SM-13 | Horizontal offload rate | `R_H` used for EA-to-EA offloading | `hyperparameters/hyperparameters.json`, `environment/queues.py` | PARTIAL | The rate exists, but auditable paper contract is not yet isolated from legacy logic | Lock the parameter contract and validate the units |
| SM-14 | Vertical offload rate | `R_V` used for EA-to-Cloud offloading | `hyperparameters/hyperparameters.json`, `environment/queues.py` | PARTIAL | The rate exists, but not yet isolated in a paper contract | Keep the parameter and expose it in runtime diagnostics |
| SM-15 | Public queues | Source-specific public queues at destination nodes | `environment/queues.py`, `environment/cloud.py` | PARTIAL | Public queue machinery exists, but auditability is weak and CPU sharing is legacy-weighted | Rework public queue traces and equal-share semantics in a later mechanism phase |
| SM-16 | Active public queues | Active if incoming task exists or backlog remains | `environment/queues.py` | PARTIAL | Active-set semantics are present in spirit, but not yet fully audited as a contract | Export active-set traces and validate them against queue occupancy |
| SM-17 | Public CPU sharing | Equal sharing across active queues | `environment/queues.py`, `phase2_mechanisms.py` | COMPLETE | Phase 2 repaired this mechanism, but it is still not the full paper rebuild | Keep this repair and retain validation artifacts |
| SM-18 | Public queue length | Length must be explicit and time-varying | `environment/queues.py`, `phase1_tracing.py` | PARTIAL | Queue lengths are traceable, but not yet fully aligned to paper state semantics | Retain queue traces and define queue-length units clearly |
| SM-19 | Historical load matrix | `L(t)` of size `W x (N+1)` | `environment/environment.py`, `phase1_tracing.py` | PARTIAL | Historical load exists as trace input, but forecast pipeline is not paper-grade | Add a load-history contract and LSTM forecast audit |
| SM-20 | Load sharing | EAs and Cloud share load info via ECs / pub-sub | `environment/environment.py`, `phase2_mechanisms.py` | UNCLEAR | Pub-sub / recovery mechanism is not convincingly simulated in current evidence | Document as a gap until explicit communication modeling exists |
| SM-21 | State vector | `[\eta_n(t), w_priv, w_off, l_n^pub(t-1), L(t)]` | `training/trace_dataset.py`, `decision_makers/agent.py` | PARTIAL | Current training summary reports `state_dim=2`, which is not the paper state vector | Replace proxy state descriptors with an auditable paper-state export |
| SM-22 | Public queue footprint | Per-source public queue lengths are part of state | `phase1_tracing.py`, `training/trace_dataset.py` | PARTIAL | Some footprint data exists, but not in the paper-native state format | Export the footprint with explicit source/destination indexing |
| SM-23 | Forecasting input | LSTM consumes load history to forecast next-slot load | `decision_makers/agent.py`, `training/lstm_forecaster.py` | PARTIAL | LSTM exists, but current evidence does not show a fully auditable forecast/history pipeline | Split forecast auditing from DQN input plumbing |
| SM-24 | DRL action space | Full state-action space over local/offload choices | `environment/action_model.py`, `environment/matchmaker.py`, `decision_makers/agent.py`, `training/trace_dataset.py` | PARTIAL | The action space is now topology-driven and includes local/horizontal/cloud choices, but the recovered Figure 7 topology is still not paper-verified enough for a hard completion claim | Keep the explicit action contract and avoid claiming exact paper topology fidelity yet |
| SM-25 | Reward semantics | Reward collected when task completes or drops | `phase2_mechanisms.py`, `phase1_tracing.py` | PARTIAL | Reward reconstruction exists, but native delayed replay is not yet the canonical runtime mechanism | Keep the reconstructed artifacts, then move reward handling into the runtime contract |
| SM-26 | Delay cost | Reward equals negative completion delay | `phase2_mechanisms.py` | PARTIAL | Delay can be reconstructed from traces, but current runtime does not yet expose a paper-native delayed reward path | Add task-linked delayed reward events in the runtime phase |
| SM-27 | Drop penalty | Dropped task gets constant penalty `-C` | `phase2_mechanisms.py` | PARTIAL | Penalty exists in reconstruction, but not as a native audit-ready event stream | Keep the value and attach it to task-level reward events later |
| SM-28 | Optimization objective | Minimize delay and loss ratio | `specs/100-hoodie-paper-faithful-baseline/spec.md` | PARTIAL | Target is documented, but current runtime evidence is still only proxy-level | Use the spec as the contract and do not claim numerical reproduction yet |
| SM-29 | HOODIE model | Dueling DQN with LSTM-based state encoding | `decision_makers/agent.py`, `training/lstm_forecaster.py` | PARTIAL | The model family exists, but the forecast/state pipeline is not yet paper-auditable end to end | Reuse existing modules and tighten the model contract |
| SM-30 | Training algorithm | 5000 episodes, epsilon schedule, target updates | `decision_makers/agent.py`, `training/train_phase3.py` | PARTIAL | Training now exists in scaffold form, but 5000-episode paper-grade training has not been performed | Separate smoke training from paper-grade training claims |
| SM-31 | Inference phase | Zero-epsilon exploitation only | `decision_makers/agent.py` | PARTIAL | Inference path exists, but current validation does not prove paper-faithful deployment behavior | Keep inference logic but audit it independently |
| SM-32 | Complexity / convergence discussion | Complexity is analytical, convergence is empirical | `resources/papers/hoodie/ocr/merged.md` | COMPLETE | This is a paper-text item, not a simulator capability | Reference the paper text only; do not invent convergence claims |
| SM-33 | Pub-sub communication | EC-mediated pub-sub broadcast of load/public queue info | `resources/papers/hoodie/ocr/merged.md` | MISSING | The current repository does not yet simulate this protocol in a paper-grade way | Mark as a later mechanism repair item, not a completed feature |
| SM-34 | Recovery mechanism | LSTM-based fallback when messages are delayed | `resources/papers/hoodie/ocr/merged.md`, `training/lstm_forecaster.py` | UNCLEAR | Text exists, but current code does not prove the recovery mechanism is operational | Treat as a documented gap until an auditable simulation path exists |
| SM-35 | Baseline family | HOODIE, RO, FLC, VO, HO, BCO, MLEO | `phase2_mechanisms.py` | PARTIAL | Baseline aliases exist, but they are not guaranteed to be paper-perfect reimplementations | Keep them labeled as proxies unless paper verification is completed |
| SM-36 | Table 4 parameters | Paper parameter registry and units | `hyperparameters/hyperparameters.json`, `resources/papers/hoodie/recovered/paper-parameter-registry.json` | PARTIAL | Parameter evidence exists, but there is no single audited contract binding code to Table 4 yet | Create a parameter contract before paper-faithful validation |
| SM-37 | 200 validation episodes | Paper-grade validation mode over 200 episodes | `training/train_phase3.py`, audit artifacts | MISSING | Current validation is smoke-level and not a full paper-grade evaluation loop | Add a dedicated validation phase later |
| SM-38 | Figures 8-11 | Paper figure-generation workflows | `artifacts/phase3_training_*`, `artifacts/phase2_mechanism_repair/` | MISSING | No paper-faithful figure pipeline is present | Do not claim figures until the validation and evaluation stack exists |
| SM-39 | Training data export | Reproducible trace-to-training dataset | `training/trace_dataset.py`, `artifacts/phase3_trace_smoke/` | PARTIAL | Data reconstruction works, but it is still reconstructed from legacy traces | Keep the reconstruction explicit and document approximations |
| SM-40 | Paper-faithful claim | Simulator already matches paper mechanisms | Repository state overall | MISSING | The repository still contains proxy behavior and reconstructed artifacts | Do not claim paper-faithful completion yet |

## S. Experimental Setup and Parameter Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| S-01 | Python implementation context | Python implementation of the full workflow | `main.py`, `training/train_phase3.py` | PARTIAL | Python exists, but paper-grade output contract is not fully present | Keep Python as the implementation base and add explicit output contracts |
| S-02 | PyTorch note | Paper used PyTorch for DRL/LSTM experiments | `requirements.txt`, `training/lstm_forecaster.py` | PARTIAL | PyTorch is present, but version/env contract is not yet tied to experimental outputs | Record the version only as environment metadata, not as a paper claim |
| S-03 | CUDA note | Paper mentions CUDA-capable training environment | Repository environment only | UNCLEAR | Hardware environment is not part of the repo contract | Record as informational metadata only if a run actually uses it |
| S-04 | Table 4 as default contract | Use Table 4 values as default parameter set | `hyperparameters/hyperparameters.json`, OCR recovery files | PARTIAL | Parameters exist, but not in a single authoritative contract file | Create a parameter contract artifact before paper-grade evaluation |
| S-05 | Arrival probability P | Default `P=0.5` | `environment/task_generator.py`, trace artifacts | COMPLETE | Default exists, but output-side recording still needs explicit contract | Keep it as the default and record it in run config |
| S-06 | Horizontal rate | `R_H=30 Mbps` | `hyperparameters/hyperparameters.json` | PARTIAL | Present as config, but not yet tied to figure output contracts | Keep and surface in run_config |
| S-07 | Vertical rate | `R_V=10 Mbps` | `hyperparameters/hyperparameters.json` | PARTIAL | Present as config, but not yet tied to figure output contracts | Keep and surface in run_config |
| S-08 | Task size set | `[2, 2.1, ..., 5]` Mbits | `environment/task_generator.py` | PARTIAL | The exact set is not yet contractually exported for output validation | Export the discrete size set in parameter metadata |
| S-09 | Processing density | `0.297` gigacycles/Mbit | `hyperparameters/hyperparameters.json` | PARTIAL | Parameter exists, but units should be locked in metadata | Add units to parameter contract and validation reports |
| S-10 | Default agent count | `N=20` EAs | `hyperparameters/hyperparameters.json`, Phase 3 artifacts | COMPLETE | Current outputs use `N=20`, but figure sweeps need explicit provenance | Record `N` in all run configs and summaries |
| S-11 | Figure 7 topology | Topology graph must be the paper topology | `resources/papers/hoodie/recovered/topology-g.json` | PARTIAL | Recovered topology exists, but output artifacts do not yet bind experiments to it | Serialize topology in output artifacts and run config |
| S-12 | Private CPU | `5 GHz` private CPU | `hyperparameters/hyperparameters.json` | PARTIAL | Config exists but is not yet part of an auditable parameter contract | Add to shared parameter contract |
| S-13 | Public CPU | `5 GHz` public CPU for EAs | `hyperparameters/hyperparameters.json`, phase 2 repair | COMPLETE | Equal-share repair exists, but needs output-contract linkage | Keep and record in run metadata |
| S-14 | Cloud CPU | `30 GHz` public CPU | `hyperparameters/hyperparameters.json` | PARTIAL | Config exists but not yet bound to figure datasets | Add to parameter contract and validation report |
| S-15 | Training episodes | `N_E=5000` | OCR text, training scaffold | PARTIAL | Current Phase 3 smoke/full runs are not 5000-episode paper training | Distinguish smoke training from paper-grade training in artifacts |
| S-16 | Episode length | `T=110` slots | `hyperparameters/hyperparameters.json` | COMPLETE | Runtime uses the slot count, but the first 100 / last 10 split still needs explicit output recording | Record action/drain split in run config |
| S-17 | Action-enabled phase | First 100 slots are action-enabled | Phase 1/2 audit docs | PARTIAL | The split exists in the restoration plan, but not all outputs encode it | Record it in run config and validation summaries |
| S-18 | Drain phase | Last 10 slots are drain-only | Phase 1/2 audit docs | PARTIAL | Drain phase exists conceptually, but output artifacts do not yet make it first-class | Add drain-phase metadata to run outputs |
| S-19 | Slot duration | `Delta=0.1 sec` | `hyperparameters/hyperparameters.json` | COMPLETE | Parameter exists, but unit consistency needs validation metadata | Keep and export the unit explicitly |
| S-20 | Timeout | `phi=20` slots / `2 sec` | `hyperparameters/hyperparameters.json` | COMPLETE | Present, but figure 10 strict-timeout regime still needs a separate output contract | Retain and export timeout regime metadata |
| S-21 | Learning rate | `7e-7` default paper value | OCR text, training scaffold | PARTIAL | The code has training settings, but no paper-grade convergence dataset | Track sweep values in figure 8 outputs later |
| S-22 | Discount factor | `gamma=0.99` default | OCR text, training scaffold | PARTIAL | Present in the scaffold, but not yet validated as part of paper-grade curves | Export gamma in training-run configs |
| S-23 | Hidden layers | `3 x 1024` | `decision_makers/agent.py`, training scaffold | PARTIAL | Model structure exists, but the figure contract is not yet audited | Record architecture metadata in model summaries |
| S-24 | Optimizer | Adam | `training/train_phase3.py` | PARTIAL | Optimizer exists, but not yet tied to figure data artifacts | Export optimizer type in training config |
| S-25 | Loss | MSE | `training/train_phase3.py` | PARTIAL | Loss exists in the scaffold, but not yet part of output contracts | Export loss definition in report metadata |
| S-26 | Target copy interval | `Ncopy=2000` | OCR text, training scaffold | PARTIAL | Exists in paper contract, not yet proven in figure outputs | Add to training metadata and future validation |
| S-27 | LSTM window | `W=10` | `training/lstm_forecaster.py` | PARTIAL | Window exists, but forecast/output coupling is not yet paper-grade | Export history window in metric contract |
| S-28 | LSTM hidden size | `1 x 20` | `training/lstm_forecaster.py` | PARTIAL | Present as scaffold, but not yet validated as part of output flows | Record architecture details in model metadata |
| S-29 | Replay memory | `10000` | `decision_makers/agent.py`, training scaffold | PARTIAL | Replay exists, but output contracts do not yet expose it | Record replay memory size in run config |
| S-30 | Drop penalty | `C=40` | `phase2_mechanisms.py` | COMPLETE | Penalty exists, but figure-grade validation still needs traceable reward data | Keep and record in reward metadata |
| S-31 | Batch size | `64` | `training/train_phase3.py` | PARTIAL | Present for smoke/full training, but not enough for paper claims | Export training hyperparameters in artifact metadata |
| S-32 | Figure 8 contract | Training convergence curves | No figure 8 dataset artifacts yet | MISSING | Current Phase 3 training is not the 5000-episode output contract | Do not generate Figure 8 until the dataset contract exists |
| S-33 | Figure 9 contract | Behavior and scalability curves | No figure 9 datasets yet | MISSING | No paper-grade sweep outputs | Create explicit sweep datasets and summaries later |
| S-34 | Figure 10 contract | Baseline comparisons | `phase2_mechanisms.py` baseline proxies | PARTIAL | Baseline aliases exist, but no paper-grade comparison datasets yet | Keep proxies labeled and do not claim paper comparisons |
| S-35 | Figure 11 contract | LSTM ablation | `training/lstm_forecaster.py` scaffold only | PARTIAL | LSTM exists, but ablation output does not exist yet | Delay Figure 11 until LSTM integration is auditable |
| S-36 | Validation episodes | `200` validation episodes | Smoke validation only | MISSING | Current validation is not paper-grade | Add a dedicated validation phase later |

## T. Figure 7 Topology Output Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| T-01 | Adjacency matrix graph | `G` must be represented as a graph | `resources/papers/hoodie/recovered/topology-g.json` | PARTIAL | Recovered data exists, but not yet tied to output artifacts | Export adjacency in a shared topology artifact |
| T-02 | 20 EAs in graph | Topology must contain 20 EAs | Current baseline config | COMPLETE | `N=20` is already used, but the output contract is not explicit | Record node count in topology metadata |
| T-03 | Match Figure 7 | Topology must match the paper graph | Recovered topology file | UNCLEAR | OCR recovery is not yet paper-verified enough for a hard claim | Validate against the OCR figure and note any uncertainties |
| T-04 | Topology artifact | Output should include adjacency matrix JSON/CSV | No dedicated figure 7 output directory yet | MISSING | No figure-7-specific output contract exists | Add `figure7_topology/` outputs later |
| T-05 | Topology plot or edge list | Output should include graph visualization or edge list | No dedicated plot artifact | MISSING | No graph plot artifact is present | Add plot or edge-list export later |
| T-06 | Action legality linkage | Topology should drive horizontal action legality | `environment/action_model.py`, `environment/matchmaker.py`, phase 2 repair | COMPLETE | Horizontal legality is now explicit in the runtime action contract, but the recovered topology provenance still needs to be recorded separately | Record topology provenance in run config and keep the legality contract explicit |
| T-07 | Run config record | Topology used in experiments must be recorded | Current run artifacts do not yet standardize this | MISSING | Topology provenance can be lost | Add `run_config.json` with topology metadata |

## U. Figure 8 Training Convergence Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| U-01 | Figure 8a | Average reward vs episode for learning-rate sweep | `training/train_phase3.py` smoke/full training only | MISSING | No sweep dataset exists | Build a 5000-episode sweep pipeline later |
| U-02 | Learning rates | `[1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7]` | OCR text only | MISSING | Sweep values are not yet exported as figure data | Add sweep config artifacts later |
| U-03 | Figure 8b | Average reward vs episode for gamma sweep | No dataset artifacts | MISSING | No gamma sweep evidence | Add sweep runs and aggregate curves later |
| U-04 | Gammas | `[0.2, 0.4, 0.6, 0.8, 0.99]` | OCR text only | MISSING | Not yet in output contract | Include in future figure 8 configs |
| U-05 | 5000 episodes | Training curves must span 5000 episodes | Phase 3 smoke/full training are below this | MISSING | Current runs are not paper-grade | Keep smoke training separate from paper training |
| U-06 | Reward averaging | Average reward across distributed agents | Trace reconstruction only | PARTIAL | Average reward exists in traces but not as paper convergence output | Define averaging in future metric contract |
| U-07 | Output dataset | `figure8_training_curves.csv` required | None | MISSING | No raw data | Add dedicated data export later |
| U-08 | Output config | `figure8_config.json` required | None | MISSING | No config artifact | Add config artifact later |
| U-09 | Output summary | `figure8_summary.json` required | None | MISSING | No summary artifact | Add summary artifact later |
| U-10 | Seed / metadata | Seed, `N`, `P`, hyperparameters, duration required | Some metadata exists in training reports | PARTIAL | Not yet standardized across figure datasets | Standardize metadata in a shared run registry |
| U-11 | Current 20-epoch training | Phase 3.2 20-epoch training is not sufficient | `artifacts/phase3_training_full_real/` | COMPLETE | This is correctly not treated as paper-grade evidence | Keep it labeled as smoke/full training only |
| U-12 | State/action approximation risk | Must flag current approximation | `training/trace_dataset.py` summary warnings | COMPLETE | Risk is documented, but not yet resolved | Continue to mark approximations explicitly |

## V. Figure 9 HOODIE Behavior and Scalability Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| V-01 | Figure 9a | Average reward vs arrival probability for `N=[10,15,20]` | No figure 9 dataset | MISSING | No sweep outputs | Add sweep pipeline later |
| V-02 | Figure 9b | Action type distribution for `P=[0.1,0.3,0.5,0.7,0.9]` | Phase 1 action trace only | PARTIAL | Action traces exist, but not paper-grade sweep outputs | Preserve traces and add summary datasets later |
| V-03 | Figure 9c | Average reward vs CPU capacity | No dataset | MISSING | No CPU sweep outputs | Add later |
| V-04 | Figure 9d | Average reward vs number of agents under traffic regimes | No dataset | MISSING | No traffic-regime sweep outputs | Add later |
| V-05 | Figure 9e | Average reward vs number of agents under data-rate scenarios | No dataset | MISSING | No data-rate sweep outputs | Add later |
| V-06 | Validation episodes | 200 validation episodes | Smoke validation only | MISSING | Paper-grade validation absent | Build dedicated validation phase later |
| V-07 | Optimally trained Q-models | Sweeps should use optimally trained models | Phase 3 smoke/full training exists only as scaffold/smoke | PARTIAL | Not enough to claim optimal paper models | Keep training outputs honest and non-paper-claiming |
| V-08 | Figure 9 datasets | CSV outputs required | None | MISSING | No raw data artifacts | Add figure 9 raw datasets later |

## W. Figure 10 Comparative Baseline Analysis Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| W-01 | Baseline set | RO, FLC, VO, HO, BCO, MLEO, HOODIE | `phase2_mechanisms.py` aliases | PARTIAL | Baseline labels exist, but proxy implementations may not be paper-perfect | Keep them labeled as proxies unless independently verified |
| W-02 | Figure 10a | Delay vs arrival probability | No dataset | MISSING | No comparison artifact | Add later |
| W-03 | Figure 10d | Drop ratio vs arrival probability | No dataset | MISSING | No comparison artifact | Add later |
| W-04 | Figure 10b | Delay vs CPU capacity | No dataset | MISSING | No comparison artifact | Add later |
| W-05 | Figure 10e | Drop ratio vs CPU capacity | No dataset | MISSING | No comparison artifact | Add later |
| W-06 | Figure 10c | Delay vs timeout (high timeout regime) | No dataset | MISSING | No comparison artifact | Add later |
| W-07 | Figure 10f | Drop ratio vs timeout (strict timeout regime) | No dataset | MISSING | No comparison artifact | Add later |
| W-08 | Delay definition | Average delay over non-dropped tasks | Phase 2 trace reconstruction | PARTIAL | Delay exists as reconstructed metric, but output convention is not yet standardized | Separate physical delay from plot sign convention later |
| W-09 | Drop ratio definition | Dropped / arrived tasks | Phase 1/2 metrics | COMPLETE | Metric exists, but not yet figure-dataset bound | Keep definition in metric registry |
| W-10 | Figure 10 config | `figure10_config.json` required | None | MISSING | No config artifact | Add later |
| W-11 | Baseline registry | `baseline_policy_registry.json` required | Phase 2 baseline mapping only | PARTIAL | Registry exists conceptually, but not as a figure artifact | Export a formal registry later |
| W-12 | Sanity report | `figure10_baseline_sanity_report.md` required | None | MISSING | No sanity report | Add later |
| W-13 | Validation episodes | 200 validation episodes | Smoke validation only | MISSING | Not paper-grade | Add later |

## X. Figure 11 LSTM Ablation Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| X-01 | Compare with/without LSTM | Need two variants | `training/lstm_forecaster.py` scaffold | PARTIAL | LSTM exists, but ablation evidence is not yet output-ready | Keep separate model variants in future output contract |
| X-02 | Metric | Average task delay vs training episodes | Trace metrics and training reports | PARTIAL | No paper-grade ablation dataset yet | Add a dedicated ablation dataset later |
| X-03 | N=20 | Use 20 EAs | Baseline config | COMPLETE | N is already in use | Record in config metadata |
| X-04 | Optimal gamma/lr | Use optimal values from Section V.A | Training scaffold only | MISSING | No validated optimal settings available | Do not fabricate optimality |
| X-05 | P=0.3 | Arrival probability for ablation | No ablation run | MISSING | Not present in outputs | Add later |
| X-06 | phi=1 sec | Deadline regime | No ablation run | MISSING | Not present in outputs | Add later |
| X-07 | Figure 11 dataset | `figure11_lstm_ablation.csv` required | None | MISSING | No raw data | Add later |
| X-08 | Figure 11 config | `figure11_config.json` required | None | MISSING | No config artifact | Add later |
| X-09 | Model variants | `hoodie_with_lstm` and `hoodie_without_lstm` | `training/lstm_forecaster.py` + agent scaffolds | PARTIAL | Variants are not yet shown as paper-grade ablation outputs | Export explicit variants later |
| X-10 | No fabricated benefit | Do not invent LSTM gain | Existing summary warnings | COMPLETE | Good: no bogus claim should be made | Keep any ablation honest |
| X-11 | Recovery mechanism separation | Recovery use of LSTM must be tracked separately | OCR contract only | UNCLEAR | The recovery mechanism is not clearly separated from ablation in current outputs | Separate the two in future artifacts |

## Y. Validation Episode Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| Y-01 | 5000-episode training where required | Training curves require 5000 episodes | Phase 3 smoke/full training below this | MISSING | Not paper-grade | Keep smoke training separate |
| Y-02 | 200-episode validation | Behavior/comparison figures use 200 validation episodes | Smoke validation only | MISSING | Not implemented as a dedicated paper validation loop | Add later |
| Y-03 | Exploitative inference | Validation uses epsilon=0 | Inference path exists conceptually | PARTIAL | Not recorded in figure datasets yet | Record epsilon and policy in validation configs |
| Y-04 | Validation artifacts | Must record seed, episodes, policy, sweep value, scenario name | Current reports vary by phase | PARTIAL | No standardized validation registry yet | Add a shared validation artifact schema |
| Y-05 | Per-episode metrics | Retained for validation runs | Trace artifacts exist | PARTIAL | Not yet standardized across output folders | Keep per-episode traces and define schemas |
| Y-06 | Aggregate metrics | Mean/std/min/max where applicable | Phase 3 training report includes summaries | PARTIAL | Needs to be standardized for figure outputs | Add to metric contract |
| Y-07 | Traceability to run_config | All generated figure datasets must trace back | None | MISSING | No run registry | Add run registry before figure claims |

## Z. Output Artifact Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| Z-01 | `artifacts/paper_outputs/` root | Required output layout | Current artifacts are spread across phase folders | MISSING | Output structure is not standardized | Introduce a paper-output directory contract later |
| Z-02 | `figure7_topology/` | Topology outputs | No dedicated folder | MISSING | No figure-specific topology outputs | Add later |
| Z-03 | `figure8_training_convergence/` | Training convergence outputs | No dedicated folder | MISSING | No figure-8 outputs | Add later |
| Z-04 | `figure9_behavior_scalability/` | Behavior/scalability outputs | No dedicated folder | MISSING | No figure-9 outputs | Add later |
| Z-05 | `figure10_baseline_comparison/` | Baseline comparison outputs | No dedicated folder | MISSING | No figure-10 outputs | Add later |
| Z-06 | `figure11_lstm_ablation/` | LSTM ablation outputs | No dedicated folder | MISSING | No figure-11 outputs | Add later |
| Z-07 | `shared/run_registry.json` | Shared run registry | No registry | MISSING | Reproducibility gap | Add later |
| Z-08 | `shared/parameter_contract.json` | Shared parameter contract | No registry | MISSING | Parameter provenance gap | Add later |
| Z-09 | `shared/baseline_policy_registry.json` | Shared baseline registry | Partial proxies only | PARTIAL | Registry exists conceptually but not as a formal artifact | Add later |
| Z-10 | `shared/metric_definitions.json` | Shared metric definitions | No registry | MISSING | Metric ambiguity remains | Add later |
| Z-11 | Raw CSV before plot | No figure accepted without raw data | Existing phase artifacts vary | PARTIAL | Raw data conventions are not standardized | Enforce raw-data-first artifact rules |
| Z-12 | Config before raw data | No raw data accepted without config | Not standardized | MISSING | Reproducibility gap | Require config-first artifact generation |

## AA. Metric Definitions Contract

| ID | Paper element | Required by paper | Current evidence | Status | Gap / risk | Recommended next action |
|---|---|---|---|---|---|---|
| AA-01 | Average reward | Mean reward across validation/training window | Phase 3 report summaries | PARTIAL | Definition is not standardized across figure outputs | Put the definition in `metric_definitions.json` |
| AA-02 | Accumulated reward | Sum of rewards over an episode/window | Training reports only | PARTIAL | Needs standardization and traceability | Add to shared metric contract |
| AA-03 | Task delay | Physical delay from arrival to completion | Phase 2 reconstructed metrics | PARTIAL | Delay sign convention can be confused with plot conventions | Store physical delay separately from sign convention |
| AA-04 | Delay sign convention | Plotting may negate delay values | OCR text only | UNCLEAR | Plot-specific sign convention not standardized in artifacts | Record sign convention explicitly in plots and summaries |
| AA-05 | Drop ratio | Dropped tasks / total arrived tasks | Phase 1/2 metrics | COMPLETE | Good metric, but still needs figure artifact mapping | Keep exact formula in metric registry |
