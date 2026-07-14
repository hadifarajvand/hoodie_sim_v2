III. Proposed Effective Completion via Hybrid Offloading Framework (ECHO)


A. Framework Overview and Design Scope




Cloud-edge continuum environments provide a distributed computing substrate for delay-sensitive computational tasks, where computation can be performed across local edge nodes, neighboring edge servers, and remote cloud resources. In this setting, hybrid computation offloading is required because relying only on local execution may overload edge nodes, while relying only on vertical cloud offloading may introduce excessive transmission and processing delay. Therefore, each arriving task must be assigned to an appropriate execution path, such as local computation, horizontal edge offloading, or vertical cloud offloading, according to the current task characteristics, queue status, communication condition, and available processing capacity. However, the offloading decision becomes more challenging when tasks are associated with strict completion bounds. A task that experiences excessive waiting time in a local or outbound-transfer queue, or is forwarded to a congested destination, may miss its allowed completion time and consequently be removed from successful execution. This makes the task drop ratio a critical performance indicator, particularly under dynamic traffic, limited edge resources, and fluctuating cloud-edge network conditions. Accordingly, this paper proposes Effective Completion via Hybrid Offloading (ECHO), a deadline-aware hybrid computation offloading method where the objective is not only to select a computationally feasible execution path, but also to guide the decision process toward timely task completion and reduced risk of task dropping. In ECHO, effective completion denotes the use of estimated end-to-end completion feasibility to guide source-queue scheduling and hybrid offloading decisions before the task outcome is observed.




Although hybrid offloading frameworks can reduce delay by distributing workloads across local, edge, and cloud resources, deadline handling must be integrated before task completion is evaluated. Existing distributed hybrid offloading agents can observe local task characteristics and forecasted load information to learn decisions that reduce execution latency and timeout-related task loss [37]. That learning foundation does not itself specify how each task's remaining completion slack should control queue order and route feasibility before action selection. If deadline information is only reflected after a task has waited, been transmitted, or failed to finish within its completion bound, the learning agent may still choose actions that are reasonable from an average-delay perspective but risky for tasks with tighter time constraints. The design rationale of the proposed framework is therefore to move deadline awareness earlier in the decision pipeline. Specifically, task urgency is introduced into queue scheduling, candidate evaluation, and reward feedback so that deadline-related risk is visible before the final execution outcome is observed.




The core idea of the proposed framework is to use Effective Remaining Time (ERT) as a unified temporal indicator for deadline-aware task handling. A raw deadline or timeout value alone is not sufficient for offloading decisions, because two tasks with similar deadlines may have different violation risks depending on their queue position, expected waiting time, transmission requirement, destination load, and processing demand. Therefore, the proposed framework interprets deadline urgency through the remaining feasible time after the expected execution conditions are considered. In this view, ERT acts as a bridge between task-level timing constraints and offloading-level decision making.


At the queue level, ERT indicates which pending task should be served earlier to avoid unnecessary deadline miss. At the candidate-selection level, it indicates whether a local, horizontal edge, or vertical cloud execution option is likely to complete the task within its allowable completion bound. This temporal signal does not replace the distributed DRL decision module; rather, it provides deadline-aware information that can be incorporated into queue ordering, feasible-action filtering, state representation, and reward feedback. As a result, the learning agent is guided not only by average delay and load-related observations, but also by the remaining time available for successful task completion.








The proposed framework consists of interdependent modeling and decision-making components that translate deadline awareness into the hybrid offloading process. The task and deadline model provides the timing basis of the framework by describing each arriving task through its arrival time, data size, processing demand, and allowable completion bound. Based on this timing information, the ERT estimation component evaluates how much effective time remains after the expected queueing, transmission, and processing conditions are considered. This temporal urgency is then used by the deadline-aware queue scheduling component to reorder pending tasks in the local and outbound-transfer queues when their risk of deadline violation differs. In parallel, the candidate-selection component evaluates local execution, horizontal edge offloading, and vertical cloud offloading according to their estimated completion behaviour and deadline feasibility. The distributed DRL decision module uses these observations together with local task information, queue status, and load-related indicators to select the final execution action at each edge agent. The reward feedback component closes the decision loop by penalizing realized duration, selection under predicted deadline infeasibility, and actual task dropping, thereby aligning learning with the objective of reducing deadline-related task loss under dynamic cloud-edge conditions.




The remainder of this section formalizes the proposed framework in a stepwise manner. First, the cloud-edge system model is defined to specify the computing nodes, communication layers, time-slotted operation, and hybrid execution paths. Then, the task model and deadline representation are introduced to describe task arrivals, task characteristics, and completion bounds. After that, the Effective Remaining Time model is formulated as the central deadline-aware timing indicator. The following subsections then explain how ERT is used for queue scheduling and candidate execution evaluation before the final offloading action is selected by the distributed DRL agent. Finally, the state space, action space, reward model, and algorithmic workflow are presented to show how the proposed deadline-aware mechanism is integrated into multi-agent distributed deep reinforcement learning. This organization separates conceptual framework design from simulation and performance evaluation, which are addressed in Section IV rather than in the proposed-method section.






  

Figure 1. Overall ECHO architecture in the IoT–edge–cloud continuum, supporting local execution, horizontal edge offloading, and vertical cloud offloading.


B. Cloud–Edge System Model


This section defines the cloud-edge system model used as the basis of the proposed deadline-aware hybrid offloading framework. The model specifies the computing entities, communication structure, task and deadline representation, offloading decision variables, and queueing components required before introducing Effective Remaining Time and the deadline-aware control logic. The main mathematical symbols introduced in this section are summarized after the architectural definitions to keep the subsequent formulations consistent and readable.


ECHO considers a distributed cloud-edge architecture with local, horizontal-edge, and vertical-cloud execution paths [37]. Its distinctive control variables are estimated end-to-end completion time, ERT, queue urgency, route feasibility, and task-level delayed outcomes. Each computational task is non-divisible and is assigned to one execution path.


At the moment a task arrives, its descriptor is assumed to be available to the source EA. This descriptor includes the input size, the processing density, and the relative timeout of the task. The model does not assume knowledge of future task arrivals. Instead, each EA makes its decision from its current local observation, the status of its own queues, and compact load information obtained from the monitoring layer. The system is represented in synchronized time slots with a fixed slot length $\Delta$, so waiting, transmission, and processing durations are expressed as integer numbers of slots. This slot-based representation makes deadline satisfaction directly comparable with estimated completion time.


Horizontal offloading is allowed only between connected edge agents, while vertical offloading to the cloud remains available as a high-capacity but potentially higher-latency execution path. The queue waiting times and candidate completion times used in the proposed method are estimates computed at the decision time. These estimates may change as the workload evolves, but they provide the temporal basis required for ERT calculation, deadline-aware queue scheduling, and candidate feasibility checking.


Under these assumptions, the physical paths and queue locations remain fixed during operation. ECHO changes the decision and service logic by evaluating deadline, end-to-end completion time, and ERT before execution, so urgency affects both queue service and route selection before a task becomes late or is dropped.










1) System Architecture
As shown in Fig. 1, ECHO operates over a three-layer IoT-edge-cloud continuum consisting of an IoT layer, an edge layer, and a cloud layer [37]. The IoT layer represents multiple task-generating service areas, while the edge layer contains $N$ Edge Agents (EAs) that provide near-user computational capacity. A remote cloud node is also available as a high-capacity computing resource for tasks that cannot be efficiently processed at the edge. Let $\mathcal{N}=\{1,2,\ldots,N,N+1\}$ denote the set of all computing nodes, where $N+1$ represents the cloud node. The set of edge agents is denoted by $\mathcal{E}=\mathcal{N}\setminus\{N+1\}=\{1,2,\ldots,N\}$. Each EA $n\in\mathcal{E}$ is associated with a corresponding IoT service area and is able to participate in both local task execution and cooperative offloading.






To support distributed monitoring and information exchange, the edge layer is assumed to include a set of Edge Controllers (ECs), denoted by $\mathcal{M}=\{1,2,\ldots,M\}$. An EC may monitor a single EA or a cluster of EAs, depending on the deployment structure. The ECs collect compact status information such as queue load and node-level activity, and this information can be shared with the corresponding EAs for load-aware decision making. This monitoring role does not imply centralized control of the offloading policy; instead, each EA remains responsible for its own local decision process while using locally observed and shared system information.


The system is observed over a finite episode composed of time slots $\mathcal{T}=\{1,2,\ldots,T\}$, where each time slot has duration $\Delta$ seconds. At the beginning of a time slot, an EA may receive a new computational task from its associated IoT area and observe the current queue and load conditions available to it. Communication from IoT devices to their area-specific base station is performed through wireless links, while the connection from the base station to the corresponding EA is assumed to rely on a wired fronthaul link. Horizontal offloading is enabled through edge-to-edge communication among EAs, and vertical offloading is enabled through the connection between EAs and the cloud node. This architecture provides the computational substrate for local execution, horizontal edge offloading, and vertical cloud offloading, which are formally represented in the hybrid offloading decision model.
Table 2 summarizes the mathematical notation used throughout ECHO.


Table 2. Mathematical notation of the ECHO framework.








Notation
	Definition
	$N$
	Number of Edge Agents (EAs).
	$M$
	Number of Edge Controllers (ECs).
	$T$
	Number of time slots in one episode.
	$n$
	Index of an Edge Agent or source node.
	$k$
	Index of an execution destination.
	$i$
	Index of a computational task.
	$h$
	Index of another task, typically a predecessor in a queue.
	$j$
	Index of a position in the fixed canonical action set.
	$t$
	Current time-slot index.
	$\mathcal{N}$
	Set of all computing nodes, including the cloud node.
	$\mathcal{E}$
	Set of Edge Agents.
	$\mathcal{M}$
	Set of Edge Controllers.
	$\mathcal{T}$
	Set of time slots in an episode.
	$\mathcal{H}$
	Set of admissible task input sizes.
	$\Delta$
	Duration of one time slot in seconds.
	$\mathbf{G}$
	Edge-layer connectivity matrix.
	$G(n,k)$
	Connectivity indicator between EAs $n$ and $k$.
	$\chi_n(t)$
	Binary indicator that a new task arrives at EA $n$ in slot $t$.
	$\xi_i$
	Computational task indexed by $i$.
	$s_i$
	Source EA of task $\xi_i$.
	$t_i^a$
	Arrival and offloading-decision slot of task $\xi_i$.
	$t_i^r$
	Resolution slot at which task $\xi_i$ completes or is recorded as dropped.
	$\tau_{n,m}$
	Slot of the $m$th actual route decision of EA $n$; the final epoch is terminal.
	$b_i$
	Input data size of task $\xi_i$ in bits.
	$b_i^{\mathrm{rem}}(t)$
	Remaining unprocessed bits of task $\xi_i$ at slot $t$.
	$\nu_i$
	Processing density of task $\xi_i$ in CPU cycles per bit.
	$\delta_i$
	Relative timeout of task $\xi_i$ in slots.
	$d_i$
	Absolute completion deadline of task $\xi_i$.
	$\alpha$
	Generic execution or offloading action.
	$\alpha_n^L$
	Local-execution action at EA $n$.
	$\alpha_{n,k}^H$
	Horizontal-offloading action from EA $n$ to connected EA $k$.
	$\alpha_n^V$
	Vertical-offloading action from EA $n$ to the cloud.
	$\alpha_i$
	Action selected for task $\xi_i$.
	$\mathcal{A}_n(t)$
	Physically available action set of EA $n$ at slot $t$.
	$\bar{\mathcal{A}}_n$
	Fixed canonical action-output set of EA $n$.
	$\bar{\alpha}_{n,j}$
	Action stored at canonical output position $j$ of EA $n$.
	$\kappa(\alpha)$
	Mapping from action $\alpha$ to its execution destination.
	$k_i$
	Destination stored with offloaded task $\xi_i$.
	$\mathbf{g}_i$
	Stored dispatch metadata of task $\xi_i$.
	$\mathcal{Q}_i^{\mathrm{src}}(t)$
	Source-side queue selected for task $\xi_i$ at slot $t$.
	$\mathcal{Q}_n^L(t)$
	Local waiting queue of EA $n$.
	$\mathcal{Q}_n^X(t)$
	Outbound-transfer waiting queue of EA $n$.
	$\mathcal{Q}_{n\rightarrow k}^D(t)$
	Destination queue at node $k$ for tasks received from source EA $n$.
	$z_{i,k}^D(t)$
	Indicator that transmission of task $\xi_i$ to destination $k$ finished before slot $t$.
	$U_k^D(t)$
	Number of tasks admitted to destination queues of node $k$ at slot $t$.
	$q_n^L(t)$
	Occupancy of the local waiting queue at EA $n$.
	$q_n^X(t)$
	Occupancy of the outbound-transfer waiting queue at EA $n$.
	$\varrho_n^L(t)$
	Residual service time of the active local task at EA $n$.
	$\varrho_n^X(t)$
	Residual transmission time of the active outbound task at EA $n$.
	$\Psi_n^L(t)$
	Remaining local-side workload at EA $n$.
	$\Psi_n^X(t)$
	Remaining outbound-transfer workload at EA $n$.
	$f_n^L$
	Local processing capacity of EA $n$.
	$f_k^{EA}$
	Processing capacity of edge destination $k$.
	$f^C$
	Processing capacity of the cloud.
	$f_k^D$
	Unified destination-processing capacity of node $k$.
	$\bar f_{n,k}^D(t)$
	Estimated effective destination capacity assigned to source queue $n\rightarrow k$.
	$R_H$
	Horizontal edge-to-edge transmission rate.
	$R_V$
	Vertical edge-to-cloud transmission rate.
	$R_{n,k}$
	Transmission rate from source node $n$ to destination $k$.
	$\tau_i^L$
	Local processing duration of task $\xi_i$.
	$\tau_{i,k}^X$
	Transmission duration of task $\xi_i$ to destination $k$.
	$\tau_{i,k}^D(t)$
	Estimated destination-processing duration of task $\xi_i$ at node $k$.
	$\mathcal{H}_i^L(t)$
	Provisional predecessor set of task $\xi_i$ in the local queue.
	$\mathcal{H}_i^X(t)$
	Provisional predecessor set of task $\xi_i$ in the outbound-transfer queue.
	$\widehat W_i^L(t)$
	Estimated local-queue waiting time of task $\xi_i$.
	$\widehat W_i^X(t)$
	Estimated outbound-transfer waiting time of task $\xi_i$.
	$\widehat T_i^L(t)$
	Estimated local completion slot of task $\xi_i$.
	$\widehat T_{i,k}^X(t)$
	Estimated completion slot of the source-side transmission stage to node $k$.
	$\widehat t_{i,k}^D(t)$
	Estimated slot at which task $\xi_i$ reaches destination queue $k$.
	$\Omega_{n\rightarrow k}(t)$
	Actual remaining cycle workload in destination queue $n\rightarrow k$.
	$\widehat\Omega_{n\rightarrow k}(t)$
	Observed or predicted remaining cycle workload used for estimation.
	$\mathcal{J}_k(t)$
	Set of active source-indexed destination queues at node $k$.
	$p_k(t)$
	Number of active source-indexed destination queues at node $k$.
	$\bar p_{n,k}(t)$
	Adjusted active-queue count after hypothetically admitting source queue $n\rightarrow k$.
	$\widehat W_{i,k}^D(t)$
	Estimated destination-queue waiting time of task $\xi_i$ at node $k$.
	$\widehat T_{i,k}^O(t)$
	Estimated end-to-end completion slot for offloading task $\xi_i$ to node $k$.
	$\widehat T_i(\alpha,t)$
	Unified estimated completion slot of task $\xi_i$ under action $\alpha$.
	$\mathbf{o}_n(t)$
	Observed destination-load vector available to EA $n$.
	$\mathbf{H}_n(t)$
	Historical load matrix maintained by EA $n$.
	$W$
	Length of the load-history lookback window.
	$F_\psi$
	LSTM-based load encoder with parameters $\psi$.
	$\psi$
	Parameter set of the recurrent load encoder.
	$\mathbf{z}_n(t)$
	Fixed-dimensional recurrent load embedding of EA $n$.
	$\widehat{\mathbf{H}}_n(t+1)$
	Predicted next-slot load representation.
	$\mathsf{ERT}_i^L(t)$
	Queue-level Effective Remaining Time of task $\xi_i$ for local execution.
	$\mathsf{ERT}_i^X(t)$
	End-to-end queue-level Effective Remaining Time of task $\xi_i$ in the transfer queue.
	$\mathsf{ERT}_i^C(\alpha,t)$
	Candidate-level Effective Remaining Time under action $\alpha$.
	$\mathcal{F}_n^L(t)$
	Predicted-feasible task set in the local queue of EA $n$.
	$\mathcal{F}_n^X(t)$
	Predicted-feasible task set in the outbound-transfer queue of EA $n$.
	$\xi_n^{L,*}(t)$
	Task selected next for local processing at EA $n$.
	$\xi_n^{X,*}(t)$
	Task selected next for outbound transmission at EA $n$.
	$\ell_i^L(t)$
	Estimated local queue-level lateness of task $\xi_i$.
	$\ell_i^X(t)$
	Estimated end-to-end transfer queue-level lateness of task $\xi_i$.
	$\mathcal{V}_i(t)$
	Set of physically available actions predicted to meet the deadline of task $\xi_i$.
	$\Lambda_i(\alpha,t)$
	Predicted lateness of candidate action $\alpha$ for task $\xi_i$.
	$\alpha_i^{fb}(t)$
	Minimum-lateness fallback action for task $\xi_i$.
	$\mathcal{U}_i(t)$
	Effective action set used by the learning policy.
	$\mu_{n,j}(t)$
	Binary availability indicator for canonical action position $j$.
	$\boldsymbol{\mu}_n(t)$
	Fixed-dimensional physical-and-deadline action mask of EA $n$.
	$\mathbf{s}_n(t)$
	Normalized DRL state observed by EA $n$.
	$\tilde{x}$
	Normalized form of numerical quantity $x$.
	$\mathsf{ERT}_{n,\min}^L(t)$
	Minimum local-queue ERT summary at EA $n$.
	$\mathsf{ERT}_{n,\min}^X(t)$
	Minimum outbound-transfer-queue ERT summary at EA $n$.
	$\mathbf{e}_i^C(t)$
	Fixed-dimensional vector of candidate-level ERT values.
	$T_i^{\mathrm{sys}}$
	Realized system duration of task $\xi_i$.
	$I_i^R$
	Decision-time indicator that every physical candidate is predicted infeasible.
	$I_i^D$
	Realized indicator that task $\xi_i$ fails to achieve deadline-satisfied completion.
	$\lambda_R$
	Penalty weight for predicted infeasibility and normalized selected-action lateness.
	$\lambda_D$
	Penalty weight for realized task dropping.
	$r_i$
	Task-level reward associated with task $\xi_i$.
	$\mathcal{P}_n$
	Pending-decision buffer of EA $n$.
	$\mathbf{p}_i$
	Pending record maintained for task $\xi_i$.
	$\mathcal{R}_n$
	Replay memory of EA $n$.
	$\zeta_{n,m}$
	Agent-specific event-epoch semi-Markov replay transition.
	$\Delta_{n,m}$
	Sojourn time between consecutive route decisions of EA $n$.
	$\mathbf{x}_{n,m}$
	Complete simulator state sampled immediately before EA $n$ acts at $\tau_{n,m}$.
	$\alpha_{n,m}$
	Route action selected by EA $n$ at its decision epoch $\tau_{n,m}$.
	$\rho_{n,m}$
	Discounted source-$n$ task reward accumulated between consecutive decisions of EA $n$.
	$\pi_n$
	Decision policy of EA $n$.
	$\pi_n^*$
	Optimal policy sought for EA $n$.
	$\gamma$
	Discount factor.
	$Q_n(\mathbf{s},\alpha;\theta_n)$
	Online action-value function of EA $n$.
	$Q_n^-(\mathbf{s},\alpha;\theta_n^-)$
	Target action-value function of EA $n$.
	$\theta_n$
	Parameter vector of the online Q-network at EA $n$.
	$\theta_n^-$
	Parameter vector of the target Q-network at EA $n$.
	$V_n(\mathbf{s};\theta_n)$
	Dueling-network state-value function.
	$A_n(\mathbf{s},\alpha;\theta_n)$
	Dueling-network action-advantage function.
	$Q_n^\mu(\mathbf{s},\alpha;t)$
	Action-value function after applying the current mask.
	$\epsilon$
	Exploration probability in the masked epsilon-greedy policy.
	$\alpha_{n,m+1}^+$
	Masked next action selected for the event-epoch Double-DQL target.
	$y_{n,m}$
	Double-DQL target for event-epoch transition $(n,m)$.
	$\widehat y_{n,m}$
	Online Q-network prediction for event-epoch transition $(n,m)$.
	$\mathcal{L}_n(\theta_n)$
	Mini-batch learning loss of EA $n$.
	$B$
	Mini-batch of replayed event-epoch transitions.
	$|B|$
	Number of transitions in mini-batch $B$.
	$N_{\mathrm{copy}}$
	Target-network copy period.
	$\alpha_{lr}$
	Learning rate.
	$\mathbb{I}[\cdot]$
	Indicator function, equal to one when its condition is true and zero otherwise.
	$\mathbb{E}_{\pi_n}[\cdot]$
	Expectation under policy $\pi_n$.
	$\lceil x\rceil$
	Smallest integer greater than or equal to $x$.
	$|\mathcal{S}|$
	Cardinality of set $\mathcal{S}$.
	$\emptyset$
	Empty set.
	$-\infty$
	Value assigned to masked actions so they cannot be selected.
	

2) Task Characteristics and Deadline Representation
At the beginning of each time slot $t\in\mathcal{T}$, each EA $n\in\mathcal{E}$ may receive a new computational task from its associated IoT area. The task-arrival process is represented by the binary variable $\chi_n(t)$ as follows:


\begin{equation}
\chi_n(t)=
\begin{cases}
1, & \text{if a new task arrives in EA } n \text{ at time slot } t,\\
0, & \text{otherwise.}
\end{cases}
\tag{1}
\end{equation}


When $\chi_n(t)=1$, the arrived task is denoted by $\xi_i$. The task is characterized by its input data size $b_i$, processing density $\nu_i$, and timeout index $\delta_i$. The task size $b_i$ is measured in bits and is drawn from the task-size set $\mathcal{H}$, while $\nu_i$ represents the number of CPU cycles required to process one bit of the task. The timeout index $\delta_i$ indicates the maximum number of time slots within which the task should be completed after its arrival.


ECHO converts the relative timeout into an absolute completion deadline so that the same timing boundary can be used in completion estimation, queue scheduling, and route selection. Since task $\xi_i$ arrives at the beginning of time slot $t$, its absolute deadline is defined as


\begin{equation}
d_i=t+\delta_i-1.
\tag{2}
\end{equation}


Accordingly, under the absolute deadline in (2), task $\xi_i$ is deadline-satisfied only if its realized completion slot does not exceed $d_i$. This explicit deadline representation is later used to define Effective Remaining Time, deadline-aware queue ordering, and deadline-feasible offloading candidate selection.


The derivation of the absolute deadline follows from the slot-based interpretation of the timeout. If a task arrives at the beginning of slot $t$ and its timeout is $\delta_i$ slots, then the task can use the slots $t,t+1,\ldots,t+\delta_i-1$. Hence, the last acceptable completion slot is $t+\delta_i-1$. This definition avoids an off-by-one ambiguity and makes the deadline condition directly comparable with completion-time estimates expressed in time-slot indexes.


The within-slot chronology is fixed as follows. At the boundary opening slot $t$, service completions produced at the end of slot $t-1$ are applied, and a completed transmission enters its stored destination queue as specified in (7). Expired waiting tasks are then removed and the current load observation is formed. New arrivals are observed, their route actions are selected from the pre-action state, and they are admitted to their selected source queues. Affected ERT orders are rebuilt and idle resources are scheduled, allowing a newly arrived task to start in slot $t$ when its resource is idle. Finally, every active operation receives exactly one slot of service. A one-slot operation started at $t$ completes at the end of slot $t$ and its boundary event is applied when slot $t+1$ opens, without adding an extra service slot. The same chronology is used for ECHO, HOODIE, and every baseline.


The task lifecycle is applied consistently to all queues. At the beginning of a service decision, a waiting task with current slot greater than its absolute deadline is removed and recorded as dropped. A task that has already started computation or transmission is not preempted; the active operation retains the resource until it finishes, but its result is recorded as dropped if the realized completion slot exceeds the deadline. This rule preserves non-preemptive resource occupancy while ensuring that only deadline-satisfied outcomes are counted as successful.








3) Hybrid Offloading Decision Model
When a new task $\xi_i$ arrives at EA $n$, ECHO selects one direct action from the local, horizontal-edge, and vertical-cloud candidates. The selected action determines both the source queue and, when offloading is chosen, the destination stored with the task. The dispatch block shown in Fig. 2 later applies that stored destination; it does not perform a second destination optimization.


The physical candidate action set is


\begin{equation}
\mathcal{A}_n(t)=\{\alpha_n^L\}\cup\{\alpha_{n,k}^H\mid k\in\mathcal{E}\setminus\{n\},\,G(n,k)=1\}\cup\{\alpha_n^V\}.
\tag{3}
\end{equation}


The execution destination associated with action $\alpha$ is


\begin{equation}
\kappa(\alpha)=\begin{cases}n, & \alpha=\alpha_n^L,\\k, & \alpha=\alpha_{n,k}^H,\\N+1, & \alpha=\alpha_n^V.\end{cases}
\tag{4}
\end{equation}


The selected source-side queue is therefore


\begin{equation}
\mathcal{Q}_i^{src}(t)=\begin{cases}\mathcal{Q}_{s_i}^L(t), & \kappa(\alpha_i)=s_i,\\\mathcal{Q}_{s_i}^X(t), & \kappa(\alpha_i)\neq s_i.\end{cases}
\tag{5}
\end{equation}


For an offloaded task, the stored destination metadata is


\begin{equation}
k_i=\kappa(\alpha_i),\qquad k_i\in\mathcal{N}\setminus\{s_i\}.
\tag{6}
\end{equation}


Selection of an offloading action does not create an immediate arrival at the destination queue. A task enters $\mathcal{Q}_{n\rightarrow k}^D(t)$ only after its source-side transmission finishes. Let


\begin{equation}
z_{i,k}^D(t)=\begin{cases}1, & \text{if transmission of task }\xi_i\text{ to node }k\text{ finishes at }t-1,\\0, & \text{otherwise}.\end{cases}
\tag{7}
\end{equation}


The number of tasks that actually enter destination queues of node $k$ at slot $t$ is


\begin{equation}
U_k^D(t)=\sum_{i:s_i\neq k}z_{i,k}^D(t).
\tag{8}
\end{equation}


For an edge destination, the source index excludes the destination itself; for the cloud, all EAs are included. Each received task is placed in the destination queue indexed by its source EA. This timing relation distinguishes the decision slot from the later transmission-completion slot.


The direct action is selected once at task arrival. ECHO does not add a new physical route; it changes how the existing local, horizontal, and vertical routes are evaluated through end-to-end completion estimation, ERT, and deadline-aware masking.


4) Local Queue Model
Each EA maintains a local waiting queue and a local processor, following the distributed queue architecture in [37]. ECHO applies non-preemptive ERT-based service selection whenever the local processor becomes idle. Every queue record stores the task identifier, source, arrival slot, size, processing density, deadline, remaining workload, and the information required to recompute completion estimates.


Let $\mathcal{Q}_n^L(t)$ contain the waiting local tasks, excluding any task currently in service. The local processing duration of task $\xi_i$ is


\begin{equation}
\tau_i^L=\left\lceil\frac{b_i\nu_i}{f_n^L\Delta}\right\rceil.
\tag{9}
\end{equation}


Let $\varrho_n^L(t)$ denote the residual service time of the task currently running on the local processor, with $\varrho_n^L(t)=0$ when the CPU is idle. If $\mathcal{H}_i^L(t)$ denotes the waiting tasks placed before $\xi_i$ under the current hypothetical ERT order, the estimated waiting time is


\begin{equation}
\widehat W_i^L(t)=\varrho_n^L(t)+\sum_{\xi_h\in\mathcal{H}_i^L(t)}\tau_h^L,
\tag{10}
\end{equation}


and the estimated local completion slot is


\begin{equation}
\widehat T_i^L(t)=t+\widehat W_i^L(t)+\tau_i^L-1.
\tag{11}
\end{equation}


For a newly arrived task, ECHO evaluates a hypothetical insertion into the local queue, computes the resulting order and completion slot, and uses this value as the local candidate completion estimate. Once local execution starts, it is not preempted by a newly arriving task. Waiting tasks can be reordered only at a later service epoch when the CPU is idle.


The deadline and completion records remain separate. ECHO does not truncate $\widehat T_i^L(t)$ at $d_i$, because truncation would hide predicted lateness and underestimate resource occupancy. A task is successfully completed only when its realized completion slot does not exceed its absolute deadline. If its deadline expires before successful completion, it is handled according to the task-lifecycle rule: a waiting task is removed, whereas an active non-preemptive operation retains the resource until completion and its result is recorded as dropped.


Whenever a task is admitted, completed, removed, or selected for service, the waiting-task order and completion estimates are updated. This local-queue model supplies the local completion value used in queue-level ERT and in the local candidate comparison.






5) Outbound-Transfer Queue Model
The outbound-transfer queue stores tasks whose ECHO action selects horizontal or vertical offloading. When such an action is selected, destination $k_i=\kappa(\alpha_i)$ is stored with the task together with its source, arrival slot, size, processing density, and deadline. The dispatch block in Fig. 2 applies this stored destination when the task enters transmission; it does not perform a second destination decision.


Let $\mathcal{Q}_n^X(t)$ contain the waiting outbound-transfer tasks, excluding any transmission currently in service. Transmission is non-preemptive. The rate associated with the stored destination is


\begin{equation}
R_{s_i,k_i}=\begin{cases}R_H, & k_i\in\mathcal{E}\setminus\{s_i\},\\ R_V, & k_i=N+1.\end{cases}
\tag{12}
\end{equation}


A horizontal destination must also satisfy $G(s_i,k_i)=1$. The transmission duration of task $\xi_i$ is


\begin{equation}
\tau_{i,k_i}^X=\left\lceil\frac{b_i}{R_{s_i,k_i}\Delta}\right\rceil.
\tag{13}
\end{equation}


Let $\varrho_n^X(t)$ be the residual transmission time of the task currently in service, or zero if the transfer resource is idle. If $\mathcal{H}_i^X(t)$ is the set of waiting tasks placed before $\xi_i$ under the current hypothetical ERT order, its estimated waiting and source-stage completion times are


\begin{equation}
\widehat W_i^X(t)=\varrho_n^X(t)+\sum_{\xi_h\in\mathcal{H}_i^X(t)}\tau_{h,k_h}^X,
\tag{14}
\end{equation}


\begin{equation}
\widehat T_{i,k_i}^X(t)=t+\widehat W_i^X(t)+\tau_{i,k_i}^X-1.
\tag{15}
\end{equation}


The estimated arrival slot at the stored destination queue is


\begin{equation}
\widehat t_{i,k_i}^D(t)=\widehat T_{i,k_i}^X(t)+1.
\tag{16}
\end{equation}


The completion estimate is not truncated at the deadline. Keeping the complete value is necessary for ERT and lateness calculation and for estimating when the transmission resource becomes available. A task that expires before successful transmission or completion is handled according to the task-lifecycle rule and recorded as dropped; an active non-preemptive transmission retains the resource until it finishes, and the deadline remains separate from estimated and realized completion time.


When an offloading candidate is evaluated, its destination determines the transmission duration and the task is inserted hypothetically into the outbound-transfer queue to estimate its provisional position, waiting time, and source-stage completion. After the action is chosen, that destination remains attached to the task. Whenever queue membership or active service changes, the hypothetical waiting and completion estimates of waiting tasks are recalculated before the next non-preemptive service decision.






6) Destination Queue and Load Model
Destination queues use the source-indexed organization in [37] and represent processing workloads received from other EAs. Each destination node $k$ maintains a source-indexed queue $\mathcal{Q}_{n\rightarrow k}^D(t)$ for tasks originating from EA $n$. This separation prevents collisions between simultaneous arrivals from different sources. A source EA does not reorder a destination queue. FIFO order is retained within each source-indexed destination queue, while the destination processor shares its processing capacity among active queues according to the architecture in [37]. These queues provide workload information for candidate completion estimation.


A queue is active when it contains unfinished computational workload. To avoid a notation collision with the action set, the active destination-queue set and its cardinality are denoted by


\begin{equation}
\mathcal{J}_k(t)=\begin{cases}\left\{n\in\mathcal{E}\setminus\{k\}\mid \Omega_{n\rightarrow k}(t)>0\right\}, & k\in\mathcal{E},\\\left\{n\in\mathcal{E}\mid \Omega_{n\rightarrow k}(t)>0\right\}, & k=N+1.\end{cases}
\tag{17}
\end{equation}


\begin{equation}
p_k(t)=\left|\mathcal{J}_k(t)\right|.
\tag{18}
\end{equation}


Because queued tasks may have different processing densities, destination load is represented in remaining CPU cycles rather than only in bits. Let $b_h^{rem}(t)$ be the remaining bits of queued task $\xi_h$ and $\nu_h$ its processing density. The remaining workload in the source-indexed destination queue is


\begin{equation}
\Omega_{n\rightarrow k}(t)=\sum_{\xi_h\in \mathcal{Q}_{n\rightarrow k}^D(t)}b_h^{rem}(t)\nu_h.
\tag{19}
\end{equation}


When candidate $n\rightarrow k$ is evaluated, admission of the new task may activate a previously inactive source queue. The adjusted number of active queues is


\begin{equation}
\bar p_{n,k}(t)=\max\left\{1,p_k(t)+\mathbb{I}\left[n\notin\mathcal{J}_k(t)\right]\right\}.
\tag{20}
\end{equation}


Let the total destination processing capacity of node $k$ be


\begin{equation}
f_k^D=\begin{cases}f_k^{EA}, & k\in\mathcal{E},\\ f^C, & k=N+1.\end{cases}
\tag{21}
\end{equation}


The effective capacity assigned to the candidate source queue is estimated as


\begin{equation}
\bar f_{n,k}^D(t)=\frac{f_k^D}{\bar p_{n,k}(t)}.
\tag{22}
\end{equation}


This definition is always finite, including when the destination is initially idle. Candidate evaluation must, however, use the destination conditions expected when the task actually arrives rather than silently treating the decision-time workload as unchanged. Let $\widehat\Omega_{s_i\rightarrow k}(\widehat t_{i,k}^D(t)\mid t)$ and $\widehat p_k(\widehat t_{i,k}^D(t)\mid t)$ denote the remaining cycle workload and active-queue count predicted at the estimated destination-arrival slot using information available at decision time $t$. The corresponding adjusted active-queue count and effective capacity are
$\widehat{\bar p}_{s_i,k}(\widehat t_{i,k}^D(t)\mid t)=\max\{1,\widehat p_k(\widehat t_{i,k}^D(t)\mid t)+\mathbb I[s_i\notin\widehat{\mathcal J}_k(\widehat t_{i,k}^D(t)\mid t)]\}$ and $\widehat{\bar f}_{s_i,k}^D(\widehat t_{i,k}^D(t)\mid t)=f_k^D/\widehat{\bar p}_{s_i,k}(\widehat t_{i,k}^D(t)\mid t)$. When no horizon-specific forecast is available, the newest observed quantities are used as an explicitly logged fallback and their information age is retained.


The destination-side waiting time and processing duration of candidate task $\xi_i$ are
\begin{equation}
\widehat W_{i,k}^D(t)=\left\lceil\frac{\widehat\Omega_{s_i\rightarrow k}(\widehat t_{i,k}^D(t)\mid t)}{\widehat{\bar f}_{s_i,k}^D(\widehat t_{i,k}^D(t)\mid t)\Delta}\right\rceil,
\tag{23}
\end{equation}
\begin{equation}
\tau_{i,k}^D(t)=\left\lceil\frac{b_i\nu_i}{\widehat{\bar f}_{s_i,k}^D(\widehat t_{i,k}^D(t)\mid t)\Delta}\right\rceil.
\tag{24}
\end{equation}
If task $\xi_i$ is expected to reach destination queue $k$ at $\widehat t_{i,k}^D(t)$, its estimated end-to-end offloading completion slot is
\begin{equation}
\widehat T_{i,k}^O(t)=\widehat t_{i,k}^D(t)+\widehat W_{i,k}^D(t)+\tau_{i,k}^D(t)-1.
\tag{25}
\end{equation}
This estimator includes source waiting, transmission, predicted arrival-time destination workload, the capacity reduction caused by concurrent active destination queues, and candidate processing. Actual destination admission still occurs only after source-side transmission completes; selecting an offloading action does not immediately place the task in a destination queue.


Destination information may remain imperfect because ECHO is distributed and future unobserved arrivals cannot be known. The arrival-time estimator is therefore a decision-time forecast rather than an oracle. Its adequacy is evaluated from signed and absolute completion-time errors, false-feasible and false-infeasible mask rates, and calibration stratified by route, load, forecast horizon, and information age. No deterministic deadline guarantee is claimed under unobserved future events.














7) Historical Load and Load Estimation
Historical load captures the recent destination-side workload observed by an EA without requiring global knowledge of future task arrivals. Consistent with the destination-queue model, each destination entry includes the remaining computational workload in CPU cycles and the number of active destination queues. The observed load vector available to EA $n$ is


\begin{equation}
\mathbf{o}_n(t)=\left[\widehat\Omega_{n\rightarrow k}(t),p_k(t)\right]_{k\in\mathcal{N}\setminus\{n\}}.
\tag{26}
\end{equation}


Using a lookback window of length $W$, the historical matrix is


\begin{equation}
\mathbf{H}_n(t)=\left[\mathbf{o}_n(t-W+1),\ldots,\mathbf{o}_n(t)\right].
\tag{27}
\end{equation}


The recurrent load encoder follows the distributed forecasting design in [37], but its representation and prediction outputs are trained explicitly. For a history matrix $\mathbf H_n(t)$,
\begin{equation}
\left(\mathbf{z}_n(t),\widehat{\mathbf{H}}_n(t+1)\right)=F_\psi\!\left(\mathbf{H}_n(t)\right),\qquad \mathcal{L}_{pred}(\psi)=\frac{1}{|\mathcal{B}_{pred}|}\sum_{u\in\mathcal{B}_{pred}}\left\|\widehat{\mathbf{H}}_n^{(u)}(t+1)-\mathbf{o}_n^{(u)}(t+1)\right\|_2^2.
\tag{28}
\end{equation}
Here $\mathbf z_n(t)$ is the fixed-dimensional embedding supplied to the Q-network, while $\widehat{\mathbf H}_n(t+1)$ is the decoded next-slot destination-load representation used to extrapolate workload and active-queue conditions to a candidate's estimated destination-arrival slot. A fresh controller report replaces the forecast for every horizon it directly covers. When a report is delayed or unavailable, the latest history and recurrent forecast supply the arrival-time workload estimate and its information age.


The recurrent model uses a separate supervised optimizer and one-step forecasting targets drawn only from training traces. The Q-network consumes a detached copy of $\mathbf z_n(t)$, so DQL gradients do not update the forecasting model. Validation traces determine the forecasting checkpoint, clipping choices, and early stopping; held-out evaluation traces are never used for fitting. Every forecast consumed by completion estimation records its prediction horizon and report age so that calibration can be stratified by route, load, horizon, and information age.




  

Figure 2. Internal structure of an ECHO-enabled Edge Agent, including local, outbound-transfer, and destination queues, end-to-end completion estimation, ERT-based scheduling, and masked hybrid decisions.


  

Figure 3. Workflow of the proposed ECHO method, from task arrival and deadline-aware route evaluation to ERT-based scheduling, execution, and delayed learning update.


Figure 3 summarizes the operational workflow of ECHO, beginning with task arrival, deadline construction, and completion-time estimation for local, horizontal-edge, and vertical-cloud routes, and continuing through candidate-level ERT evaluation, queue scheduling, execution, and learning update. At each decision epoch, ECHO first checks whether any deadline-feasible route exists; when one or more valid routes are available, the learned policy selects among them through the action mask, whereas an empty valid set invokes the minimum-lateness fallback before the task outcome is recorded for reward and replay generation.














C. Effective Remaining Time Model


The central timing variable of the proposed framework is Effective Remaining Time (ERT). A raw timeout value only specifies the maximum allowed completion bound of a task, but it does not show how much feasible time remains after queueing, transmission, destination load, and processing requirements are considered. Therefore, ERT is introduced to convert deadline information into an operational urgency indicator that can be used before the task is completed or dropped.


Two complementary forms of ERT are defined. Queue-level ERT is used to rank pending tasks inside a source-side queue, while candidate-level ERT is used to evaluate whether a local, horizontal edge, or vertical cloud execution path is feasible before the final offloading action is selected.


1) Queue-Level ERT
Queue-level ERT measures the urgency of a task waiting in a source-side local or outbound-transfer queue. Local ERT uses the local completion estimate, whereas transfer ERT uses the end-to-end offloading estimate that includes source waiting, transmission, destination waiting, and destination processing.


For a task $\xi_i$ waiting in the local queue, queue-level ERT is


\begin{equation}
\mathsf{ERT}_i^L(t)=d_i-\widehat T_i^L(t).
\tag{29}
\end{equation}


For a task in the outbound-transfer queue with stored destination $k_i=\kappa(\alpha_i)$, end-to-end queue ERT is defined in (30).


Unlike a source-stage transmission slack, the transfer ERT in (30) is end-to-end:


\begin{equation}
\mathsf{ERT}_i^X(t)=d_i-\widehat T_{i,k_i}^O(t).
\tag{30}
\end{equation}


A positive value indicates predicted completion before the deadline, zero denotes the feasibility boundary, and a negative value indicates predicted lateness. A negative estimate is not the same as actual expiration; expiration depends on the current slot and the realized task lifecycle.


The provisional order is constructed iteratively. Starting after the residual active service, ECHO evaluates each unscheduled task in the next position, selects the smallest non-negative ERT or the minimum-lateness task when none is feasible, appends it to the provisional order, and repeats. Completion estimates and ERT values are recomputed whenever queue membership or service state changes.






2) Candidate-Level ERT
Candidate-level ERT compares the local, horizontal-edge, and vertical-cloud routes for the same arriving task. The unified route-completion estimate is


\begin{equation}
\widehat T_i(\alpha,t)=\begin{cases}\widehat T_i^L(t), & \alpha=\alpha_{s_i}^L,\\\widehat T_{i,k}^O(t), & \kappa(\alpha)=k\neq s_i.\end{cases}
\tag{31}
\end{equation}


Candidate-level Effective Remaining Time is then defined as


For every physically available action $\alpha\in\mathcal{A}_{s_i}(t)$,


\begin{equation}
\mathsf{ERT}_i^C(\alpha,t)=
d_i-\widehat T_i(\alpha,t).
\tag{32}
\end{equation}


A non-negative candidate ERT is exactly equivalent to the estimated deadline-feasibility condition $\widehat T_i(\alpha,t)\leq d_i$. The valid action set is defined once in Section E from this condition.


ERT is therefore a completion-slack variable rather than an unrelated heuristic score: it directly measures the deadline remaining after the estimated route completion requirement is accounted for.






3) ERT Interpretation
The sign and magnitude of ERT provide a compact interpretation of task urgency. A large positive ERT means that the task has sufficient remaining time and can tolerate some queueing or transmission delay. A small positive ERT indicates that the task is still feasible but urgent. A zero ERT represents a boundary condition in which any additional delay may cause deadline violation. A negative ERT indicates that the task is estimated to miss its deadline under the current queue or candidate condition.


ECHO uses this interpretation consistently across the decision pipeline. At the queue level, the smallest non-negative ERT identifies the most urgent predicted-feasible task, while minimum lateness is used when all waiting tasks are predicted late. At candidate selection, negative-ERT actions are masked whenever at least one valid action exists; if all actions are negative, the minimum-lateness fallback is selected and its predicted miss risk is stored for reward calculation. Actual task removal is penalized separately. Thus, ERT connects deadline representation, queue scheduling, candidate filtering, and distributed DRL learning.






4) Deterministic ERT-Order Construction and Complexity
Because the completion estimate of a waiting task depends on the predecessors placed before it, ERT ordering is defined by a constructive procedure rather than by evaluating all tasks under an unspecified final order. For a queue containing $q$ waiting tasks, ECHO initializes a cumulative source workload with the residual time of the active non-preemptive operation. At provisional position $r=1,\ldots,q$, it performs the following steps: (i) evaluate every unscheduled task as the next task after the already fixed prefix; (ii) compute its provisional completion time and ERT using the current cumulative workload and, for a transfer task, its stored destination and the current destination estimate; (iii) form the subset with non-negative ERT; (iv) select the smallest non-negative ERT when that subset is non-empty, otherwise select the smallest estimated lateness; (v) break exact ties by original FIFO arrival order; and (vi) append the selected task to the fixed prefix and update the cumulative source workload. The procedure terminates after every waiting task has exactly one position. Thus, the predecessor sets in (10) and (14) are outputs of the constructive order and are not assumed in advance.


With cumulative source workload maintained incrementally, at most $q+(q-1)+\cdots+1=q(q+1)/2$ candidate evaluations are required, giving $O(q^2)$ time and $O(q)$ temporary storage per queue rebuild. Candidate-level route evaluation for one arriving task requires $O(|\mathcal{A}_n(t)|)$ completion and mask evaluations, and the canonical action output has $O(N)$ positions. Neural inference retains the complexity of one forward pass through the LSTM and Dueling-DQL networks. These costs are measured separately in the evaluation through decision latency and queue-rebuild time rather than being assumed negligible.
Equations (33)--(40) are the local-queue and outbound-queue instantiations of this single deterministic scheduler; they do not define separate scheduling algorithms.




D. Deadline-Aware Queue Scheduling


ECHO controls the service order of the local and outbound-transfer queues. Scheduling is non-preemptive: an active computation or transmission continues until completion, while waiting tasks may be reordered whenever the corresponding resource becomes idle. Expired waiting tasks are removed before each service selection, and completion estimates are recomputed.


1) Local Queue Scheduling
Let $\mathcal{Q}_n^L(t)$ contain the waiting local tasks, excluding any task currently in service. The predicted-feasible local-task set is


\begin{equation}
\mathcal{F}_n^L(t)=\left\{\xi_i\in\mathcal{Q}_n^L(t)\mid \mathsf{ERT}_i^L(t)\geq0\right\}.
\tag{33}
\end{equation}


If this set is non-empty, the local processor selects the task with the smallest non-negative ERT:


\begin{equation}
\xi_n^{L,*}(t)=\arg\min_{\xi_i\in\mathcal{F}_n^L(t)}\mathsf{ERT}_i^L(t).
\tag{34}
\end{equation}


If all waiting tasks are predicted late, ECHO does not give automatic priority to the most negative ERT. Instead, it selects the task with the smallest estimated queue-level lateness,


\begin{equation}
\ell_i^L(t)=\max\left\{0,\widehat T_i^L(t)-d_i\right\},
\tag{35}
\end{equation}


\begin{equation}
\xi_n^{L,*}(t)=\arg\min_{\xi_i\in\mathcal{Q}_n^L(t)}\ell_i^L(t),\quad \mathcal{F}_n^L(t)=\emptyset.
\tag{36}
\end{equation}


FIFO order is used only to break equal ERT or equal-lateness values. After admission, completion, removal, or service selection, the provisional order and all local completion and ERT values are updated.


2) Outbound-Transfer Queue Scheduling
The same non-preemptive rule is applied before transmission. Let $\mathcal{Q}_n^X(t)$ contain the waiting outbound-transfer tasks, each retaining destination $k_i=\kappa(\alpha_i)$. The predicted-feasible transfer set is


\begin{equation}
\mathcal{F}_n^X(t)=\left\{\xi_i\in\mathcal{Q}_n^X(t)\mid \mathsf{ERT}_i^X(t)\geq0\right\}.
\tag{37}
\end{equation}


When this set is non-empty, the next transmitted task is


\begin{equation}
\xi_n^{X,*}(t)=\arg\min_{\xi_i\in\mathcal{F}_n^X(t)}\mathsf{ERT}_i^X(t).
\tag{38}
\end{equation}


When every waiting transfer task is predicted late, the source EA uses end-to-end minimum lateness:


\begin{equation}
\ell_i^X(t)=\max\left\{0,\widehat T_{i,k_i}^O(t)-d_i\right\},
\tag{39}
\end{equation}


\begin{equation}
\xi_n^{X,*}(t)=\arg\min_{\xi_i\in\mathcal{Q}_n^X(t)}\ell_i^X(t),\quad \mathcal{F}_n^X(t)=\emptyset.
\tag{40}
\end{equation}


The selected task is transmitted to its stored destination; the dispatch block applies that destination without a new decision. FIFO remains the tie-breaker. This rule prevents an already highly late task from automatically displacing a still-feasible urgent task merely because its ERT is more negative.


3) Destination Queue Consideration
Destination queues remain destination-side processing structures and are not reordered by the source EA. Their remaining computational workload, adjusted active-queue count, and observed or LSTM-predicted load are used to estimate candidate completion time and candidate-level ERT. Thus, ECHO directly controls the service order only in the source local and outbound-transfer queues, while destination-queue conditions influence destination feasibility through completion-time estimation.














E. Deadline-Aware Candidate Selection
For each arriving task, ECHO evaluates the direct local, horizontal-edge, and vertical-cloud actions defined in (3). Candidate completion and ERT are computed by (31)-(32) before the task is inserted into a source queue.


1) Fixed and Deadline-Valid Action Sets


The fixed canonical output set of EA n is defined in (41). The source position and disconnected horizontal destinations remain in the fixed network output but are marked unavailable.


\begin{equation}
\bar{\mathcal{A}}_n=\{\alpha_n^L,\alpha_{n,1}^H,\ldots,\alpha_{n,N}^H,\alpha_n^V\}.
\tag{41}
\end{equation}


The deadline-valid set for task i is defined in (42).


\begin{equation}
\mathcal{V}_i(t)=\{\alpha\in\mathcal{A}_{s_i}(t)\mid \mathsf{ERT}_i^C(\alpha,t)\geq0\}.
\tag{42}
\end{equation}


2) Minimum-Lateness Fallback


If no action is predicted to satisfy the deadline, candidate lateness and the fallback action are defined in (43)-(44).


\begin{equation}
\Lambda_i(\alpha,t)=\max\{0,\widehat T_i(\alpha,t)-d_i\}.
\tag{43}
\end{equation}


\begin{equation}
\alpha_i^{fb}(t)=\arg\min_{\alpha\in\mathcal{A}_{s_i}(t)}\Lambda_i(\alpha,t).
\tag{44}
\end{equation}


The fallback avoids an arbitrary choice under overload. In addition to storing the empty-valid-set indicator, ECHO retains the selected fallback action's predicted lateness so that two infeasible actions do not receive an identical decision-time penalty when one is substantially less late.


3) Effective Set and Action Mask


The effective set and the binary canonical-action mask are defined in (45)-(46).


\begin{equation}
\mathcal{U}_i(t)=\begin{cases}\mathcal{V}_i(t), & \mathcal{V}_i(t)\neq\emptyset,\\ \{\alpha_i^{fb}(t)\}, & \mathcal{V}_i(t)=\emptyset.\end{cases}
\tag{45}
\end{equation}


\begin{equation}
\mu_{s_i,j}(t)=\mathbb{I}[\bar\alpha_{s_i,j}\in\mathcal{A}_{s_i}(t)]\,\mathbb{I}[\bar\alpha_{s_i,j}\in\mathcal{U}_i(t)],\qquad \boldsymbol{\mu}_{s_i}(t)=[\mu_{s_i,j}(t)]_j.
\tag{46}
\end{equation}




The same mask is used in exploration, exploitation, and Double-DQL target-action selection.


4) Direct Decision and Queue Admission


Action admissibility, source-queue admission, stored dispatch metadata, and the pending decision record are specified in (47)-(50).


\begin{equation}
\alpha_i\in\mathcal{U}_i(t_i^a).
\tag{47}
\end{equation}


\begin{equation}
\xi_i\in\mathcal{Q}_i^{src}(t_i^a).
\tag{48}
\end{equation}


\begin{equation}
\mathbf{g}_i^{base}=(s_i,t_i^a,b_i,\nu_i,d_i),\qquad \mathbf{g}_i^{off}=(\mathbf{g}_i^{base},k_i)\ \text{only when }\kappa(\alpha_i)\neq s_i.
\tag{49}
\end{equation}




\begin{equation}
\mathbf{p}_i=(\xi_i,\mathbf{s}_{s_i}(t_i^a),\boldsymbol{\mu}_{s_i}(t_i^a),\alpha_i,t_i^a,d_i,\widehat T_i(\alpha_i,t_i^a),\mathsf{ERT}_i^C(\alpha_i,t_i^a),\Lambda_i(\alpha_i,t_i^a),I_i^R)\in\mathcal{P}_{s_i}.
\tag{50}
\end{equation}




Thus, action selection occurs once at task arrival. The selected action belongs to the effective set in (47), the task is admitted by (48), and only an offloaded task receives the destination extension in (49). The pending record in (50) preserves all decision-time quantities required to calculate the delayed reward without recomputing them from a later environment state. No second destination optimization is performed.




F. Multi-Agent Distributed DRL Formulation


Each EA acts as an autonomous learning agent. The recurrent load encoder, dueling value–advantage decomposition, Double-DQL target separation, replay memory, and target network follow established distributed learning components [37]. ECHO defines its own state, admissible actions, reward semantics, and event-driven semi-Markov interval transition timing.


1) State Representation


Queue occupancies and remaining source-side workloads are defined in (51)-(52).


\begin{equation}
q_n^L(t)=|\mathcal{Q}_n^L(t)|,\qquad q_n^X(t)=|\mathcal{Q}_n^X(t)|.
\tag{51}
\end{equation}


\begin{equation}
\Psi_n^L(t)=\varrho_n^L(t)+\sum_{\xi_h\in\mathcal{Q}_n^L(t)}\tau_h^L,\qquad \Psi_n^X(t)=\varrho_n^X(t)+\sum_{\xi_h\in\mathcal{Q}_n^X(t)}\tau_{h,k_h}^X.
\tag{52}
\end{equation}


For a fixed network size $N$, the size-specific fixed-dimensional normalized state is defined in (53).


\begin{equation}
\mathbf{s}_n(t)=[\tilde\chi_n(t),\tilde b_i,\tilde\nu_i,\tilde\delta_i,\tilde q_n^L,\tilde q_n^X,\tilde\Psi_n^L,\tilde\Psi_n^X,\tilde\varrho_n^L,\tilde\varrho_n^X,\tilde{\mathbf{o}}_n,\mathbf{z}_n,\widetilde{\mathsf{ERT}}_{n,\min}^L,\widetilde{\mathsf{ERT}}_{n,\min}^X,\widetilde{\bar{\mathbf e}}_i^C,\boldsymbol{\mu}_n].
\tag{53}
\end{equation}




When no task arrives, task-specific and candidate-specific entries are zero, while queue, service, and load entries remain active. Queue occupancies distinguish an empty queue from a queue whose minimum ERT is exactly zero. Numerical features are min–max normalized to bounded ranges, ERT values are symmetrically clipped before normalization, and the action mask is zero when no decision is required.


The fixed candidate-ERT vector is defined over every canonical output position. Let $E_{\max}>0$ be the symmetric clipping bound. Physically invalid canonical positions are assigned the lower clipped sentinel and remain disabled by the mask:
\begin{equation}
\bar e_{i,j}^C(t)=\begin{cases}\operatorname{clip}\!\left(\mathsf{ERT}_i^C(\bar\alpha_{s_i,j},t),-E_{\max},E_{\max}\right), & \bar\alpha_{s_i,j}\in\mathcal{A}_{s_i}(t),\\-E_{\max}, & \bar\alpha_{s_i,j}\notin\mathcal{A}_{s_i}(t),\end{cases}\qquad \bar{\mathbf e}_i^C(t)=[\bar e_{i,j}^C(t)]_j.
\tag{54}
\end{equation}
The accompanying mask distinguishes a genuinely urgent boundary value from a physically unavailable output position.




For the network-size experiments, ECHO uses a size-specific but semantically identical architecture rather than padding all experiments to an arbitrary maximum. For a system with $N$ EAs, the ordered destination-load blocks and candidate-action outputs are constructed for exactly those $N$ nodes, giving a canonical action dimension of $N+2$: one local action, $N$ horizontal-destination positions, and one cloud action. The source position and disconnected destinations remain present but are disabled by the physical-and-deadline mask. For every tested value $N\in\{10,15,20,25,30\}$, a separate size-specific campaign is trained and evaluated. Consistent with the distributed HOODIE foundation, each EA retains its own learner and checkpoint rather than sharing policy parameters across EAs; the same per-agent architecture, hyperparameters, seed policy, and training budget are used at every tested size. State fields retain the same definition and ordering for every existing destination; only the number of destination blocks changes with the experimental topology. Therefore, the scalability study measures independently trained policies at different system sizes and makes no claim that one checkpoint transfers zero-shot between different values of $N$.


2) Effective Actions


The fixed canonical set, deadline-valid set, fallback, effective set, and action mask are already defined in (41)-(46) and are used without changing the network output dimension.


3) Task Outcome and Reward


Task i is resolved at slot t_i^r by deadline-satisfied completion or by a dropped outcome. Its realized system duration is defined in (55).


\begin{equation}
T_i^{sys}=t_i^r-t_i^a+1.
\tag{55}
\end{equation}


The predicted-risk and realized-drop indicators are defined in (56)-(57).


\begin{equation}
I_i^R=\begin{cases}1, & \mathcal{V}_i(t_i^a)=\emptyset,\\0, & \text{otherwise}.\end{cases}
\tag{56}
\end{equation}


\begin{equation}
I_i^D=\begin{cases}1, & \xi_i\text{ does not achieve deadline-satisfied completion},\\0, & \text{otherwise}.\end{cases}
\tag{57}
\end{equation}


The task-level reward is defined in (58).


\begin{equation}
r_i=-T_i^{sys}-\lambda_R\left(I_i^R+\frac{\Lambda_i(\alpha_i,t_i^a)}{\max\{1,\delta_i\}}\right)-\lambda_D I_i^D.
\tag{58}
\end{equation}


The decision-time term has two complementary parts. The indicator $I_i^R$ marks that every physical action was predicted infeasible, while the deadline-normalized selected-action lateness $\Lambda_i(\alpha_i,t_i^a)/\max\{1,\delta_i\}$ differentiates fallback actions according to the severity of their predicted miss. For a selected deadline-feasible action, this lateness term is zero. The realized-drop term remains separate because changing load may invalidate an initially feasible action, while a fallback action may occasionally achieve deadline-satisfied completion.


4) Agent-Specific Event-Driven Semi-Markov Formulation and Markov Property
For each EA $n$, let $\tau_{n,m}$ denote the slot of its $m$th actual route decision, namely the $m$th slot in which $\chi_n(t)=1$. The terminal epoch is set to the first terminal decision state after the episode, and the agent-specific sojourn is $\Delta_{n,m}=\tau_{n,m+1}-\tau_{n,m}$. This construction avoids introducing an artificial no-decision action for EAs that receive no task at a global arrival slot.


Let $\mathbf{x}_{n,m}$ denote the complete simulator state sampled immediately before the action of EA $n$ at $\tau_{n,m}$. It contains the topology, all waiting and active task records, absolute deadlines, stored destinations, residual local and transmission services, source-indexed destination workloads, current processing and link conditions, load histories, and unresolved outcome records. The policy observation $\mathbf{s}_n(\tau_{n,m})$ in (53) is the decentralized compression $h_n(\mathbf{x}_{n,m})$ supplied to the learner.


The action $\alpha_{n,m}$ is the route selected for the task arriving at epoch $\tau_{n,m}$. Boundary outcomes applied before the next action at $\tau_{n,m+1}$ close the preceding interval. Consequently, every source-$n$ task reward produced after the action at $\tau_{n,m}$ and no later than the pre-action boundary of $\tau_{n,m+1}$ contributes to that interval. The discounted interval reward is
\begin{equation}
\rho_{n,m}=\sum_{\substack{\xi_i:s_i=n,\\\tau_{n,m}<t_i^r\leq\tau_{n,m+1}}}\gamma^{t_i^r-\tau_{n,m}}r_i,\qquad \Delta_{n,m}=\tau_{n,m+1}-\tau_{n,m}.
\tag{59}
\end{equation}
The replay transition is therefore
$\zeta_{n,m}=(\mathbf{s}_n(\tau_{n,m}),\alpha_{n,m},\rho_{n,m},\mathbf{s}_n(\tau_{n,m+1}),\Delta_{n,m})$,
with the next-state mask stored as part of $\mathbf{s}_n(\tau_{n,m+1})$. The first route decision of an EA opens an interval but does not finalize a predecessor transition. At every later route decision, the current task descriptor, candidate ERT values, and mask are computed first; the resulting complete pre-action observation then closes the previous interval. At terminal epoch $T+1$, all end-of-episode outcomes are resolved exactly once, the terminal observation and terminal flag are formed, and the last open interval is finalized with $\Delta_{n,m}=T+1-\tau_{n,m}$. Pending task records determine source, decision-time quantities, outcome time, and reward, but they never create overlapping task-level replay transitions. Each resolved reward is assigned to exactly one source-specific interval.




Proposition 1 (agent-epoch embedded Markov property). Assume that exogenous arrivals and time-varying resource processes are Markov and included in the complete state, service and transmission evolution depends only on current queue and residual-work records, and the finite history required by the predictor is included in $\mathbf{x}_{n,m}$. Then the process sampled at the stopping times $\{\tau_{n,m}\}$ satisfies
\begin{equation}
\Pr(\mathbf{x}_{n,m+1},\Delta_{n,m},\rho_{n,m}\mid \mathbf{x}_{n,0},\alpha_{n,0},\ldots,\mathbf{x}_{n,m},\alpha_{n,m})
=\Pr(\mathbf{x}_{n,m+1},\Delta_{n,m},\rho_{n,m}\mid \mathbf{x}_{n,m},\alpha_{n,m}).
\tag{60}
\end{equation}
Proof. The slot-level simulator is Markov in the complete state because that state contains every variable required to determine the next boundary event, service progression, arrival distribution, and task outcome. Each $\tau_{n,m}$ is a stopping time with respect to this process. By the strong Markov property, conditional on $\mathbf{x}_{n,m}$ and action $\alpha_{n,m}$, the distribution of the next decision state of EA $n$, its sojourn time, and all source-$n$ rewards accumulated before that state is independent of states and actions preceding $\tau_{n,m}$. Hence the embedded decision process is an SMDP on the complete state.


The induced semi-Markov transition kernel is $K_n(B,\delta,r\mid\mathbf{x},\alpha)=\Pr(\mathbf{x}_{n,m+1}\in B,\Delta_{n,m}=\delta,\rho_{n,m}=r\mid\mathbf{x}_{n,m}=\mathbf{x},\alpha_{n,m}=\alpha)$. Therefore, on the complete state, the optimal action-value function satisfies the SMDP Bellman relation $Q_n^*(\mathbf{x},\alpha)=\mathbb{E}[\rho_{n,m}+\gamma^{\Delta_{n,m}}\max_{\alpha'}Q_n^*(\mathbf{x}_{n,m+1},\alpha')\mid\mathbf{x}_{n,m}=\mathbf{x},\alpha_{n,m}=\alpha]$, with the continuation term omitted at the terminal epoch. This establishes the mathematical basis for the $\gamma^{\Delta_{n,m}}$ target rather than treating it as an ad hoc delayed-reward correction.


The decentralized learner does not observe $\mathbf{x}_{n,m}$ directly. It uses $\mathbf{s}_n=h_n(\mathbf{x}_{n,m})$ and is therefore a partially observed function approximation to the proven SMDP. The mathematical Markov claim applies to the complete simulator state, while the empirical evaluation determines whether the chosen decentralized observation is sufficiently informative. This formulation retains delayed credit assignment, avoids unsupported overlapping task transitions, requires no learned no-operation action, and yields the Bellman discount $\gamma^{\Delta_{n,m}}$ used below.


5) Dueling Double-DQL Model


The LSTM embedding in (28) is concatenated with the remaining state features before the fully connected layers. The Dueling-DQL and Double-DQL components follow [37], while ECHO uses the state, mask, reward, and semi-Markov target defined here.


\begin{equation}
Q_n(\mathbf{s},\alpha;\theta_n)=V_n(\mathbf{s};\theta_n)+A_n(\mathbf{s},\alpha;\theta_n)-\frac{1}{|\bar{\mathcal{A}}_n|}\sum_{\alpha'\in\bar{\mathcal{A}}_n}A_n(\mathbf{s},\alpha';\theta_n).
\tag{61}
\end{equation}


\begin{equation}
Q_n^\mu(\mathbf{s},\alpha;t)=\begin{cases}Q_n(\mathbf{s},\alpha;\theta_n), & \alpha\in\mathcal{U}_i(t),\\-\infty, & \alpha\notin\mathcal{U}_i(t).\end{cases}
\tag{62}
\end{equation}


During training, action selection follows the masked epsilon-greedy rule in (63).


\begin{equation}
\alpha_i=\begin{cases}\text{uniform sample from }\mathcal{U}_i(t_i^a), & \text{with probability }\epsilon,\\\arg\max_{\alpha\in\bar{\mathcal{A}}_{s_i}}Q_{s_i}^\mu(\mathbf{s}_{s_i}(t_i^a),\alpha;t_i^a), & \text{with probability }1-\epsilon.\end{cases}
\tag{63}
\end{equation}


For a replayed transition, the masked next action, Double-DQL target, online prediction, and mini-batch loss are defined in (64)-(67).


\begin{equation}
\alpha_{n,m+1}^+=\arg\max_{\alpha'\in\bar{\mathcal{A}}_n}Q_n^\mu(\mathbf{s}_n(\tau_{n,m+1}),\alpha';\tau_{n,m+1}).
\tag{64}
\end{equation}


\begin{equation}
y_{n,m}=\begin{cases}\rho_{n,m}, & \text{if the stored next state is terminal},\\\rho_{n,m}+\gamma^{\Delta_{n,m}}Q_n^-(\mathbf{s}_n(\tau_{n,m+1}),\alpha_{n,m+1}^+;\theta_n^-), & \text{otherwise},\end{cases}
\tag{65}
\end{equation}
The action $\alpha_{n,m+1}^+$ is computed from the mask stored with the fully constructed next decision observation. A terminal transition carries an explicit terminal flag and no continuation value; an all-zero terminal mask is therefore never passed to the argmax in (64).




\begin{equation}
\widehat y_{n,m}=Q_n(\mathbf{s}_n(\tau_{n,m}),\alpha_{n,m};\theta_n).
\tag{66}
\end{equation}


\begin{equation}
\mathcal{L}_n(\theta_n)=\frac{1}{|B|}\sum_{(n,m)\in B}(y_{n,m}-\widehat y_{n,m})^2.
\tag{67}
\end{equation}


The target parameters are copied from the online parameters every target-copy period. The same action mask is applied during exploration, exploitation, and target-action selection.


G. Algorithmic Workflow of ECHO


The training and inference procedures use the same slot-level environment sequence. Service is non-preemptive, an offloaded task carries its selected destination until dispatch, transfer-queue priority uses end-to-end ERT, and learning finalizes one event-epoch semi-Markov transition per EA between consecutive actual route decisions of the same EA as defined in (59)–(60).


1) Training Procedure


Algorithm 1. Training procedure of ECHO
1: Initialize replay memory, queues, active-service records, task records, load histories, online and target Q-networks, LSTM parameters, and one open-interval record and reward accumulator for each EA.
2: for each training episode do
3: Reset the synchronized environment; clear every open interval; set each source-specific interval-reward accumulator to zero.
4: for each slot $t=1,\ldots,T$ do
5: Apply all boundary events produced at the end of slot $t-1$: admit completed transmissions to their stored destination queues, resolve completed computations, and add every resulting task reward from (55)--(58) to the accumulator of its source EA.
6: Receive the newest destination-load report. When a horizon-specific report is unavailable, obtain the required arrival-time workload estimate from the LSTM model in (28). Mark every nonempty outbound queue whose relevant destination estimate or information age changed for ERT reconstruction.
7: Remove waiting tasks for which $t>d_i$, record each as dropped exactly once, and add its reward to the corresponding source accumulator. Active non-preemptive operations are not removed.
8: Observe all EA arrival indicators $\{\chi_n(t)\}_{n\in\mathcal{E}}$.
9: if at least one task arrives then
10: For each arriving EA $n$, create the task descriptor and deadline using (2); evaluate local, horizontal, and vertical completion at the appropriate service and destination-arrival times; compute candidate ERT by (32); construct the valid, fallback, and effective sets by (42)--(45); build the candidate-ERT vector and canonical mask by (46), (53), and (54); and only then construct the complete pre-action state $\mathbf{x}_{n,m}$ and decentralized observation $\mathbf{s}_n(\tau_{n,m})$.
11: If EA $n$ has an open previous interval, finalize its preceding transition using the stored state and action, the accumulated source-$n$ interval reward, the fully constructed current observation and mask, and $\Delta_{n,m-1}=\tau_{n,m}-\tau_{n,m-1}$; append the transition to replay memory and reset only the accumulator of EA $n$.
12: Select the current action using the masked epsilon-greedy rule in (63).
13: Admit the task to the selected source queue; store destination metadata only for an offloaded task; store the pending record in (50), including its decision-time completion estimate, candidate ERT, selected lateness, mask, and risk indicator; and open the current interval with the current state, action, and epoch.
14: end if
15: Remove any newly invalidated waiting records. Rebuild the deterministic ERT order of every changed local queue and every changed or destination-estimate-affected outbound queue, then schedule each idle source resource. Newly admitted tasks may start in the same slot when the corresponding resource is idle.
16: Schedule destination processing according to the frozen source-indexed FIFO and capacity-sharing rule.
17: Execute exactly one slot of all active local, transmission, and destination services. Record operations that finish at the end of slot $t$ for application at the boundary of slot $t+1$.
18: Update observed loads, history matrices, supervised LSTM targets, and the next-slot prediction.
19: When replay memory contains at least one complete mini-batch, compute the masked event-epoch targets in (64)--(67), update the online Q-networks, and update the LSTM only with its separate prediction loss in (28).
20: Every target-copy period, copy the online Q-network parameters to the target networks.
21: end for
22: At terminal epoch $T+1$, first apply all events produced at the end of slot $T$, then mark every still-unresolved admitted task as dropped exactly once, add all terminal rewards to the appropriate source accumulators, construct the terminal observation and terminal flag, and finalize the last open interval of every EA with $\Delta=(T+1)-\tau_{n,m}$. The continuation term is zero at this terminal transition. Decay the exploration probability.
23: end for


2) Inference Procedure


Algorithm 2. Inference procedure of ECHO
1: Freeze the selected Q-network and LSTM checkpoints, normalization and clipping bounds, canonical action order, topology, and evaluation configuration.
2: At the beginning of slot $t$, apply every service-completion and transmission-arrival event recorded at the end of slot $t-1$ and resolve each resulting task outcome exactly once.
3: Receive the newest destination-load report or use the horizon-specific LSTM forecast when the report is stale or unavailable. Mark every nonempty outbound queue whose relevant destination estimate or information age changed for ERT reconstruction.
4: Remove expired waiting tasks while allowing active non-preemptive services to retain their resources until completion.
5: Observe all arrival indicators.
6: if at least one task arrives then
7: For each arriving EA $n$, create the task descriptor and deadline, estimate every physical route at the task's expected destination-arrival time, compute candidate ERT, construct the valid set and minimum-lateness fallback, and build the fixed canonical mask.
8: Construct the complete pre-action observation using the task fields, queue state, destination-load representation, candidate-ERT vector, and current mask.
9: Select the highest-valued unmasked action, admit the task to the corresponding source queue, store offload destination metadata only when offloading is selected, and retain the decision-time estimate, ERT, lateness, and risk fields for later outcome logging.
10: end if
11: Rebuild the deterministic ERT order of every changed local queue and every changed or destination-estimate-affected outbound queue; start service on idle source resources, including newly admitted tasks when possible.
12: Schedule destination processing according to the frozen source-indexed FIFO and capacity-sharing rule shared by all compared methods.
13: Execute exactly one slot of active computation and transmission, record end-of-slot completions for the next boundary, and update load history and the next-slot forecast.
14: Log route, decision-time estimate, information age, realized completion or drop, mask-calibration outcome, and runtime overhead for every resolved task without altering the frozen policy or figure values.


3) Method Summary


ECHO is fully specified by three interacting controls: end-to-end completion estimation, ERT-based source-queue scheduling, and masked distributed action selection. The local queue is prioritized by local completion slack, whereas the outbound-transfer queue is prioritized by end-to-end offloading slack that includes destination conditions. Every new task is evaluated over local, horizontal, and vertical routes, and no second destination decision is made after admission. Resolved tasks contribute to source-specific interval rewards, and one agent-specific event-epoch semi-Markov replay transition is finalized between consecutive actual route decisions of each EA, so delayed outcomes are included with the correct within-interval and sojourn discounts.
