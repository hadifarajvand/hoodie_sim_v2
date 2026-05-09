# Paper Mechanism Registry

Read-only warning: this registry is analysis-only and does not change simulator behavior.

| Field | Value |
|---|---|
| Registry Version | 016 |
| Read Only | true |
| Behavior Changes | false |
| Passed | true |

## Blocking Gaps
- system_topology: Topology adjacency is not present as a structured artifact. (blocking)
- timeout_and_drop: Timeout and Drop requires paper-faithful validation before any repair feature. (high)
- reward_definition: Reward Definition requires paper-faithful validation before any repair feature. (high)

## High-Risk Assumptions
- cpu_capacity: Evaluation sweeps over CPU capacity exist in the paper, but the registry only captures the documented values, not a new sweep. (high)
- link_data_rates: Exact topology-specific rate mapping is not fully explicit in the OCR excerpts. (high)
- transmission_delay: The exact closed-form transmission-delay equation is not recovered here. (medium)
- computation_delay: The precise delay decomposition is not fully restated in the OCR snippets. (medium)
- timeout_and_drop: The OCR exposes timeout values, but the exact terminal accounting path should be verified against the runtime kernel. (blocking)
- reward_definition: The exact equation text is not reconstructed here, only the paper references and convention are preserved. (blocking)
- dqn_double_dueling_lstm_training: Exact network topology and training hyperparameters are only partially visible in OCR. (high)

## Mechanism Entries
### M001 - System Topology
- Category: `system_topology`
- Paper Status: `partially_documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `blocking`
- Next Action: `requires_reference_kernel`
- Expected Behavior: A multi-server edge topology is defined with an adjacency matrix G over edge agents and cloud connectivity.
- Missing Details: Topology adjacency matrix G is not present as a structured artifact.
- Implementation Gaps: Structured adjacency artifact is absent from the repository., Topology evidence is conceptual rather than encoded as a reusable registry artifact.
- Validation Implications: A reference kernel or topology artifact is needed before topology assertions can be made beyond the OCR text.
- Evidence:
  - [Section V.A / Table 4] learning. C. PROPOSED SCHEME AND CONTRIBUTIONS In this paper, we propose a Hybrid Computation Offloading via Distributed Deep Reinforcement Learning (HOODIE),appropriate for delay-aware decision-making in CEC. Under a multi-server topology graph of CEC, HOODIE leverages distributed and autonomous DRL agents to intelligently assist on task placement decisions. The objective of HOODIE is to jointly optimize task computation delay and CEC throughput (or minimal drop rate) by dynamically balancing hybrid task flows across CEC resources. Unlike existing offloading schemes that rely on (i) iterative approaches with high inference delay (as in heuristic methods),
### M002 - Edge Agents and Cloud
- Category: `edge_agents_and_cloud`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `low`
- Next Action: `keep`
- Expected Behavior: Each edge agent and the cloud are part of the cloud-edge continuum and participate in hybrid offloading decisions.
- Missing Details: Precise boundary semantics between EC and EA roles are not fully formalized in the OCR text.
- Implementation Gaps: Project mapping is clear, but the OCR is more descriptive than operational for controller relationships.
- Validation Implications: The registry should not infer controller behavior beyond the paper's set definitions.
- Evidence:
  - [Table 3 / system model symbols] dge Agent or vertically towards the Cloud. TABLE 2. Mathematical symbols <html><body><table><thead><tr><td></td><td>Symbol Meaning [Unit]</td><td>Symbol</td><td>Meaning [Unit]</td></tr></thead><tbody><tr><td>N</td><td>Set of EAs and Cloud</td><td>\$\textbackslash\{\}overline\{\{\textbackslash\{\}psi\_\{n\}\textasciicircum{}\{\{p r i v\}\}(t)\}\}\$</td><td>Completion time slot of private task \$u\_\{n\}(t)\$</td></tr><tr><td>3</td><td>Set of EAs</td><td>\$w\_\{n\}\textasciicircum{}\{\{p r i v\}\}(t)\$</td><td>Waiting time of private task [time slots] \$u\_\{n\}(t)\$</td></tr><tr><td>M</td><td>Set of ECs</td><td>\$f\_\{n\}\textasciicircum{}\{E A,p r i
### M003 - Action Space
- Category: `action_space`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `high`
- Next Action: `inspect_source`
- Expected Behavior: Agents choose among local processing, horizontal offload, and vertical offload, with single-step action semantics.
- Missing Details: Multi-hop action semantics are intentionally excluded by the paper's single-step constraint, but the exact legality matrix is not fully exposed.
- Implementation Gaps: Need explicit reference kernel if action legality must be validated independently of current policy code.
- Validation Implications: Action legality must be tested against topology and queue semantics.
- Evidence:
  - [action_space] ></tr><tr><td>DRL</td><td>Deep Reinforcement Learning</td></tr><tr><td>EA</td><td>Edge Agent</td></tr><tr><td>EC</td><td>Edge Controller</td></tr><tr><td>FIFO</td><td>First In First Out</td></tr><tr><td>FLC</td><td>Full Local Computing</td></tr><tr><td>HO</td><td>Horizontal Offloader</td></tr><tr><td>HOODIE</td><td>Hybrid Computation Offloading via Distributed Deep Reinforcement Learning</td></tr><tr><td>ID</td><td>in Delay-aware Cloud-Edge Continuum</td></tr><tr><td>IoT</td><td>Identifier</td></tr><tr><td></td><td>Internet of Things</td></tr><tr><td>LSTM</td><td>Long Short-Term Memory</td></tr><tr><td>MEC</td><td>Mobile Edge Computing</td></tr><t
### M004 - Local Computation
- Category: `local_computation`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `inspect_source`
- Expected Behavior: Tasks may be processed locally by an EA using its private compute capacity.
- Missing Details: Exact local-computation timing formula is not fully restated in the OCR snippets we rely on.
- Implementation Gaps: Need a reference kernel to verify local-compute timing from paper semantics alone.
- Validation Implications: Local-compute duration and completion order should be covered by environment-level tests.
- Evidence:
  - [local_computation] y minimize task latency and drop rate,supporting both vertical (edge-to-cloud) and horizontal (edge-to-edge) task flows. This is achieved by enabling dual functionality at each agent (i.e. each agent may serve either as local task processor or as host for offloaded tasks). This hybrid model significantly enhances resource utilization and avoids bottlenecks. The proposed scheme enforces autonomy in the distributed decision-making, with each agent not knowing the decisions of the other agents. In this context,HOODIES facilitates the process for removing old or adding new agents in CC. HOODIE agents exploit the Double and Dueling DRL techniques for lear
### M005 - Horizontal Offloading
- Category: `horizontal_offloading`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `high`
- Next Action: `requires_reference_kernel`
- Expected Behavior: Tasks can be offloaded from one EA to a neighboring EA through the horizontal link and processed via a public queue.
- Missing Details: Neighbor legality depends on topology adjacency, which is not recovered as structured data.
- Implementation Gaps: Need adjacency-backed validation before horizontal routing can be treated as fully proven.
- Validation Implications: Offload routing must be checked against topology and queue behavior.
- Evidence:
  - [horizontal_offloading] Edge and Cloud. A. TOWARDS HYBRID TASK OFFLOADING AND DISTRIBUTEDML In the context of CEC, task offloading involves dynamically deciding whether to process tasks locally at the edge, offload them to another edge node (horizontal offloading) or to a cloud server (vertical offloading), under time-varying task arrival traffic. The primary goal of task offloading is to optimize system performance by minimizing target indicators, such as latency, energy consumption, and task drop ratio, to prevent bottlenecks and ensure smooth and efficient flow of CEC operations. As an optimization problem, task offloading is constrained by several factors, including limi
### M006 - Vertical Offloading
- Category: `vertical_offloading`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `inspect_source`
- Expected Behavior: Tasks can be offloaded from an EA to the cloud for processing through the vertical link.
- Missing Details: Cloud queue semantics are not fully spelled out in the OCR text.
- Implementation Gaps: A reference kernel is needed to validate cloud-handling semantics independently.
- Validation Implications: Cloud offloading must be checked under deadline pressure and queueing behavior.
- Evidence:
  - [vertical_offloading] ADING AND DISTRIBUTEDML In the context of CEC, task offloading involves dynamically deciding whether to process tasks locally at the edge, offload them to another edge node (horizontal offloading) or to a cloud server (vertical offloading), under time-varying task arrival traffic. The primary goal of task offloading is to optimize system performance by minimizing target indicators, such as latency, energy consumption, and task drop ratio, to prevent bottlenecks and ensure smooth and efficient flow of CEC operations. As an optimization problem, task offloading is constrained by several factors, including limited computational resources at the Edge, ba
### M007 - Private Queue
- Category: `private_queue`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `keep`
- Expected Behavior: Each EA maintains a private queue for locally processed tasks with waiting and completion timing.
- Missing Details: Service discipline is only implicitly described by the OCR excerpts.
- Implementation Gaps: Need explicit lifecycle tracing if queue order needs formal auditing.
- Validation Implications: Private queue timing should be exercised by environment tests.
- Evidence:
  - [private_queue] A \$n\textbackslash\{\}in\textbackslash\{\}mathcal\{E\}\$ is equipped with N FiFO computation queues to execute tasks,and 1 offloading queue to stack the tasks to be offloaded.For EA n, the computation queue n is called private queue because it is used for computing the local tasks, whereas the rest of \$N-1\$ . computation queues are called public queues because they are used to host external tasks. The public queue \$n'\textbackslash\{\}in\textbackslash\{\}mathcal\{E\}-\textbackslash\{\}\{n\textbackslash\{\}\}\$ ofeach EA \$n\textbackslash\{\}in\textbackslash\{\}mathcal\{E\}\$ stacks the tasks offl oaded by EA \$n\textasciicircum{}\{\textback
### M008 - Public Queue
- Category: `public_queue`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `inspect_source`
- Expected Behavior: Offloaded tasks are inserted into FIFO public queues and processed under the destination node's public capacity.
- Missing Details: The scheduling rules among multiple public queues are not fully explicit in the OCR excerpts.
- Implementation Gaps: Need a reference kernel for queue-accounting checks if public queue rules are ambiguous.
- Validation Implications: Public queue behavior must be compared with trace accounting.
- Evidence:
  - [public_queue] b\}\}(t)\$</td><td>Size of task [bits] \$u\_\{n,k\}\textasciicircum{}\{p u b\}(t)\$</td></tr><tr><td>\$u\_\{n\}(t)\$</td><td>Task ID arrived in EA n</td><td>\$l\_\{n,k\}\textasciicircum{}\{p u b\}(t)\$</td><td>Length of public queue n of node k at time slot</td></tr><tr><td>\$\textbackslash\{\}eta\_\{n\}(t)\$</td><td>at time slot t Size of task \$u\_\{n\}(t)\$</td><td>\$\textbackslash\{\}mathcal\{A\}\_\{k\}(t)\$</td><td>t [bits] Set of active queues of</td></tr><tr><td>\$\textbackslash\{\}rho\_\{n\}(t)\$</td><td>[bits] Processing density of task</td><td>| \$A\_\{k\}(t)\$</td><td>node k at time slot t Number of active pub-</td></tr><tr><td>\$\te
### M009 - Task Arrival Process
- Category: `task_arrival_process`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `high`
- Next Action: `keep`
- Expected Behavior: Tasks arrive stochastically with a Bernoulli arrival probability per EA and slot.
- Missing Details: The exact randomization boundaries outside the OCR table are not fully recovered here.
- Implementation Gaps: Need to compare trace arrivals against the paper traffic assumptions.
- Validation Implications: Arrival process correctness influences all later sensitivity and fairness analysis.
- Evidence:
  - [task_arrival_process] ved from IoT layer. To reduce complexity, each HOODIE agent does not require knowledge on the decisions made by other agents. The optimization problem is formulated with known task timeouts and other task features under stochastic traffic at each agent. To solve this problem, HOODIE state input received both local task characteristics and forecasts about the upcoming load of the CEC nodes. The contributions of the present work can be summarized as follows: An analytical modelling and problem formulation is presented for the mathematical description of the hybrid task offloading in CEC. HOODIE particularly fits to scenarios where both edge and cloud
### M010 - Task Size Distribution
- Category: `task_size_distribution`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `recover_from_paper`
- Expected Behavior: Task sizes are drawn from a discrete set of values recovered from the OCR table.
- Missing Details: The OCR recovery of the size set is incomplete in places, so the discrete range should be treated as best-effort evidence.
- Implementation Gaps: Need to compare the recovered size set against committed traces if finer validation is required.
- Validation Implications: Task size variation drives delay and drop behavior.
- Evidence:
  - [task_size_distribution] $ 1,i.e. the task ID is set to zero if no task arrived. We also define the size of task \$u\_\{n\}(t)\{\textbackslash\{\}mathrm\{\textasciitilde{}a s\textasciitilde{}\}\}\textbackslash\{\}eta\_\{n\}(t)\$ 一(in bits). The values of task size are drawn from the discrete set \$\textbackslash\{\}mathcal\{H\}\{=\}\textbackslash\{\}\{\textbackslash\{\}eta\_\{1\},\textbackslash\{\}eta\_\{2\},\textbackslash\{\}ldots,\textbackslash\{\}eta\_\{|\textbackslash\{\}mathcal\{H\}|\}\textbackslash\{\}\}\$ . The size of task \$u\_\{n\}(t)\$ can be also written as \$\textbackslash\{\}eta\_\{n\}(t)=\textbackslash\{\}overset\{\textbackslash\{\}cdot\}\{x\_\{n\}\}(t)\textbackslash\{\}cdot\textbackslash\{\}
### M011 - Processing Density
- Category: `processing_density`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `keep`
- Expected Behavior: Task processing density expresses how many CPU cycles per bit are required.
- Missing Details: OCR provides a value, but some surrounding unit annotations are noisy.
- Implementation Gaps: Unit normalization must be checked against the paper text before assuming exact scale conversion.
- Validation Implications: Processing density affects both local computation and offloading delay calculations.
- Evidence:
  - [processing_density] (t)\$</td><td>at time slot t Size of task \$u\_\{n\}(t)\$</td><td>\$\textbackslash\{\}mathcal\{A\}\_\{k\}(t)\$</td><td>t [bits] Set of active queues of</td></tr><tr><td>\$\textbackslash\{\}rho\_\{n\}(t)\$</td><td>[bits] Processing density of task</td><td>| \$A\_\{k\}(t)\$</td><td>node k at time slot t Number of active pub-</td></tr><tr><td>\$\textbackslash\{\}phi\_\{n\}(t)\$</td><td>[CPU cycles/bit] \$u\_\{n\}(t)\$</td><td></td><td>lic queues of node k at time slot t</td></tr><tr><td></td><td>Timeout of task [time slot] \$u\_\{n\}(t)\$</td><td>\$f\_\{n\}\textasciicircum{}\{E A,p u b\}\$</td><td>Public processing capacity of EA n [cycles/sec]</td></tr
### M012 - CPU Capacity
- Category: `cpu_capacity`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `high`
- Next Action: `keep`
- Expected Behavior: Private, public, and cloud compute capacities determine whether tasks can be executed locally or offloaded.
- Missing Details: Evaluation sweeps over CPU capacity exist in the paper, but the registry only captures the documented values, not a new sweep.
- Implementation Gaps: Exact boundary handling across private, public, and cloud capacities remains a paper-to-code comparison point.
- Validation Implications: CPU capacity is central to delay and drop behavior under load.
- Evidence:
  - [cpu_capacity] ><td>\$w\_\{n\}\textasciicircum{}\{\{p r i v\}\}(t)\$</td><td>Waiting time of private task [time slots] \$u\_\{n\}(t)\$</td></tr><tr><td>M</td><td>Set of ECs</td><td>\$f\_\{n\}\textasciicircum{}\{E A,p r i v\}\$</td><td>Private Processing Capacity of EA n</td></tr><tr><td>T</td><td>Set of time slots</td><td></td><td>[cycles/sec] Set of link data rates</td></tr><tr><td>H</td><td>Set of task sizes</td><td>\$R\_\{H\}\$ \$\textbackslash\{\}mathcal\{R\}\$</td><td>Horizontal data rate</td></tr><tr><td>N</td><td>Number of EAs</td><td>\$R\_\{V\}\$</td><td>[bps] Vertical data rate [bps]</td></tr><tr><td>M</td><td>Number of ECs</td><td>\$R\_\{n,k\}\textasciicircum{}\{o f f\}
### M013 - Link Data Rates
- Category: `link_data_rates`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `high`
- Next Action: `requires_reference_kernel`
- Expected Behavior: Horizontal and vertical links use distinct data rates that influence offloading delay.
- Missing Details: Exact topology-specific rate mapping is not fully explicit in the OCR excerpts.
- Implementation Gaps: Need adjacency-backed validation to connect data rates to specific link pairs.
- Validation Implications: Link-rate assumptions can materially alter horizontal and vertical offload latency.
- Evidence:
  - [link_data_rates] city of EA n</td></tr><tr><td>T</td><td>Set of time slots</td><td></td><td>[cycles/sec] Set of link data rates</td></tr><tr><td>H</td><td>Set of task sizes</td><td>\$R\_\{H\}\$ \$\textbackslash\{\}mathcal\{R\}\$</td><td>Horizontal data rate</td></tr><tr><td>N</td><td>Number of EAs</td><td>\$R\_\{V\}\$</td><td>[bps] Vertical data rate [bps]</td></tr><tr><td>M</td><td>Number of ECs</td><td>\$R\_\{n,k\}\textasciicircum{}\{o f f\}\$</td><td>Data rate between EA n</td></tr><tr><td>T</td><td>Number of time slots</td><td>\$w\_\{n\}\textasciicircum{}\{\{o f f\}\}(t)\$</td><td>and node k [bps] Waiting time of</td></tr><tr><td></td><td></td><td></td><td>offloadi
### M014 - Transmission Delay
- Category: `transmission_delay`
- Paper Status: `partially_documented`
- Implementation Status: `assumption_backed`
- Assumption Risk: `medium`
- Next Action: `recover_from_paper`
- Expected Behavior: Transmission delay arises from moving tasks across horizontal or vertical links and should depend on task size and link rate.
- Missing Details: The exact closed-form transmission-delay equation is not recovered here., Link-specific formulas are only partially exposed in OCR.
- Implementation Gaps: Need explicit formula recovery before a strict paper-faithful check can be made.
- Validation Implications: Transmission delay is a major source of paper-to-code drift if units are misread.
- Evidence:
  - [transmission_delay] ADING AND DISTRIBUTEDML In the context of CEC, task offloading involves dynamically deciding whether to process tasks locally at the edge, offload them to another edge node (horizontal offloading) or to a cloud server (vertical offloading), under time-varying task arrival traffic. The primary goal of task offloading is to optimize system performance by minimizing target indicators, such as latency, energy consumption, and task drop ratio, to prevent bottlenecks and ensure smooth and efficient flow of CEC operations. As an optimization problem, task offloading is constrained by several factors, including limited computational resources at the Edge, ba
### M015 - Computation Delay
- Category: `computation_delay`
- Paper Status: `partially_documented`
- Implementation Status: `assumption_backed`
- Assumption Risk: `medium`
- Next Action: `recover_from_paper`
- Expected Behavior: Computation delay reflects processing time for local, public, and cloud execution paths.
- Missing Details: The precise delay decomposition is not fully restated in the OCR snippets., Unit normalization is incomplete in the OCR extraction.
- Implementation Gaps: Need formula-level tracing before asserting exact paper-faithful delay math.
- Validation Implications: Delay-sensitive behavior drives all comparison metrics and reward shaping.
- Evidence:
  - [computation_delay] ing stability, we incorporate techniques such as Long Short-term Memory (LSTM), Dueling deep Q-networks (DQN), and double-DQN. Extensive simulation results demonstrate that HOODIE effectively reduces task drop rates and average task processing delays, outperforming several baseline methods under changing CEC settings and dynamic conditions. INDEx TeRMS Cloud computing, cloud-edge continuum, cognitive network, deep reinforcement learning,edge computing, internet of things, task offloading. I. INTRODUCTION T HE Cloud-Edge Computing Continuum (CeC)repre-sents a distributed synergistic computing paradigm that integrates cloud computing resources with edge computi
### M016 - Timeout and Drop
- Category: `timeout_and_drop`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `blocking`
- Next Action: `requires_reference_kernel`
- Expected Behavior: Tasks that miss their deadlines are dropped, and timeout values constrain how long they may remain in the system.
- Missing Details: The OCR exposes timeout values, but the exact terminal accounting path should be verified against the runtime kernel.
- Implementation Gaps: Need careful validation against traces because timeout/drop strongly affects audit findings and fairness.
- Validation Implications: Any mismatch here changes reported drop ratio and the validity of baseline comparisons.
- Evidence:
  - [timeout_and_drop] host both local and external workloads arrived from IoT layer. To reduce complexity, each HOODIE agent does not require knowledge on the decisions made by other agents. The optimization problem is formulated with known task timeouts and other task features under stochastic traffic at each agent. To solve this problem, HOODIE state input received both local task characteristics and forecasts about the upcoming load of the CEC nodes. The contributions of the present work can be summarized as follows: An analytical modelling and problem formulation is presented for the mathematical description of the hybrid task offloading in CEC. HOODIE partic
### M017 - Reward Definition
- Category: `reward_definition`
- Paper Status: `documented`
- Implementation Status: `assumption_backed`
- Assumption Risk: `blocking`
- Next Action: `requires_reference_kernel`
- Expected Behavior: Reward combines delayed-task completion value and drop penalties, and is only emitted on terminal outcomes.
- Missing Details: The exact equation text is not reconstructed here, only the paper references and convention are preserved.
- Implementation Gaps: Reward formula validation should be tied back to the OCR equations before any repair work is attempted.
- Validation Implications: Reward integrity is a high-risk point because it shapes all training and evaluation behavior.
- Evidence:
  - [reward_definition] \{B\}\$</td><td>64 samples</td></tr></tbody></table></body></html> 1234567891011121314151617181920 FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. VOLUME , 17 ===== page\_018\_0\_res.txt ===== is the cumulative reward, as defined in (20) and (24), that was collected in a series of 5000 episodes, and averaged across all the distributed HOODIE agents. Note that, since the task delay is considered a negative metric, the ideal value is zero, which explains why the reward curves are negative and increasing. In Fig. 8b, the impact of the discount factor γ is also demonstrated, where different reward curves for varying values of \$\textbackslash\{\}gamma=[0.2,0.4,
### M018 - State Representation
- Category: `state_representation`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `medium`
- Next Action: `inspect_source`
- Expected Behavior: The state combines local task features with load-history and forecast information from the CEC environment.
- Missing Details: Exact vector ordering is not fully described in the OCR snippets.
- Implementation Gaps: Need a reference kernel to check that the state layout matches the paper semantics.
- Validation Implications: State drift can alter policy behavior and invalidate learned comparisons.
- Evidence:
  - [state_representation] d or adding new agents in CC. HOODIE agents exploit the Double and Dueling DRL techniques for learning stability [29]. To proactively adapt to time-varying workloads, the proposed algorithm considers as DRL inputs both local task features and forecasts about the upcoming load in the CEC. During the training, HOODIE considers only singlestep offloading decisions in order to enforce each agent provide fast decisions and avoid ping-pong effects.Also, the delay introduced in multi-hop offloading strategies is eliminated. Under this option, HOODIE simplifies the interfacing requirements (needed in multi-scale CEC) for multi-hop offloading and, thus,can be deployed in multi-agent CEC systems.
### M019 - Load Forecasting or LSTM Input
- Category: `load_forecasting_or_lstm_input`
- Paper Status: `documented`
- Implementation Status: `assumption_backed`
- Assumption Risk: `high`
- Next Action: `requires_reference_kernel`
- Expected Behavior: The DRL agents consume load-history information and LSTM-based forecasts to anticipate upcoming demand.
- Missing Details: Sequence length semantics and exact forecast encoding are not fully recoverable here.
- Implementation Gaps: No committed proof here that the forecast pipeline matches the paper's intended input shape.
- Validation Implications: Forecast input drift directly affects training stability and any LSTM claim.
- Evidence:
  - [load_forecasting_or_lstm_input] nts. The optimization problem is formulated with known task timeouts and other task features under stochastic traffic at each agent. To solve this problem, HOODIE state input received both local task characteristics and forecasts about the upcoming load of the CEC nodes. The contributions of the present work can be summarized as follows: An analytical modelling and problem formulation is presented for the mathematical description of the hybrid task offloading in CEC. HOODIE particularly fits to scenarios where both edge and cloud resources need to be efficiently managed to support latency-sensitive and resource-intensive applications of the end-devices. HOODIE
### M020 - DQN Double Dueling LSTM Training
- Category: `dqn_double_dueling_lstm_training`
- Paper Status: `documented`
- Implementation Status: `unknown`
- Assumption Risk: `high`
- Next Action: `requires_reference_kernel`
- Expected Behavior: The training stack uses DQN-style learning with double and dueling techniques, plus LSTM for enhanced stability and forecasting.
- Missing Details: Exact network topology and training hyperparameters are only partially visible in OCR., Committed artifacts do not prove the learned HOODIE stack itself.
- Implementation Gaps: Training mechanics remain a future reference-kernel or repair topic, not something this registry can prove.
- Validation Implications: Training claims must not be overinterpreted as validated implementation behavior.
- Evidence:
  - [dqn_double_dueling_lstm_training] in the distributed decision-making, with each agent not knowing the decisions of the other agents. In this context,HOODIES facilitates the process for removing old or adding new agents in CC. HOODIE agents exploit the Double and Dueling DRL techniques for learning stability [29]. To proactively adapt to time-varying workloads, the proposed algorithm considers as DRL inputs both local task features and forecasts about the upcoming load in the CEC. During the training, HOODIE considers only singlestep offloading decisions in order to enforce each agent provide fast decisions and avoid ping-pong effects.Also, the delay introduced in multi-hop offloading strategies
### M021 - Training Episode Protocol
- Category: `training_episode_protocol`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `medium`
- Next Action: `keep`
- Expected Behavior: Training runs over 5000 episodes with a fixed episode horizon and queue-emptying tail slots.
- Missing Details: Exploration schedule and seed handling are not fully recovered from OCR here.
- Implementation Gaps: Need validation against training logs if episode protocol fidelity becomes relevant.
- Validation Implications: Episode protocol affects reward curves and any Fig. 8 / Fig. 11 reproduction claim.
- Evidence:
  - [training_episode_protocol] 21314151617181920 FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. VOLUME , 17 ===== page\_018\_0\_res.txt ===== is the cumulative reward, as defined in (20) and (24), that was collected in a series of 5000 episodes, and averaged across all the distributed HOODIE agents. Note that, since the task delay is considered a negative metric, the ideal value is zero, which explains why the reward curves are negative and increasing. In Fig. 8b, the impact of the discount factor γ is also demonstrated, where different reward curves for varying values of \$\textbackslash\{\}gamma=[0.2,0.4,0.6,0.8,0.99]\$ are shown. Stabilizing the value
### M022 - Validation Episode Protocol
- Category: `validation_episode_protocol`
- Paper Status: `documented`
- Implementation Status: `partially_implemented`
- Assumption Risk: `medium`
- Next Action: `keep`
- Expected Behavior: Validation uses trained Q-models over 200 episodes with exploitative actions.
- Missing Details: Exact trace reuse and pairing details are not fully spelled out in the OCR snippets.
- Implementation Gaps: Validation protocol should be checked against audit and sensitivity outputs if needed.
- Validation Implications: Validation semantics determine reported performance comparisons.
- Evidence:
  - [validation_episode_protocol] er density \$(N=[10,15,20])\$ ). To assess the HOoDIE performance, we used the optimally trained Q models of each agent (as they resulted from Section A) and we calculated the average reward collected during a series of 200 validation episodes (i.e. all agents performed exploitative actions). Evidently, as the task arrival probability increases, the average reward decreases across all configurations, indicating the system's increased strain under higher task loads.This is attributed to the complexity introduced when the system load is significantly increased, imposing further suboptimality in the task placement decision. The task arrivals density directl
### M023 - Baseline Policy Definitions
- Category: `baseline_policy_definitions`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `low`
- Next Action: `keep`
- Expected Behavior: The paper compares HOODIE against named baselines such as RO, FLC, VO, HO, BCO, and MLEO.
- Missing Details: Exact tie-breaking and all paper-side heuristics for the baselines are not fully enumerated in the OCR excerpts.
- Implementation Gaps: Policy-by-policy fidelity should be checked in later fairness and differential features.
- Validation Implications: Baselines are central to all comparison claims and fairness checks.
- Evidence:
  - [baseline_policy_definitions] IOS INNOOULOS1 (emb,E), IAS RALIAS2, SOTIRIOS SPANTIDEAS1,ANDPANAGIOTIS TRAKADAS1 1DarrtndilniitofciC.2RcotoIiC CORRESPONDING AUTHOR:ANASTASIOS GIANNOPOULOS (e-mail: angianno@Ua.gr. Union'sHORIONresearchandinnovationprogrammeundergrantagreementNo101070177. ABSTRACT Cloud-Edge Computing Continuum (CEC) system, where edge and cloud nodes are seamlessly connected, is dedicated to handle substantial computational loads offloaded by end-users. These tasks can suffer from delays or be dropped entirely when deadlines are missed, particularly under fluctuating network conditions and resource limitations. The CEC is coupled with the need f
### M024 - Evaluation Metrics
- Category: `evaluation_metrics`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `medium`
- Next Action: `inspect_source`
- Expected Behavior: Evaluation reports average delay, drop ratio, throughput, and related reward behavior with paper-specific sign conventions.
- Missing Details: The paper's negative-delay convention must remain a caveat because repository outputs may preserve positive stored values.
- Implementation Gaps: Exact aggregation formulas should be checked against the paper equations if metric repair is ever attempted.
- Validation Implications: Any metric drift would invalidate comparison and audit outputs.
- Evidence:
  - [evaluation_metrics] nsity-complexity tradeoff, which balances computational resources and task load effectively, thereby maintaining higher performance levels under varying conditions. Note that the high negative rewards do not reflect the average delay of the tasks, but they indicate the high negative penalties received for task drops, which is more frequent as the P increases. Under the same simulations, Fig. 9b depicts the distribution of actions taken by the HOoDIE agents across different task arrival probabilities, categorized into local computation,horizontal, and vertical offloading. The results show a clear preference for horizontal offloading, especially
### M025 - Figure Result Requirements
- Category: `figure_result_requirements`
- Paper Status: `documented`
- Implementation Status: `implemented`
- Assumption Risk: `low`
- Next Action: `keep`
- Expected Behavior: The paper requires specific evaluation outputs across figures 7 through 11 and associated narrative claims.
- Missing Details: Figure numbers alone do not prove reproducibility of the underlying mechanisms.
- Implementation Gaps: Figure requirements are only comparison scaffolding until mechanism fidelity is proven elsewhere.
- Validation Implications: The registry must not confuse figure support with full paper validation.
- Evidence:
  - [figure_result_requirements] <td>10000 samples</td></tr><tr><td>Task Drop Penalty</td><td>\$C\$</td><td>40</td></tr><tr><td>Batch size</td><td>\$N\_\{B\}\$</td><td>64 samples</td></tr></tbody></table></body></html> 1234567891011121314151617181920 FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. VOLUME , 17 ===== page\_018\_0\_res.txt ===== is the cumulative reward, as defined in (20) and (24), that was collected in a series of 5000 episodes, and averaged across all the distributed HOODIE agents. Note that, since the task delay is considered a negative metric, the ideal value is zero, which explains why the reward curves are negative and increasing.

## Implementation Gap Summary
- documented: 22
- partially_documented: 3
- ambiguous: 0
- missing: 0
- implemented: 13
- partially_implemented: 7
- assumption_backed: 4
- unknown: 1
- not_implemented: 0
- mapped_in_project: 25
- mapped_but_unvalidated: 25
- paper_validated: 0
- total_entries: 25

Recommended next feature: `reference_task_lifecycle_kernel`

No runtime changes statement: this registry is read-only and does not validate paper reproduction.
