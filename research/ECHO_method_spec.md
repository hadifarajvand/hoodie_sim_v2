---
source_document: "https://docs.google.com/document/d/17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE/edit"
source_document_id: "17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE"
source_tab_title: "روش پیشنهادی"
source_tab_id: "t.iav4589yyeo7"
source_revision_id: "ALtnJHyTLdhKaOnVqfvxB74eKtegK8Hrsx5l2yaYdk68tSHgf-QdYtM6nrsTZrwFDm3DbTUFkeWajyCFP0Eevns2d7r0_twwuuYjD4ZcMQ"
exported_at_utc: "2026-07-12T06:55:12.371510+00:00"
authority: "Primary ECHO method specification"
---

# روش پیشنهادی

**III. Proposed Effective Completion via Hybrid Offloading Framework (ECHO)**

**A. Framework Overview and Design Scope**

Cloud-edge continuum environments provide a distributed computing substrate for delay-sensitive computational tasks, where computation can be performed across local edge nodes, neighboring edge servers, and remote cloud resources. In this setting, hybrid computation offloading is required because relying only on local execution may overload edge nodes, while relying only on vertical cloud offloading may introduce excessive transmission and processing delay. Therefore, each arriving task must be assigned to an appropriate execution path, such as local computation, horizontal edge offloading, or vertical cloud offloading, according to the current task characteristics, queue status, communication condition, and available processing capacity. However, the offloading decision becomes more challenging when tasks are associated with strict completion bounds. A task that experiences excessive waiting time in a local or outbound-transfer queue, or is forwarded to a congested destination, may miss its allowed completion time and consequently be removed from successful execution. This makes the task drop ratio a critical performance indicator, particularly under dynamic traffic, limited edge resources, and fluctuating cloud-edge network conditions. Accordingly, this paper proposes Effective Completion via Hybrid Offloading (ECHO), a deadline-aware hybrid computation offloading method where the objective is not only to select a computationally feasible execution path, but also to guide the decision process toward timely task completion and reduced risk of task dropping. In ECHO, effective completion denotes the use of estimated end-to-end completion feasibility to guide source-queue scheduling and hybrid offloading decisions before the task outcome is observed.

Although hybrid offloading frameworks can reduce delay by distributing workloads across local, edge, and cloud resources, deadline handling must be integrated before task completion is evaluated. Existing distributed hybrid offloading agents can observe local task characteristics and forecasted load information to learn decisions that reduce execution latency and timeout-related task loss \[37\]. That learning foundation does not itself specify how each task's remaining completion slack should control queue order and route feasibility before action selection. If deadline information is only reflected after a task has waited, been transmitted, or failed to finish within its completion bound, the learning agent may still choose actions that are reasonable from an average-delay perspective but risky for tasks with tighter time constraints. The design rationale of the proposed framework is therefore to move deadline awareness earlier in the decision pipeline. Specifically, task urgency is introduced into queue scheduling, candidate evaluation, and reward feedback so that deadline-related risk is visible before the final execution outcome is observed.

The core idea of the proposed framework is to use Effective Remaining Time (ERT) as a unified temporal indicator for deadline-aware task handling. A raw deadline or timeout value alone is not sufficient for offloading decisions, because two tasks with similar deadlines may have different violation risks depending on their queue position, expected waiting time, transmission requirement, destination load, and processing demand. Therefore, the proposed framework interprets deadline urgency through the remaining feasible time after the expected execution conditions are considered. In this view, ERT acts as a bridge between task-level timing constraints and offloading-level decision making.

At the queue level, ERT indicates which pending task should be served earlier to avoid unnecessary deadline miss. At the candidate-selection level, it indicates whether a local, horizontal edge, or vertical cloud execution option is likely to complete the task within its allowable completion bound. This temporal signal does not replace the distributed DRL decision module; rather, it provides deadline-aware information that can be incorporated into queue ordering, feasible-action filtering, state representation, and reward feedback. As a result, the learning agent is guided not only by average delay and load-related observations, but also by the remaining time available for successful task completion.

The proposed framework consists of interdependent modeling and decision-making components that translate deadline awareness into the hybrid offloading process. The task and deadline model provides the timing basis of the framework by describing each arriving task through its arrival time, data size, processing demand, and allowable completion bound. Based on this timing information, the ERT estimation component evaluates how much effective time remains after the expected queueing, transmission, and processing conditions are considered. This temporal urgency is then used by the deadline-aware queue scheduling component to reorder pending tasks in the local and outbound-transfer queues when their risk of deadline violation differs. In parallel, the candidate-selection component evaluates local execution, horizontal edge offloading, and vertical cloud offloading according to their estimated completion behaviour and deadline feasibility. The distributed DRL decision module uses these observations together with local task information, queue status, and load-related indicators to select the final execution action at each edge agent. The reward feedback component closes the decision loop by penalizing realized duration, selection under predicted deadline infeasibility, and actual task dropping, thereby aligning learning with the objective of reducing deadline-related task loss under dynamic cloud-edge conditions.

The remainder of this section formalizes the proposed framework in a stepwise manner. First, the cloud-edge system model is defined to specify the computing nodes, communication layers, time-slotted operation, and hybrid execution paths. Then, the task model and deadline representation are introduced to describe task arrivals, task characteristics, and completion bounds. After that, the Effective Remaining Time model is formulated as the central deadline-aware timing indicator. The following subsections then explain how ERT is used for queue scheduling and candidate execution evaluation before the final offloading action is selected by the distributed DRL agent. Finally, the state space, action space, reward model, and algorithmic workflow are presented to show how the proposed deadline-aware mechanism is integrated into multi-agent distributed deep reinforcement learning. This organization separates conceptual framework design from simulation and performance evaluation, which are addressed in Section IV rather than in the proposed-method section.

**![][image1]**  
***Figure 1\. Overall ECHO architecture in the IoT–edge–cloud continuum, supporting local execution, horizontal edge offloading, and vertical cloud offloading.***

**B. Cloud–Edge System Model**

This section defines the cloud-edge system model used as the basis of the proposed deadline-aware hybrid offloading framework. The model specifies the computing entities, communication structure, task and deadline representation, offloading decision variables, and queueing components required before introducing Effective Remaining Time and the deadline-aware control logic. The main mathematical symbols introduced in this section are summarized after the architectural definitions to keep the subsequent formulations consistent and readable.

**ECHO considers a distributed cloud-edge architecture with local, horizontal-edge, and vertical-cloud execution paths \[37\]. Its distinctive control variables are estimated end-to-end completion time, ERT, queue urgency, route feasibility, and task-level delayed outcomes. Each computational task is non-divisible and is assigned to one execution path.**

**At the moment a task arrives, its descriptor is assumed to be available to the source EA. This descriptor includes the input size, the processing density, and the relative timeout of the task. The model does not assume knowledge of future task arrivals. Instead, each EA makes its decision from its current local observation, the status of its own queues, and compact load information obtained from the monitoring layer. The system is represented in synchronized time slots with a fixed slot length $\\Delta$, so waiting, transmission, and processing durations are expressed as integer numbers of slots. This slot-based representation makes deadline satisfaction directly comparable with estimated completion time.**

**Horizontal offloading is allowed only between connected edge agents, while vertical offloading to the cloud remains available as a high-capacity but potentially higher-latency execution path. The queue waiting times and candidate completion times used in the proposed method are estimates computed at the decision time. These estimates may change as the workload evolves, but they provide the temporal basis required for ERT calculation, deadline-aware queue scheduling, and candidate feasibility checking.**

**Under these assumptions, the physical paths and queue locations remain fixed during operation. ECHO changes the decision and service logic by evaluating deadline, end-to-end completion time, and ERT before execution, so urgency affects both queue service and route selection before a task becomes late or is dropped.**

**1\) System Architecture**  
As shown in Fig. 1, ECHO operates over a three-layer IoT-edge-cloud continuum consisting of an IoT layer, an edge layer, and a cloud layer \[37\]. The IoT layer represents multiple task-generating service areas, while the edge layer contains $N$ Edge Agents (EAs) that provide near-user computational capacity. A remote cloud node is also available as a high-capacity computing resource for tasks that cannot be efficiently processed at the edge. Let $\\mathcal{N}=\\{1,2,\\ldots,N,N+1\\}$ denote the set of all computing nodes, where $N+1$ represents the cloud node. The set of edge agents is denoted by $\\mathcal{E}=\\mathcal{N}\\setminus\\{N+1\\}=\\{1,2,\\ldots,N\\}$. Each EA $n\\in\\mathcal{E}$ is associated with a corresponding IoT service area and is able to participate in both local task execution and cooperative offloading.

To support distributed monitoring and information exchange, the edge layer is assumed to include a set of Edge Controllers (ECs), denoted by $\\mathcal{M}=\\{1,2,\\ldots,M\\}$. An EC may monitor a single EA or a cluster of EAs, depending on the deployment structure. The ECs collect compact status information such as queue load and node-level activity, and this information can be shared with the corresponding EAs for load-aware decision making. This monitoring role does not imply centralized control of the offloading policy; instead, each EA remains responsible for its own local decision process while using locally observed and shared system information.

The system is observed over a finite episode composed of time slots $\\mathcal{T}=\\{1,2,\\ldots,T\\}$, where each time slot has duration $\\Delta$ seconds. At the beginning of a time slot, an EA may receive a new computational task from its associated IoT area and observe the current queue and load conditions available to it. Communication from IoT devices to their area-specific base station is performed through wireless links, while the connection from the base station to the corresponding EA is assumed to rely on a wired fronthaul link. Horizontal offloading is enabled through edge-to-edge communication among EAs, and vertical offloading is enabled through the connection between EAs and the cloud node. This architecture provides the computational substrate for local execution, horizontal edge offloading, and vertical cloud offloading, which are formally represented in the hybrid offloading decision model.  
Table 1 summarizes the mathematical notation used throughout ECHO.

**Table 1\. Mathematical notation of the ECHO framework.**

| Notation | Definition |
| :---- | :---- |
| $N$ | Number of Edge Agents (EAs). |
| $M$ | Number of Edge Controllers (ECs). |
| $T$ | Number of time slots in one episode. |
| $n$ | Index of an Edge Agent or source node. |
| $k$ | Index of an execution destination. |
| $i$ | Index of a computational task. |
| $h$ | Index of another task, typically a predecessor in a queue. |
| $j$ | Index of a position in the fixed canonical action set. |
| $t$ | Current time-slot index. |
| $\\mathcal{N}$ | Set of all computing nodes, including the cloud node. |
| $\\mathcal{E}$ | Set of Edge Agents. |
| $\\mathcal{M}$ | Set of Edge Controllers. |
| $\\mathcal{T}$ | Set of time slots in an episode. |
| $\\mathcal{H}$ | Set of admissible task input sizes. |
| $\\Delta$ | Duration of one time slot in seconds. |
| $\\mathbf{G}$ | Edge-layer connectivity matrix. |
| $G(n,k)$ | Connectivity indicator between EAs $n$ and $k$. |
| $\\chi\_n(t)$ | Binary indicator that a new task arrives at EA $n$ in slot $t$. |
| $\\xi\_i$ | Computational task indexed by $i$. |
| $s\_i$ | Source EA of task $\\xi\_i$. |
| $t\_i^a$ | Arrival and offloading-decision slot of task $\\xi\_i$. |
| $t\_i^r$ | Resolution slot at which task $\\xi\_i$ completes or is recorded as dropped. |
| $t\_i^+$ | First valid decision slot after task $\\xi\_i$ is resolved, or the terminal decision state. |
| $b\_i$ | Input data size of task $\\xi\_i$ in bits. |
| $b\_i^{\\mathrm{rem}}(t)$ | Remaining unprocessed bits of task $\\xi\_i$ at slot $t$. |
| $\\nu\_i$ | Processing density of task $\\xi\_i$ in CPU cycles per bit. |
| $\\delta\_i$ | Relative timeout of task $\\xi\_i$ in slots. |
| $d\_i$ | Absolute completion deadline of task $\\xi\_i$. |
| $\\alpha$ | Generic execution or offloading action. |
| $\\alpha\_n^L$ | Local-execution action at EA $n$. |
| $\\alpha\_{n,k}^H$ | Horizontal-offloading action from EA $n$ to connected EA $k$. |
| $\\alpha\_n^V$ | Vertical-offloading action from EA $n$ to the cloud. |
| $\\alpha\_i$ | Action selected for task $\\xi\_i$. |
| $\\mathcal{A}\_n(t)$ | Physically available action set of EA $n$ at slot $t$. |
| $\\bar{\\mathcal{A}}\_n$ | Fixed canonical action-output set of EA $n$. |
| $\\bar{\\alpha}\_{n,j}$ | Action stored at canonical output position $j$ of EA $n$. |
| $\\kappa(\\alpha)$ | Mapping from action $\\alpha$ to its execution destination. |
| $k\_i$ | Destination stored with offloaded task $\\xi\_i$. |
| $\\mathbf{g}\_i$ | Stored dispatch metadata of task $\\xi\_i$. |
| $\\mathcal{Q}\_i^{\\mathrm{src}}(t)$ | Source-side queue selected for task $\\xi\_i$ at slot $t$. |
| $\\mathcal{Q}\_n^L(t)$ | Local waiting queue of EA $n$. |
| $\\mathcal{Q}\_n^X(t)$ | Outbound-transfer waiting queue of EA $n$. |
| $\\mathcal{Q}\_{n\\rightarrow k}^D(t)$ | Destination queue at node $k$ for tasks received from source EA $n$. |
| $z\_{i,k}^D(t)$ | Indicator that transmission of task $\\xi\_i$ to destination $k$ finished before slot $t$. |
| $U\_k^D(t)$ | Number of tasks admitted to destination queues of node $k$ at slot $t$. |
| $q\_n^L(t)$ | Occupancy of the local waiting queue at EA $n$. |
| $q\_n^X(t)$ | Occupancy of the outbound-transfer waiting queue at EA $n$. |
| $\\varrho\_n^L(t)$ | Residual service time of the active local task at EA $n$. |
| $\\varrho\_n^X(t)$ | Residual transmission time of the active outbound task at EA $n$. |
| $\\Psi\_n^L(t)$ | Remaining local-side workload at EA $n$. |
| $\\Psi\_n^X(t)$ | Remaining outbound-transfer workload at EA $n$. |
| $f\_n^L$ | Local processing capacity of EA $n$. |
| $f\_k^{EA}$ | Processing capacity of edge destination $k$. |
| $f^C$ | Processing capacity of the cloud. |
| $f\_k^D$ | Unified destination-processing capacity of node $k$. |
| $\\bar f\_{n,k}^D(t)$ | Estimated effective destination capacity assigned to source queue $n\\rightarrow k$. |
| $R\_H$ | Horizontal edge-to-edge transmission rate. |
| $R\_V$ | Vertical edge-to-cloud transmission rate. |
| $R\_{n,k}$ | Transmission rate from source node $n$ to destination $k$. |
| $\\tau\_i^L$ | Local processing duration of task $\\xi\_i$. |
| $\\tau\_{i,k}^X$ | Transmission duration of task $\\xi\_i$ to destination $k$. |
| $\\tau\_{i,k}^D(t)$ | Estimated destination-processing duration of task $\\xi\_i$ at node $k$. |
| $\\mathcal{H}\_i^L(t)$ | Provisional predecessor set of task $\\xi\_i$ in the local queue. |
| $\\mathcal{H}\_i^X(t)$ | Provisional predecessor set of task $\\xi\_i$ in the outbound-transfer queue. |
| $\\widehat W\_i^L(t)$ | Estimated local-queue waiting time of task $\\xi\_i$. |
| $\\widehat W\_i^X(t)$ | Estimated outbound-transfer waiting time of task $\\xi\_i$. |
| $\\widehat T\_i^L(t)$ | Estimated local completion slot of task $\\xi\_i$. |
| $\\widehat T\_{i,k}^X(t)$ | Estimated completion slot of the source-side transmission stage to node $k$. |
| $\\widehat t\_{i,k}^D(t)$ | Estimated slot at which task $\\xi\_i$ reaches destination queue $k$. |
| $\\Omega\_{n\\rightarrow k}(t)$ | Actual remaining cycle workload in destination queue $n\\rightarrow k$. |
| $\\widehat\\Omega\_{n\\rightarrow k}(t)$ | Observed or predicted remaining cycle workload used for estimation. |
| $\\mathcal{J}\_k(t)$ | Set of active source-indexed destination queues at node $k$. |
| $p\_k(t)$ | Number of active source-indexed destination queues at node $k$. |
| $\\bar p\_{n,k}(t)$ | Adjusted active-queue count after hypothetically admitting source queue $n\\rightarrow k$. |
| $\\widehat W\_{i,k}^D(t)$ | Estimated destination-queue waiting time of task $\\xi\_i$ at node $k$. |
| $\\widehat T\_{i,k}^O(t)$ | Estimated end-to-end completion slot for offloading task $\\xi\_i$ to node $k$. |
| $\\widehat T\_i(\\alpha,t)$ | Unified estimated completion slot of task $\\xi\_i$ under action $\\alpha$. |
| $\\mathbf{o}\_n(t)$ | Observed destination-load vector available to EA $n$. |
| $\\mathbf{H}\_n(t)$ | Historical load matrix maintained by EA $n$. |
| $W$ | Length of the load-history lookback window. |
| $F\_\\psi$ | LSTM-based load encoder with parameters $\\psi$. |
| $\\psi$ | Parameter set of the recurrent load encoder. |
| $\\mathbf{z}\_n(t)$ | Fixed-dimensional recurrent load embedding of EA $n$. |
| $\\widehat{\\mathbf{H}}\_n(t+1)$ | Predicted next-slot load representation. |
| $\\mathsf{ERT}\_i^L(t)$ | Queue-level Effective Remaining Time of task $\\xi\_i$ for local execution. |
| $\\mathsf{ERT}\_i^X(t)$ | End-to-end queue-level Effective Remaining Time of task $\\xi\_i$ in the transfer queue. |
| $\\mathsf{ERT}\_i^C(\\alpha,t)$ | Candidate-level Effective Remaining Time under action $\\alpha$. |
| $\\mathcal{F}\_n^L(t)$ | Predicted-feasible task set in the local queue of EA $n$. |
| $\\mathcal{F}\_n^X(t)$ | Predicted-feasible task set in the outbound-transfer queue of EA $n$. |
| $\\xi\_n^{L,\*}(t)$ | Task selected next for local processing at EA $n$. |
| $\\xi\_n^{X,\*}(t)$ | Task selected next for outbound transmission at EA $n$. |
| $\\ell\_i^L(t)$ | Estimated local queue-level lateness of task $\\xi\_i$. |
| $\\ell\_i^X(t)$ | Estimated end-to-end transfer queue-level lateness of task $\\xi\_i$. |
| $\\mathcal{V}\_i(t)$ | Set of physically available actions predicted to meet the deadline of task $\\xi\_i$. |
| $\\Lambda\_i(\\alpha,t)$ | Predicted lateness of candidate action $\\alpha$ for task $\\xi\_i$. |
| $\\alpha\_i^{fb}(t)$ | Minimum-lateness fallback action for task $\\xi\_i$. |
| $\\mathcal{U}\_i(t)$ | Effective action set used by the learning policy. |
| $\\mu\_{n,j}(t)$ | Binary availability indicator for canonical action position $j$. |
| $\\boldsymbol{\\mu}\_n(t)$ | Fixed-dimensional physical-and-deadline action mask of EA $n$. |
| $\\mathbf{s}\_n(t)$ | Normalized DRL state observed by EA $n$. |
| $\\tilde{x}$ | Normalized form of numerical quantity $x$. |
| $\\mathsf{ERT}\_{n,\\min}^L(t)$ | Minimum local-queue ERT summary at EA $n$. |
| $\\mathsf{ERT}\_{n,\\min}^X(t)$ | Minimum outbound-transfer-queue ERT summary at EA $n$. |
| $\\mathbf{e}\_i^C(t)$ | Fixed-dimensional vector of candidate-level ERT values. |
| $T\_i^{\\mathrm{sys}}$ | Realized system duration of task $\\xi\_i$. |
| $I\_i^R$ | Decision-time indicator that every physical candidate is predicted infeasible. |
| $I\_i^D$ | Realized indicator that task $\\xi\_i$ fails to achieve deadline-satisfied completion. |
| $\\lambda\_R$ | Penalty weight for predicted deadline risk. |
| $\\lambda\_D$ | Penalty weight for realized task dropping. |
| $r\_i$ | Task-level reward associated with task $\\xi\_i$. |
| $\\mathcal{P}\_n$ | Pending-decision buffer of EA $n$. |
| $\\mathbf{p}\_i$ | Pending record maintained for task $\\xi\_i$. |
| $\\mathcal{R}\_n$ | Replay memory of EA $n$. |
| $\\zeta\_i$ | Finalized task-level semi-Markov transition. |
| $\\Delta\_i$ | Decision-to-decision duration associated with transition $\\zeta\_i$. |
| $\\pi\_n$ | Decision policy of EA $n$. |
| $\\pi\_n^\*$ | Optimal policy sought for EA $n$. |
| $\\gamma$ | Discount factor. |
| $Q\_n(\\mathbf{s},\\alpha;\\theta\_n)$ | Online action-value function of EA $n$. |
| $Q\_n^-(\\mathbf{s},\\alpha;\\theta\_n^-)$ | Target action-value function of EA $n$. |
| $\\theta\_n$ | Parameter vector of the online Q-network at EA $n$. |
| $\\theta\_n^-$ | Parameter vector of the target Q-network at EA $n$. |
| $V\_n(\\mathbf{s};\\theta\_n)$ | Dueling-network state-value function. |
| $A\_n(\\mathbf{s},\\alpha;\\theta\_n)$ | Dueling-network action-advantage function. |
| $Q\_n^\\mu(\\mathbf{s},\\alpha;t)$ | Action-value function after applying the current mask. |
| $\\epsilon$ | Exploration probability in the masked epsilon-greedy policy. |
| $\\alpha\_i^+$ | Masked next action selected for the Double-DQL target. |
| $y\_i$ | Double-DQL training target for task transition $i$. |
| $\\widehat y\_i$ | Online Q-network prediction for task transition $i$. |
| $\\mathcal{L}\_n(\\theta\_n)$ | Mini-batch learning loss of EA $n$. |
| $B$ | Mini-batch of replayed task transitions. |
| $|B|$ | Number of transitions in mini-batch $B$. |
| $N\_{\\mathrm{copy}}$ | Target-network copy period. |
| $\\alpha\_{lr}$ | Learning rate. |
| $\\mathbb{I}\[\\cdot\]$ | Indicator function, equal to one when its condition is true and zero otherwise. |
| $\\mathbb{E}\_{\\pi\_n}\[\\cdot\]$ | Expectation under policy $\\pi\_n$. |
| $\\lceil x\\rceil$ | Smallest integer greater than or equal to $x$. |
| $|\\mathcal{S}|$ | Cardinality of set $\\mathcal{S}$. |
| $\\emptyset$ | Empty set. |
| $-\\infty$ | Value assigned to masked actions so they cannot be selected. |

**2\) Task Characteristics and Deadline Representation**  
At the beginning of each time slot $t\\in\\mathcal{T}$, each EA $n\\in\\mathcal{E}$ may receive a new computational task from its associated IoT area. The task-arrival process is represented by the binary variable $\\chi\_n(t)$ as follows:

\\begin{equation}  
\\chi\_n(t)=  
\\begin{cases}  
1, & \\text{if a new task arrives in EA } n \\text{ at time slot } t,\\\\  
0, & \\text{otherwise.}  
\\end{cases}  
\\tag{1}  
\\end{equation}

When $\\chi\_n(t)=1$, the arrived task is denoted by $\\xi\_i$. The task is characterized by its input data size $b\_i$, processing density $\\nu\_i$, and timeout index $\\delta\_i$. The task size $b\_i$ is measured in bits and is drawn from the task-size set $\\mathcal{H}$, while $\\nu\_i$ represents the number of CPU cycles required to process one bit of the task. The timeout index $\\delta\_i$ indicates the maximum number of time slots within which the task should be completed after its arrival.

ECHO converts the relative timeout into an absolute completion deadline so that the same timing boundary can be used in completion estimation, queue scheduling, and route selection. Since task $\\xi\_i$ arrives at the beginning of time slot $t$, its absolute deadline is defined as

\\begin{equation}  
d\_i=t+\\delta\_i-1.  
\\tag{2}  
\\end{equation}

Accordingly, under the absolute deadline in (2), task $\\xi\_i$ is deadline-satisfied only if its realized completion slot does not exceed $d\_i$. This explicit deadline representation is later used to define Effective Remaining Time, deadline-aware queue ordering, and deadline-feasible offloading candidate selection.

The derivation of the absolute deadline follows from the slot-based interpretation of the timeout. If a task arrives at the beginning of slot $t$ and its timeout is $\\delta\_i$ slots, then the task can use the slots $t,t+1,\\ldots,t+\\delta\_i-1$. Hence, the last acceptable completion slot is $t+\\delta\_i-1$. This definition avoids an off-by-one ambiguity and makes the deadline condition directly comparable with completion-time estimates expressed in time-slot indexes.

The task lifecycle is applied consistently to all queues. At the beginning of a service decision, a waiting task with current slot greater than its absolute deadline is removed and recorded as dropped. A task that has already started computation or transmission is not preempted; the active operation retains the resource until it finishes, but its result is recorded as dropped if the realized completion slot exceeds the deadline. This rule preserves non-preemptive resource occupancy while ensuring that only deadline-satisfied outcomes are counted as successful.

**3\) Hybrid Offloading Decision Model**  
**When a new task $\\xi\_i$ arrives at EA $n$, ECHO selects one direct action from the local, horizontal-edge, and vertical-cloud candidates. The selected action determines both the source queue and, when offloading is chosen, the destination stored with the task. The dispatch block shown in Fig. 2 later applies that stored destination; it does not perform a second destination optimization.**

**The physical candidate action set is**

**\\begin{equation}**  
**\\mathcal{A}\_n(t)=\\{\\alpha\_n^L\\}\\cup\\{\\alpha\_{n,k}^H\\mid k\\in\\mathcal{E}\\setminus\\{n\\},\\,G(n,k)=1\\}\\cup\\{\\alpha\_n^V\\}.**  
**\\tag{3}**  
**\\end{equation}**

**The execution destination associated with action $\\alpha$ is**

**\\begin{equation}**  
**\\kappa(\\alpha)=\\begin{cases}n, & \\alpha=\\alpha\_n^L,\\\\k, & \\alpha=\\alpha\_{n,k}^H,\\\\N+1, & \\alpha=\\alpha\_n^V.\\end{cases}**  
**\\tag{4}**  
**\\end{equation}**

**The selected source-side queue is therefore**

**\\begin{equation}**  
**\\mathcal{Q}\_i^{src}(t)=\\begin{cases}\\mathcal{Q}\_{s\_i}^L(t), & \\kappa(\\alpha\_i)=s\_i,\\\\\\mathcal{Q}\_{s\_i}^X(t), & \\kappa(\\alpha\_i)\\neq s\_i.\\end{cases}**  
**\\tag{5}**  
**\\end{equation}**

**For an offloaded task, the stored destination metadata is**

**\\begin{equation}**  
**k\_i=\\kappa(\\alpha\_i),\\qquad k\_i\\in\\mathcal{N}\\setminus\\{s\_i\\}.**  
**\\tag{6}**  
**\\end{equation}**

**Selection of an offloading action does not create an immediate arrival at the destination queue. A task enters $\\mathcal{Q}\_{n\\rightarrow k}^D(t)$ only after its source-side transmission finishes. Let**

**\\begin{equation}**  
**z\_{i,k}^D(t)=\\begin{cases}1, & \\text{if transmission of task }\\xi\_i\\text{ to node }k\\text{ finishes at }t-1,\\\\0, & \\text{otherwise}.\\end{cases}**  
**\\tag{7}**  
**\\end{equation}**

**The number of tasks that actually enter destination queues of node $k$ at slot $t$ is**

**\\begin{equation}**  
**U\_k^D(t)=\\sum\_{i:s\_i\\neq k}z\_{i,k}^D(t).**  
**\\tag{8}**  
**\\end{equation}**

**For an edge destination, the source index excludes the destination itself; for the cloud, all EAs are included. Each received task is placed in the destination queue indexed by its source EA. This timing relation distinguishes the decision slot from the later transmission-completion slot.**

**The direct action is selected once at task arrival. ECHO does not add a new physical route; it changes how the existing local, horizontal, and vertical routes are evaluated through end-to-end completion estimation, ERT, and deadline-aware masking.**

**4\) Local Queue Model**  
Each EA maintains a local waiting queue and a local processor, following the distributed queue architecture in \[37\]. ECHO applies non-preemptive ERT-based service selection whenever the local processor becomes idle. Every queue record stores the task identifier, source, arrival slot, size, processing density, deadline, remaining workload, and the information required to recompute completion estimates.

Let $\\mathcal{Q}\_n^L(t)$ contain the waiting local tasks, excluding any task currently in service. The local processing duration of task $\\xi\_i$ is

\\begin{equation}  
\\tau\_i^L=\\left\\lceil\\frac{b\_i\\nu\_i}{f\_n^L\\Delta}\\right\\rceil.  
\\tag{9}  
\\end{equation}

Let $\\varrho\_n^L(t)$ denote the residual service time of the task currently running on the local processor, with $\\varrho\_n^L(t)=0$ when the CPU is idle. If $\\mathcal{H}\_i^L(t)$ denotes the waiting tasks placed before $\\xi\_i$ under the current hypothetical ERT order, the estimated waiting time is

\\begin{equation}  
\\widehat W\_i^L(t)=\\varrho\_n^L(t)+\\sum\_{\\xi\_h\\in\\mathcal{H}\_i^L(t)}\\tau\_h^L,  
\\tag{10}  
\\end{equation}

and the estimated local completion slot is

\\begin{equation}  
\\widehat T\_i^L(t)=t+\\widehat W\_i^L(t)+\\tau\_i^L-1.  
\\tag{11}  
\\end{equation}

For a newly arrived task, ECHO evaluates a hypothetical insertion into the local queue, computes the resulting order and completion slot, and uses this value as the local candidate completion estimate. Once local execution starts, it is not preempted by a newly arriving task. Waiting tasks can be reordered only at a later service epoch when the CPU is idle.

The deadline and completion records remain separate. ECHO does not truncate $\\widehat T\_i^L(t)$ at $d\_i$, because truncation would hide predicted lateness and underestimate resource occupancy. A task is successfully completed only when its realized completion slot does not exceed its absolute deadline. If its deadline expires before successful completion, it is handled according to the task-lifecycle rule: a waiting task is removed, whereas an active non-preemptive operation retains the resource until completion and its result is recorded as dropped.

Whenever a task is admitted, completed, removed, or selected for service, the waiting-task order and completion estimates are updated. This local-queue model supplies the local completion value used in queue-level ERT and in the local candidate comparison.

**5\) Outbound-Transfer Queue Model**  
The outbound-transfer queue stores tasks whose ECHO action selects horizontal or vertical offloading. When such an action is selected, destination $k\_i=\\kappa(\\alpha\_i)$ is stored with the task together with its source, arrival slot, size, processing density, and deadline. The dispatch block in Fig. 2 applies this stored destination when the task enters transmission; it does not perform a second destination decision.

Let $\\mathcal{Q}\_n^X(t)$ contain the waiting outbound-transfer tasks, excluding any transmission currently in service. Transmission is non-preemptive. The rate associated with the stored destination is

\\begin{equation}  
R\_{s\_i,k\_i}=\\begin{cases}R\_H, & k\_i\\in\\mathcal{E}\\setminus\\{s\_i\\},\\\\ R\_V, & k\_i=N+1.\\end{cases}  
\\tag{12}  
\\end{equation}

A horizontal destination must also satisfy $G(s\_i,k\_i)=1$. The transmission duration of task $\\xi\_i$ is

\\begin{equation}  
\\tau\_{i,k\_i}^X=\\left\\lceil\\frac{b\_i}{R\_{s\_i,k\_i}\\Delta}\\right\\rceil.  
\\tag{13}  
\\end{equation}

Let $\\varrho\_n^X(t)$ be the residual transmission time of the task currently in service, or zero if the transfer resource is idle. If $\\mathcal{H}\_i^X(t)$ is the set of waiting tasks placed before $\\xi\_i$ under the current hypothetical ERT order, its estimated waiting and source-stage completion times are

\\begin{equation}  
\\widehat W\_i^X(t)=\\varrho\_n^X(t)+\\sum\_{\\xi\_h\\in\\mathcal{H}\_i^X(t)}\\tau\_{h,k\_h}^X,  
\\tag{14}  
\\end{equation}

\\begin{equation}  
\\widehat T\_{i,k\_i}^X(t)=t+\\widehat W\_i^X(t)+\\tau\_{i,k\_i}^X-1.  
\\tag{15}  
\\end{equation}

The estimated arrival slot at the stored destination queue is

\\begin{equation}  
\\widehat t\_{i,k\_i}^D(t)=\\widehat T\_{i,k\_i}^X(t)+1.  
\\tag{16}  
\\end{equation}

The completion estimate is not truncated at the deadline. Keeping the complete value is necessary for ERT and lateness calculation and for estimating when the transmission resource becomes available. A task that expires before successful transmission or completion is handled according to the task-lifecycle rule and recorded as dropped; an active non-preemptive transmission retains the resource until it finishes, and the deadline remains separate from estimated and realized completion time.

When an offloading candidate is evaluated, its destination determines the transmission duration and the task is inserted hypothetically into the outbound-transfer queue to estimate its provisional position, waiting time, and source-stage completion. After the action is chosen, that destination remains attached to the task. Whenever queue membership or active service changes, the hypothetical waiting and completion estimates of waiting tasks are recalculated before the next non-preemptive service decision.

**6\) Destination Queue and Load Model**  
Destination queues use the source-indexed organization in \[37\] and represent processing workloads received from other EAs. Each destination node $k$ maintains a source-indexed queue $\\mathcal{Q}\_{n\\rightarrow k}^D(t)$ for tasks originating from EA $n$. This separation prevents collisions between simultaneous arrivals from different sources. A source EA does not reorder a destination queue. FIFO order is retained within each source-indexed destination queue, while the destination processor shares its processing capacity among active queues according to the architecture in \[37\]. These queues provide workload information for candidate completion estimation.

A queue is active when it contains unfinished computational workload. To avoid a notation collision with the action set, the active destination-queue set and its cardinality are denoted by

\\begin{equation}  
\\mathcal{J}\_k(t)=\\begin{cases}\\left\\{n\\in\\mathcal{E}\\setminus\\{k\\}\\mid \\Omega\_{n\\rightarrow k}(t)\>0\\right\\}, & k\\in\\mathcal{E},\\\\\\left\\{n\\in\\mathcal{E}\\mid \\Omega\_{n\\rightarrow k}(t)\>0\\right\\}, & k=N+1.\\end{cases}  
\\tag{17}  
\\end{equation}

\\begin{equation}  
p\_k(t)=\\left|\\mathcal{J}\_k(t)\\right|.  
\\tag{18}  
\\end{equation}

Because queued tasks may have different processing densities, destination load is represented in remaining CPU cycles rather than only in bits. Let $b\_h^{rem}(t)$ be the remaining bits of queued task $\\xi\_h$ and $\\nu\_h$ its processing density. The remaining workload in the source-indexed destination queue is

\\begin{equation}  
\\Omega\_{n\\rightarrow k}(t)=\\sum\_{\\xi\_h\\in \\mathcal{Q}\_{n\\rightarrow k}^D(t)}b\_h^{rem}(t)\\nu\_h.  
\\tag{19}  
\\end{equation}

When candidate $n\\rightarrow k$ is evaluated, admission of the new task may activate a previously inactive source queue. The adjusted number of active queues is

\\begin{equation}  
\\bar p\_{n,k}(t)=\\max\\left\\{1,p\_k(t)+\\mathbb{I}\\left\[n\\notin\\mathcal{J}\_k(t)\\right\]\\right\\}.  
\\tag{20}  
\\end{equation}

Let the total destination processing capacity of node $k$ be

\\begin{equation}  
f\_k^D=\\begin{cases}f\_k^{EA}, & k\\in\\mathcal{E},\\\\ f^C, & k=N+1.\\end{cases}  
\\tag{21}  
\\end{equation}

The effective capacity assigned to the candidate source queue is estimated as

\\begin{equation}  
\\bar f\_{n,k}^D(t)=\\frac{f\_k^D}{\\bar p\_{n,k}(t)}.  
\\tag{22}  
\\end{equation}

This definition is always finite, including when the destination is initially idle. Let $\\widehat\\Omega\_{n\\rightarrow k}(t)$ denote the workload available to the source EA for estimation. It equals the latest observed cycle workload when a fresh update is available; otherwise, it is obtained from the LSTM load estimate. The destination-side waiting time and processing duration of the candidate task are

\\begin{equation}  
\\widehat W\_{i,k}^D(t)=\\left\\lceil\\frac{\\widehat\\Omega\_{s\_i\\rightarrow k}(t)}{\\bar f\_{s\_i,k}^D(t)\\Delta}\\right\\rceil,  
\\tag{23}  
\\end{equation}

\\begin{equation}  
\\tau\_{i,k}^D(t)=\\left\\lceil\\frac{b\_i\\nu\_i}{\\bar f\_{s\_i,k}^D(t)\\Delta}\\right\\rceil.  
\\tag{24}  
\\end{equation}

If task $\\xi\_i$ is expected to reach destination queue $k$ at $\\widehat t\_{i,k}^D(t)$, its estimated end-to-end offloading completion slot is

\\begin{equation}  
\\widehat T\_{i,k}^O(t)=\\widehat t\_{i,k}^D(t)+\\widehat W\_{i,k}^D(t)+\\tau\_{i,k}^D(t)-1.  
\\tag{25}  
\\end{equation}

This model includes the work already waiting in the appropriate source-indexed destination queue and the capacity reduction caused by concurrent active destination queues. The estimate is used for horizontal and vertical candidate ERT. Actual task arrival at the destination queue occurs only after its source-side transmission completes; selecting an offloading action does not place the task immediately in the destination queue.

Destination workload information may be stale because the method remains distributed. ECHO therefore uses the newest received status when available and the LSTM estimate otherwise. This allows destination congestion to influence candidate feasibility without giving the source EA control over destination scheduling.

7\) Historical Load and Load Estimation  
*Historical load captures the recent destination-side workload observed by an EA without requiring global knowledge of future task arrivals. Consistent with the destination-queue model, each destination entry includes the remaining computational workload in CPU cycles and the number of active destination queues. The observed load vector available to EA $n$ is*

*\\begin{equation}*  
*\\mathbf{o}\_n(t)=\\left\[\\widehat\\Omega\_{n\\rightarrow k}(t),p\_k(t)\\right\]\_{k\\in\\mathcal{N}\\setminus\\{n\\}}.*  
*\\tag{26}*  
*\\end{equation}*

*Using a lookback window of length $W$, the historical matrix is*

*\\begin{equation}*  
*\\mathbf{H}\_n(t)=\\left\[\\mathbf{o}\_n(t-W+1),\\ldots,\\mathbf{o}\_n(t)\\right\].*  
*\\tag{27}*  
*\\end{equation}*

*The recurrent load encoder follows the distributed forecasting design in \[37\]. The encoder*

*\\begin{equation}*  
*\\mathbf{z}\_n(t)=F\_\\psi\\left(\\mathbf{H}\_n(t)\\right)*  
*\\tag{28}*  
*\\end{equation}*

*produces a fixed-dimensional representation for the DRL state and a next-slot workload estimate $\\widehat{\\mathbf{H}}\_n(t+1)$ for candidate completion estimation. When a fresh EC-provisioned workload update is available, the current observation is used. If an update is delayed or unavailable, the latest history and the LSTM estimate provide $\\widehat\\Omega\_{n\\rightarrow k}(t)$ and the expected active-queue information.*

*The LSTM output is connected directly to two ECHO functions: $\\mathbf{z}\_n(t)$ is included in the agent state, and its decoded workload estimate is used in destination waiting-time calculation. This keeps stale-load handling explicit while preserving decentralized operation.*

*![][image2]*  
*Figure 2\. Internal structure of an ECHO-enabled Edge Agent, including local, outbound-transfer, and destination queues, end-to-end completion estimation, ERT-based scheduling, and masked hybrid decisions.*

![][image3]  
Figure 3\. Workflow of the proposed ECHO method, from task arrival and deadline-aware route evaluation to ERT-based scheduling, execution, and delayed learning update.

Figure 3 summarizes the operational workflow of ECHO, beginning with task arrival, deadline construction, and completion-time estimation for local, horizontal-edge, and vertical-cloud routes, and continuing through candidate-level ERT evaluation, queue scheduling, execution, and learning update. At each decision epoch, ECHO first checks whether any deadline-feasible route exists; when one or more valid routes are available, the learned policy selects among them through the action mask, whereas an empty valid set invokes the minimum-lateness fallback before the task outcome is recorded for reward and replay generation.

**C. Effective Remaining Time Model**

The central timing variable of the proposed framework is Effective Remaining Time (ERT). A raw timeout value only specifies the maximum allowed completion bound of a task, but it does not show how much feasible time remains after queueing, transmission, destination load, and processing requirements are considered. Therefore, ERT is introduced to convert deadline information into an operational urgency indicator that can be used before the task is completed or dropped.

Two complementary forms of ERT are defined. Queue-level ERT is used to rank pending tasks inside a source-side queue, while candidate-level ERT is used to evaluate whether a local, horizontal edge, or vertical cloud execution path is feasible before the final offloading action is selected.

**1\) Queue-Level ERT**  
Queue-level ERT measures the urgency of a task waiting in a source-side local or outbound-transfer queue. Local ERT uses the local completion estimate, whereas transfer ERT uses the end-to-end offloading estimate that includes source waiting, transmission, destination waiting, and destination processing.

For a task $\\xi\_i$ waiting in the local queue, queue-level ERT is

\\begin{equation}  
\\mathsf{ERT}\_i^L(t)=d\_i-\\widehat T\_i^L(t).  
\\tag{29}  
\\end{equation}

For a task in the outbound-transfer queue with stored destination $k\_i=\\kappa(\\alpha\_i)$, end-to-end queue ERT is defined in (30).

Unlike a source-stage transmission slack, the transfer ERT in (30) is end-to-end:

\\begin{equation}  
\\mathsf{ERT}\_i^X(t)=d\_i-\\widehat T\_{i,k\_i}^O(t).  
\\tag{30}  
\\end{equation}

A positive value indicates predicted completion before the deadline, zero denotes the feasibility boundary, and a negative value indicates predicted lateness. A negative estimate is not the same as actual expiration; expiration depends on the current slot and the realized task lifecycle.

The provisional order is constructed iteratively. Starting after the residual active service, ECHO evaluates each unscheduled task in the next position, selects the smallest non-negative ERT or the minimum-lateness task when none is feasible, appends it to the provisional order, and repeats. Completion estimates and ERT values are recomputed whenever queue membership or service state changes.

**2\) Candidate-Level ERT**  
Candidate-level ERT compares the local, horizontal-edge, and vertical-cloud routes for the same arriving task. The unified route-completion estimate is

\\begin{equation}  
\\widehat T\_i(\\alpha,t)=\\begin{cases}\\widehat T\_i^L(t), & \\alpha=\\alpha\_{s\_i}^L,\\\\\\widehat T\_{i,k}^O(t), & \\kappa(\\alpha)=k\\neq s\_i.\\end{cases}  
\\tag{31}  
\\end{equation}

Candidate-level Effective Remaining Time is then defined as

For every physically available action $\\alpha\\in\\mathcal{A}\_{s\_i}(t)$,

\\begin{equation}  
\\mathsf{ERT}\_i^C(\\alpha,t)=  
d\_i-\\widehat T\_i(\\alpha,t).  
\\tag{32}  
\\end{equation}

A non-negative candidate ERT is exactly equivalent to the estimated deadline-feasibility condition $\\widehat T\_i(\\alpha,t)\\leq d\_i$. The valid action set is defined once in Section E from this condition.

ERT is therefore a completion-slack variable rather than an unrelated heuristic score: it directly measures the deadline remaining after the estimated route completion requirement is accounted for.

**3\) ERT Interpretation**  
The sign and magnitude of ERT provide a compact interpretation of task urgency. A large positive ERT means that the task has sufficient remaining time and can tolerate some queueing or transmission delay. A small positive ERT indicates that the task is still feasible but urgent. A zero ERT represents a boundary condition in which any additional delay may cause deadline violation. A negative ERT indicates that the task is estimated to miss its deadline under the current queue or candidate condition.

ECHO uses this interpretation consistently across the decision pipeline. At the queue level, the smallest non-negative ERT identifies the most urgent predicted-feasible task, while minimum lateness is used when all waiting tasks are predicted late. At candidate selection, negative-ERT actions are masked whenever at least one valid action exists; if all actions are negative, the minimum-lateness fallback is selected and its predicted miss risk is stored for reward calculation. Actual task removal is penalized separately. Thus, ERT connects deadline representation, queue scheduling, candidate filtering, and distributed DRL learning.

**D. Deadline-Aware Queue Scheduling**

ECHO controls the service order of the local and outbound-transfer queues. Scheduling is non-preemptive: an active computation or transmission continues until completion, while waiting tasks may be reordered whenever the corresponding resource becomes idle. Expired waiting tasks are removed before each service selection, and completion estimates are recomputed.

1\) Local Queue Scheduling  
Let $\\mathcal{Q}\_n^L(t)$ contain the waiting local tasks, excluding any task currently in service. The predicted-feasible local-task set is

\\begin{equation}  
\\mathcal{F}\_n^L(t)=\\left\\{\\xi\_i\\in\\mathcal{Q}\_n^L(t)\\mid \\mathsf{ERT}\_i^L(t)\\geq0\\right\\}.  
\\tag{33}  
\\end{equation}

If this set is non-empty, the local processor selects the task with the smallest non-negative ERT:

\\begin{equation}  
\\xi\_n^{L,\*}(t)=\\arg\\min\_{\\xi\_i\\in\\mathcal{F}\_n^L(t)}\\mathsf{ERT}\_i^L(t).  
\\tag{34}  
\\end{equation}

If all waiting tasks are predicted late, ECHO does not give automatic priority to the most negative ERT. Instead, it selects the task with the smallest estimated queue-level lateness,

\\begin{equation}  
\\ell\_i^L(t)=\\max\\left\\{0,\\widehat T\_i^L(t)-d\_i\\right\\},  
\\tag{35}  
\\end{equation}

\\begin{equation}  
\\xi\_n^{L,\*}(t)=\\arg\\min\_{\\xi\_i\\in\\mathcal{Q}\_n^L(t)}\\ell\_i^L(t),\\quad \\mathcal{F}\_n^L(t)=\\emptyset.  
\\tag{36}  
\\end{equation}

FIFO order is used only to break equal ERT or equal-lateness values. After admission, completion, removal, or service selection, the provisional order and all local completion and ERT values are updated.

2\) Outbound-Transfer Queue Scheduling  
The same non-preemptive rule is applied before transmission. Let $\\mathcal{Q}\_n^X(t)$ contain the waiting outbound-transfer tasks, each retaining destination $k\_i=\\kappa(\\alpha\_i)$. The predicted-feasible transfer set is

\\begin{equation}  
\\mathcal{F}\_n^X(t)=\\left\\{\\xi\_i\\in\\mathcal{Q}\_n^X(t)\\mid \\mathsf{ERT}\_i^X(t)\\geq0\\right\\}.  
\\tag{37}  
\\end{equation}

When this set is non-empty, the next transmitted task is

\\begin{equation}  
\\xi\_n^{X,\*}(t)=\\arg\\min\_{\\xi\_i\\in\\mathcal{F}\_n^X(t)}\\mathsf{ERT}\_i^X(t).  
\\tag{38}  
\\end{equation}

When every waiting transfer task is predicted late, the source EA uses end-to-end minimum lateness:

\\begin{equation}  
\\ell\_i^X(t)=\\max\\left\\{0,\\widehat T\_{i,k\_i}^O(t)-d\_i\\right\\},  
\\tag{39}  
\\end{equation}

\\begin{equation}  
\\xi\_n^{X,\*}(t)=\\arg\\min\_{\\xi\_i\\in\\mathcal{Q}\_n^X(t)}\\ell\_i^X(t),\\quad \\mathcal{F}\_n^X(t)=\\emptyset.  
\\tag{40}  
\\end{equation}

The selected task is transmitted to its stored destination; the dispatch block applies that destination without a new decision. FIFO remains the tie-breaker. This rule prevents an already highly late task from automatically displacing a still-feasible urgent task merely because its ERT is more negative.

3\) Destination Queue Consideration  
Destination queues remain destination-side processing structures and are not reordered by the source EA. Their remaining computational workload, adjusted active-queue count, and observed or LSTM-predicted load are used to estimate candidate completion time and candidate-level ERT. Thus, ECHO directly controls the service order only in the source local and outbound-transfer queues, while destination-queue conditions influence destination feasibility through completion-time estimation.

**E. Deadline-Aware Candidate Selection**  
**For each arriving task, ECHO evaluates the direct local, horizontal-edge, and vertical-cloud actions defined in (3). Candidate completion and ERT are computed by (31)-(32) before the task is inserted into a source queue.**

**1\) Fixed and Deadline-Valid Action Sets**

**The fixed canonical output set of EA n is defined in (41). The source position and disconnected horizontal destinations remain in the fixed network output but are marked unavailable.**

**\\begin{equation}**  
**\\bar{\\mathcal{A}}\_n=\\{\\alpha\_n^L,\\alpha\_{n,1}^H,\\ldots,\\alpha\_{n,N}^H,\\alpha\_n^V\\}.**  
**\\tag{41}**  
**\\end{equation}**

**The deadline-valid set for task i is defined in (42).**

**\\begin{equation}**  
**\\mathcal{V}\_i(t)=\\{\\alpha\\in\\mathcal{A}\_{s\_i}(t)\\mid \\mathsf{ERT}\_i^C(\\alpha,t)\\geq0\\}.**  
**\\tag{42}**  
**\\end{equation}**

**2\) Minimum-Lateness Fallback**

**If no action is predicted to satisfy the deadline, candidate lateness and the fallback action are defined in (43)-(44).**

**\\begin{equation}**  
**\\Lambda\_i(\\alpha,t)=\\max\\{0,\\widehat T\_i(\\alpha,t)-d\_i\\}.**  
**\\tag{43}**  
**\\end{equation}**

**\\begin{equation}**  
**\\alpha\_i^{fb}(t)=\\arg\\min\_{\\alpha\\in\\mathcal{A}\_{s\_i}(t)}\\Lambda\_i(\\alpha,t).**  
**\\tag{44}**  
**\\end{equation}**

**The fallback avoids an arbitrary choice under overload and records predicted deadline risk for the later reward.**

**3\) Effective Set and Action Mask**

**The effective set and the binary canonical-action mask are defined in (45)-(46).**

**\\begin{equation}**  
**\\mathcal{U}\_i(t)=\\begin{cases}\\mathcal{V}\_i(t), & \\mathcal{V}\_i(t)\\neq\\emptyset,\\\\ \\{\\alpha\_i^{fb}(t)\\}, & \\mathcal{V}\_i(t)=\\emptyset.\\end{cases}**  
**\\tag{45}**  
**\\end{equation}**

**\\begin{equation}**  
**\\mu\_{n,j}(t)=\\mathbb{I}\[\\bar\\alpha\_{n,j}\\in\\mathcal{U}\_i(t)\],\\qquad \\boldsymbol{\\mu}\_n(t)=\[\\mu\_{n,j}(t)\]\_j.**  
**\\tag{46}**  
**\\end{equation}**

**The same mask is used in exploration, exploitation, and Double-DQL target-action selection.**

**4\) Direct Decision and Queue Admission**

**Action admissibility, source-queue admission, stored dispatch metadata, and the pending decision record are specified in (47)-(50).**

**\\begin{equation}**  
**\\alpha\_i\\in\\mathcal{U}\_i(t\_i^a).**  
**\\tag{47}**  
**\\end{equation}**

**\\begin{equation}**  
**\\xi\_i\\in\\mathcal{Q}\_i^{src}(t\_i^a).**  
**\\tag{48}**  
**\\end{equation}**

**\\begin{equation}**  
**\\mathbf{g}\_i=(s\_i,k\_i,t\_i^a,b\_i,\\nu\_i,d\_i).**  
**\\tag{49}**  
**\\end{equation}**

**\\begin{equation}**  
**\\mathbf{p}\_i=(\\xi\_i,\\mathbf{s}\_{s\_i}(t\_i^a),\\alpha\_i,t\_i^a,d\_i,I\_i^R)\\in\\mathcal{P}\_{s\_i}.**  
**\\tag{50}**  
**\\end{equation}**

**Thus, action selection occurs once at task arrival. The selected action belongs to the effective set in (47), the task is admitted by (48), and an offloaded task carries the destination already defined in (6) through metadata (49). No second destination optimization is performed. The risk indicator stored in (50) is formally defined in (56) and is available at decision time.**

**F. Multi-Agent Distributed DRL Formulation**

**Each EA acts as an autonomous learning agent. The recurrent load encoder, dueling value–advantage decomposition, Double-DQL target separation, replay memory, and target network follow established distributed learning components \[37\]. ECHO defines its own state, admissible actions, reward semantics, and task-level semi-Markov transition timing.**

**1\) State Representation**

**Queue occupancies and remaining source-side workloads are defined in (51)-(52).**

**\\begin{equation}**  
**q\_n^L(t)=|\\mathcal{Q}\_n^L(t)|,\\qquad q\_n^X(t)=|\\mathcal{Q}\_n^X(t)|.**  
**\\tag{51}**  
**\\end{equation}**

**\\begin{equation}**  
**\\Psi\_n^L(t)=\\varrho\_n^L(t)+\\sum\_{\\xi\_h\\in\\mathcal{Q}\_n^L(t)}\\tau\_h^L,\\qquad \\Psi\_n^X(t)=\\varrho\_n^X(t)+\\sum\_{\\xi\_h\\in\\mathcal{Q}\_n^X(t)}\\tau\_{h,k\_h}^X.**  
**\\tag{52}**  
**\\end{equation}**

**The fixed-dimensional normalized state is defined in (53).**

**\\begin{equation}**  
**\\mathbf{s}\_n(t)=\[\\tilde\\chi\_n(t),\\tilde b\_i,\\tilde\\nu\_i,\\tilde\\delta\_i,\\tilde q\_n^L,\\tilde q\_n^X,\\tilde\\Psi\_n^L,\\tilde\\Psi\_n^X,\\tilde\\varrho\_n^L,\\tilde\\varrho\_n^X,\\tilde{\\mathbf{o}}\_n,\\mathbf{z}\_n,\\widetilde{\\mathsf{ERT}}\_{n,\\min}^L,\\widetilde{\\mathsf{ERT}}\_{n,\\min}^X,\\tilde{\\mathbf{e}}\_i^C,\\boldsymbol{\\mu}\_n\].**  
**\\tag{53}**  
**\\end{equation}**

**When no task arrives, task-specific and candidate-specific entries are zero, while queue, service, and load entries remain active. Queue occupancies distinguish an empty queue from a queue whose minimum ERT is exactly zero. Numerical features are min–max normalized to bounded ranges, ERT values are symmetrically clipped before normalization, and the action mask is zero when no decision is required.**

**The fixed candidate-ERT vector is defined in (54).**

**\\begin{equation}**  
**\\mathbf{e}\_i^C(t)=\[\\mathsf{ERT}\_i^C(\\alpha,t)\]\_{\\alpha\\in\\bar{\\mathcal{A}}\_{s\_i}}.**  
**\\tag{54}**  
**\\end{equation}**

**2\) Effective Actions**

**The fixed canonical set, deadline-valid set, fallback, effective set, and action mask are already defined in (41)-(46) and are used without changing the network output dimension.**

**3\) Task Outcome and Reward**

**Task i is resolved at slot t\_i^r by deadline-satisfied completion or by a dropped outcome. Its realized system duration is defined in (55).**

**\\begin{equation}**  
**T\_i^{sys}=t\_i^r-t\_i^a+1.**  
**\\tag{55}**  
**\\end{equation}**

**The predicted-risk and realized-drop indicators are defined in (56)-(57).**

**\\begin{equation}**  
**I\_i^R=\\begin{cases}1, & \\mathcal{V}\_i(t\_i^a)=\\emptyset,\\\\0, & \\text{otherwise}.\\end{cases}**  
**\\tag{56}**  
**\\end{equation}**

**\\begin{equation}**  
**I\_i^D=\\begin{cases}1, & \\xi\_i\\text{ does not achieve deadline-satisfied completion},\\\\0, & \\text{otherwise}.\\end{cases}**  
**\\tag{57}**  
**\\end{equation}**

**The task-level reward is defined in (58).**

**\\begin{equation}**  
**r\_i=-T\_i^{sys}-\\lambda\_R I\_i^R-\\lambda\_D I\_i^D.**  
**\\tag{58}**  
**\\end{equation}**

**The risk term describes decision-time predicted infeasibility, whereas the drop term describes the realized failure. They remain distinct because changing load may invalidate an initially feasible action, while a fallback action may occasionally succeed.**

**4\) Task-Level Semi-Markov Transition**

**A task reward is known when the task is resolved at $t\_i^r$, but the next action mask is defined only at a decision epoch. Let $t\_i^+$ be the first subsequent slot at the source EA for which $t\_i^+\>t\_i^r$ and $\\chi\_{s\_i}(t\_i^+)=1$. If no such slot occurs before the episode ends, $t\_i^+$ denotes the terminal decision state at $T+1$. The realized reward is attached to the pending record at $t\_i^r$, and the transition is finalized when $\\mathbf{s}\_{s\_i}(t\_i^+)$ becomes available.**

**\\begin{equation}**  
**\\zeta\_i=(\\mathbf{s}\_{s\_i}(t\_i^a),\\alpha\_i,r\_i,\\mathbf{s}\_{s\_i}(t\_i^+),\\Delta\_i),\\qquad \\Delta\_i=t\_i^+-t\_i^a.**  
**\\tag{59}**  
**\\end{equation}**

**This aligns the delayed task reward with the next state at which another route decision can actually be made and ensures that the target-state action mask is well-defined. Although the outcome is observed at $t\_i^r$, the reward is credited to the originating decision at $t\_i^a$. The policy objective is therefore given in (60).**

**\\begin{equation}**  
**\\pi\_n^\*=\\arg\\max\_{\\pi\_n}\\mathbb{E}\_{\\pi\_n}\\left\[\\sum\_{\\xi\_i:s\_i=n}\\gamma^{t\_i^a-1}r\_i\\right\].**  
**\\tag{60}**  
**\\end{equation}**

**5\) Dueling Double-DQL Model**

**The LSTM embedding in (28) is concatenated with the remaining state features before the fully connected layers. The Dueling-DQL and Double-DQL components follow \[37\], while ECHO uses the state, mask, reward, and semi-Markov target defined here.**

**\\begin{equation}**  
**Q\_n(\\mathbf{s},\\alpha;\\theta\_n)=V\_n(\\mathbf{s};\\theta\_n)+A\_n(\\mathbf{s},\\alpha;\\theta\_n)-\\frac{1}{|\\bar{\\mathcal{A}}\_n|}\\sum\_{\\alpha'\\in\\bar{\\mathcal{A}}\_n}A\_n(\\mathbf{s},\\alpha';\\theta\_n).**  
**\\tag{61}**  
**\\end{equation}**

**\\begin{equation}**  
**Q\_n^\\mu(\\mathbf{s},\\alpha;t)=\\begin{cases}Q\_n(\\mathbf{s},\\alpha;\\theta\_n), & \\alpha\\in\\mathcal{U}\_i(t),\\\\-\\infty, & \\alpha\\notin\\mathcal{U}\_i(t).\\end{cases}**  
**\\tag{62}**  
**\\end{equation}**

**During training, action selection follows the masked epsilon-greedy rule in (63).**

**\\begin{equation}**  
**\\alpha\_i=\\begin{cases}\\text{uniform sample from }\\mathcal{U}\_i(t\_i^a), & \\text{with probability }\\epsilon,\\\\\\arg\\max\_{\\alpha\\in\\bar{\\mathcal{A}}\_{s\_i}}Q\_{s\_i}^\\mu(\\mathbf{s}\_{s\_i}(t\_i^a),\\alpha;t\_i^a), & \\text{with probability }1-\\epsilon.\\end{cases}**  
**\\tag{63}**  
**\\end{equation}**

**For a replayed transition, the masked next action, Double-DQL target, online prediction, and mini-batch loss are defined in (64)-(67).**

**\\begin{equation}**  
**\\alpha\_i^+=\\arg\\max\_{\\alpha'\\in\\bar{\\mathcal{A}}\_{s\_i}}Q\_{s\_i}^\\mu(\\mathbf{s}\_{s\_i}(t\_i^+),\\alpha';t\_i^+).**  
**\\tag{64}**  
**\\end{equation}**

**\\begin{equation}**  
**y\_i=\\begin{cases}r\_i, & \\mathbf{s}\_{s\_i}(t\_i^+)\\text{ is terminal},\\\\r\_i+\\gamma^{\\Delta\_i}Q\_{s\_i}^-(\\mathbf{s}\_{s\_i}(t\_i^+),\\alpha\_i^+;\\theta\_{s\_i}^-), & \\text{otherwise}.\\end{cases}**  
**\\tag{65}**  
**\\end{equation}**

**\\begin{equation}**  
**\\widehat y\_i=Q\_{s\_i}(\\mathbf{s}\_{s\_i}(t\_i^a),\\alpha\_i;\\theta\_{s\_i}).**  
**\\tag{66}**  
**\\end{equation}**

**\\begin{equation}**  
**\\mathcal{L}\_n(\\theta\_n)=\\frac{1}{|B|}\\sum\_{i\\in B}(y\_i-\\widehat y\_i)^2.**  
**\\tag{67}**  
**\\end{equation}**

**The target parameters are copied from the online parameters every target-copy period. The same action mask is applied during exploration, exploitation, and target-action selection.**

G. Algorithmic Workflow of ECHO

The training and inference procedures use the same slot-level environment sequence. Service is non-preemptive, an offloaded task carries its selected destination until dispatch, transfer-queue priority uses end-to-end ERT, and learning uses the task-level transition in (59).

1\) Training Procedure

Algorithm 1\. Training procedure of ECHO at EA n  
1: Initialize replay memory, pending records, queues, task records, load history, online and target networks, the LSTM encoder, and learning parameters.  
2: for each training episode do  
3: Reset the environment, queues, active services, and unresolved-task records.  
4: for each slot t do  
5: Receive the newest queue/load update; otherwise use the LSTM estimate from (28).  
6: Advance local, transfer, and destination services without preemption; move completed transmissions to destination queues.  
7: Resolve successful completions and dropped outcomes, compute their realized rewards through (55)-(58), and retain the updated records in the pending buffer until their next decision states are observed.  
8: Remove expired waiting tasks, recompute (29)-(30), and schedule idle local and transfer resources using (33)-(40).  
9: Observe the arrival indicator.  
10: if a task arrives then  
11: Create its descriptor, source, arrival slot, and deadline using (2).  
12: Evaluate route completion by (31), candidate ERT by (32), valid actions by (42), and fallback by (44) when required.  
13: Build the state by (51)-(54), apply (45)-(46), select the action by (63), and insert the task according to (47)-(49).  
14: Store the pending decision record in (50).  
15: end if  
16: Update the observed load vector, history matrix, and LSTM estimate.  
17: For each resolved pending task whose next decision epoch is the current arrival slot, finalize (59) with $\\mathbf{s}\_{s\_i}(t\_i^+)$, move it to replay memory, and remove the pending record.  
18: When replay memory contains a mini-batch, compute (64)-(67) and update the online network.  
19: Every target-copy period, set the target parameters equal to the online parameters.  
20: end for  
21: At episode termination, mark unresolved admitted tasks as dropped, attach terminal rewards, finalize all outcome-known pending records with the terminal next-decision state at $T+1$, and decay epsilon.  
22: end for

2\) Inference Procedure

Algorithm 2\. Inference procedure of ECHO at EA n  
1: Receive the newest queue/load update or use the LSTM estimate.  
2: Advance local, transfer, and destination services; move completed transmissions and resolve outcomes.  
3: Remove expired waiting tasks, recompute (29)-(30), and schedule idle resources using (33)-(40).  
4: Observe the arrival indicator.  
5: if a task arrives then  
6: Create its descriptor and deadline using (2).  
7: Evaluate (31)-(32), construct the valid set (42), and use fallback (44) when required.  
8: Build the state through (51)-(54) and apply the effective set and mask in (45)-(46).  
9: Select the highest masked Q-value, insert the task into the queue in (48), and store destination metadata when offloading is selected.  
10: end if  
11: Update queue status, destination workload, and load history for slot t+1.

3\) Method Summary

ECHO is fully specified by three interacting controls: end-to-end completion estimation, ERT-based source-queue scheduling, and masked distributed action selection. The local queue is prioritized by local completion slack, whereas the outbound-transfer queue is prioritized by end-to-end offloading slack that includes destination conditions. Every new task is evaluated over local, horizontal, and vertical routes, and no second destination decision is made after admission. Resolved tasks generate task-level semi-Markov replay transitions, so delayed rewards are paired with the next valid decision state and the correct discount duration.
