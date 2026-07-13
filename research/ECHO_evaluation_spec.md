---
source_document: "https://docs.google.com/document/d/17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE/edit"
source_document_id: "17iqZWA0bF5unbyuVYnRiW1IUcr0Ctb2KFw1f5XE2poE"
source_tab_title: "ارزیابی"
source_tab_id: "t.oxhaq5ojy5h6"
source_revision_id: "ALtnJHyTLdhKaOnVqfvxB74eKtegK8Hrsx5l2yaYdk68tSHgf-QdYtM6nrsTZrwFDm3DbTUFkeWajyCFP0Eevns2d7r0_twwuuYjD4ZcMQ"
exported_at_utc: "2026-07-12T06:55:12.371510+00:00"
authority: "Primary ECHO evaluation and figure specification"
---

# ارزیابی

**IV. Experimental Evaluation**

**This section evaluates ECHO by following the same experimental organization as the base article while preserving the deadline-aware mechanisms and task lifecycle defined in Section III. The evaluation contains one topology figure, two learning-parameter panels, five behavioral and scalability panels, six comparative-performance panels, and one LSTM ablation figure. Accordingly, the section uses five numbered evaluation figures containing fifteen panels in total, and all figure positions remain as placeholders until the simulator exports the final PNG files.**

**A. Experimental Setup and Common Parameters**

**The experiments are conducted in a time-slotted simulator representing the IoT-edge-cloud continuum in Section III. The default environment contains 20 Edge Agents and one cloud node. Every generated task is indivisible and may be executed locally, offloaded horizontally to a connected EA, or offloaded vertically to the cloud. Local processing and source-side transmission are non-preemptive. ECHO may reorder only waiting tasks in the local and outbound-transfer queues, while source-indexed destination queues retain FIFO order and the shared destination-processing rule.**

**Each episode contains 110 time slots. New tasks and offloading decisions are enabled during the first 100 slots, and the final 10 slots form a drain interval during which no new task is generated. Tasks that do not achieve deadline-satisfied completion by the end of the drain interval are counted as dropped. The synthetic task descriptors consist of arrival time, task size, processing density, and timeout. Within each seed, identical task traces are reused across ECHO, HOODIE, and every baseline method.**

**The default edge layer uses the 20-EA adjacency matrix of the base evaluation. Figure 4 displays this matrix as an undirected graph and must be generated directly from the topology used by the simulator so that the paper and implementation cannot diverge.**

**\[Insert Figure 4 here\]**  
**Figure 4\. Edge-layer topology graph of the connectivity matrix used in the ECHO experiments with 20 EAs.**

**The default system and learning values are summarized in Table 2\. When a panel varies one parameter, all parameters not explicitly named in that panel remain fixed at the values in Table 2\.**

**Table 2\. System and learning parameters used in the ECHO experiments.**

| Parameter | Symbol | Baseline value |
| :---- | :---- | :---- |
| Task-arrival probability | P | 0.5 |
| Horizontal data rate | R\_H | 30 Mbps |
| Vertical data rate | R\_V | 10 Mbps |
| Task size | b\_i | {2.0,2.1,...,5.0} Mbits |
| Processing density | \\nu\_i | 0.297 Gcycles/Mbit |
| Number of EAs | N | 20 |
| EA local capacity | f\_n^L | 5 GHz |
| EA destination capacity | f\_k^{EA} | 5 GHz |
| Cloud capacity | f^C | 30 GHz |
| Training episodes | N\_E | 5000 |
| Episode length | T | 110 slots |
| Decision/drain split | \-- | 100 decision \+ 10 drain slots |
| Time-slot duration | \\Delta | 0.1 s |
| Default timeout | \\delta\_i | 20 slots (2 s) |
| Learning rate | \\alpha\_{lr} | 7 × 10^-7 |
| Discount factor | \\gamma | 0.99 |
| Q-network hidden layers | \-- | 3 × 1024 ReLU units |
| Optimizer | \-- | Adam |
| Loss function | \\mathcal{L}\_n | Mean-squared error |
| Target-copy period | N\_{copy} | 2000 training iterations |
| LSTM lookback | W | 10 slots |
| LSTM hidden layer | \-- | 1 × 20 LSTM cells |
| Replay-memory size | N\_R | 10000 transitions |
| Mini-batch size | N\_B | 64 |
| Predicted-risk penalty | \\lambda\_R | 20 |
| Realized drop penalty | \\lambda\_D | 40 |
| ERT clipping bound | E\_{max} | \[-20,20\] slots |
| Feature normalization | \-- | Min-max scaling to \[-1,1\] |
| Evaluation protocol | \-- | 10 seeds × 200 held-out episodes |

The default values in Table 2 are used unless a panel explicitly varies one or more parameters. ECHO-specific quantities, including the predicted-risk penalty, realized-drop penalty, and ERT clipping bound, remain fixed during the base-matched experiments after being selected on validation traces. Every learning-based configuration is trained with the same random seeds and training budget, and all compared methods are evaluated on identical held-out task traces.

B. Learning-Parameter Selection

Following the experimental organization of the base article, the first composite result figure examines the learning rate and discount factor before the remaining experiments are conducted. The training metric is the accumulated task-level reward in (58), averaged across the distributed ECHO agents at each episode. Because delay and deadline-related penalties enter the reward negatively, values closer to zero indicate better training performance. These panels are used to select ECHO's learning parameters and are not interpreted as a direct numerical comparison with HOODIE, whose reward semantics are different.

For Fig. 5(a), the learning-rate sweep is alpha\_lr in {10^-9, 5x10^-9, 10^-8, 10^-7, 5x10^-7, 7x10^-7}, with gamma=0.99, N=20, and P=0.5. For Fig. 5(b), the discount-factor sweep is gamma in {0.2, 0.4, 0.6, 0.8, 0.99}, using the selected learning rate and the same default system configuration. Each curve spans 5000 training episodes and is averaged across the EAs and random seeds.

\[Insert Figure 5(a)-(b) here\]  
Figure 5\. Accumulated ECHO reward averaged across the distributed agents as a function of the training episode for different (a) learning rates alpha\_lr and (b) discount factors gamma.

After simulation, the discussion will identify the configuration that provides the most stable convergence and the best final validation performance. The selected values are then fixed for Figs. 6-8 so that the later scenario comparisons do not tune the learning parameters separately for each reported result.

C. ECHO Behavior and Scalability Analysis

The second composite result figure reproduces the five-panel behavioral analysis of the base article using the complete ECHO method. These panels explain how the learned ECHO policy reacts to task intensity, local processing capacity, system scale, and communication-rate conditions before the direct comparison with alternative offloading schemes.

In Fig. 6(a), the average accumulated ECHO reward is plotted against P in {0.1, 0.3, 0.5, 0.7, 0.9} for N in {10, 15, 20}. All other parameters follow Table 2\. This panel measures how the distributed policy responds as simultaneous task generation becomes more frequent.

In Fig. 6(b), the total numbers of local, horizontal-edge, and vertical-cloud actions are reported for P in {0.1, 0.3, 0.5, 0.7, 0.9} under the default 20-EA topology. The panel is descriptive rather than an optimization objective: a larger count for one route is not automatically better. Its purpose is to explain how ECHO redistributes tasks as load changes and to verify that masked or physically invalid actions are never selected.

In Fig. 6(c), the average accumulated reward is plotted against local EA processing capacity in {4, 5, 6, 7, 8, 9} GHz for N in {10, 15, 20}. Destination-side EA capacity is changed consistently with the tested edge-processing setting, while the cloud capacity and communication rates remain at their default values.

In Fig. 6(d), scalability is evaluated for N in {10, 15, 20, 25, 30} under three traffic profiles. Moderate traffic uses task sizes of 1-3 Mbits and P=0.5; heavy traffic uses task sizes of 2-5 Mbits and P=0.7; and extreme traffic uses task sizes of 3-7 Mbits and P=0.9. A topology of the corresponding size is generated for each value of N while preserving the same connectivity-generation rule.

In Fig. 6(e), scalability is evaluated for the same EA counts under three data-rate profiles: balanced capacity with R\_H=10 Mbps and R\_V=30 Mbps, horizontal-centric capacity with R\_H=20 Mbps and R\_V=20 Mbps, and vertical-centric capacity with R\_H=5 Mbps and R\_V=40 Mbps. The remaining parameters follow Table 2\.

\[Insert Figure 6(a)-(e) here\]  
Figure 6\. ECHO behavior under varying system parameters: (a) average reward versus task-arrival probability for different numbers of EAs; (b) local, horizontal-edge, and vertical-cloud action distribution across task-arrival probabilities; (c) average reward versus EA processing capacity; (d) average reward versus the number of EAs under different traffic scenarios; and (e) average reward versus the number of EAs under different offloading data-rate scenarios.

The interpretation of Fig. 6 will use reward trends together with task-drop, waiting-time, fallback, and action-mask logs. In particular, a reward change will not be attributed to ERT scheduling or candidate masking unless the corresponding task-level records support that explanation.

D. Comparative Performance Analysis

The principal comparison follows the six-panel organization of the base article. ECHO is evaluated against HOODIE and the same six baseline schemes: Random Offloader (RO), Full Local Computing (FLC), Vertical Offloader (VO), Horizontal Offloader (HO), Balanced Cyclic Offloader (BCO), and Minimum Latency Estimation Offloader (MLEO). RO randomly selects among physically available execution types, FLC always executes locally, VO always selects the cloud, HO selects a horizontal destination, BCO rotates among the available routes, and MLEO selects the route with the smallest estimated delay. All methods use the same arrivals, task descriptors, topology, processing capacities, data rates, deadlines, and random seeds.

Average delay is calculated only for tasks that achieve deadline-satisfied completion and is reported as a negative quantity, matching the convention of the base article; therefore, a value closer to zero is better. To prevent dropped tasks from being hidden by the conditional delay calculation, each delay panel is paired with a corresponding task-drop panel. Task drop ratio is the number of tasks without deadline-satisfied completion divided by the number of generated tasks.

For the delay panels in Figs. 7(a)-7(c), a high task timeout of 10 seconds is used so that sufficiently many tasks remain available for a meaningful delay comparison. Figure 7(a) varies P over {0.1, 0.3, 0.5, 0.7, 0.9}; Fig. 7(b) varies EA processing capacity over {3, 4, 5, 6, 7} GHz; and Fig. 7(c) varies task timeout over {9.6, 9.8, 10.0, 10.2, 10.4} seconds.

For the drop-ratio panels in Figs. 7(d)-7(f), stricter deadlines are used to expose differences in deadline handling. Figure 7(d) varies P over {0.1, 0.3, 0.5, 0.7, 0.9} with a 2-second timeout; Fig. 7(e) varies EA processing capacity over {3, 4, 5, 6, 7} GHz with a 2-second timeout; and Fig. 7(f) varies task timeout over {1.6, 1.8, 2.0, 2.2, 2.4} seconds. These three panels are the primary tests of the ECHO contribution because queue-level ERT, end-to-end candidate ERT, the valid-action mask, and minimum-lateness fallback directly target deadline-satisfied completion.

\[Insert Figure 7(a)-(f) here\]  
Figure 7\. Performance comparison of ECHO against HOODIE and six baseline offloading schemes under varying conditions: (a) average delay versus task-arrival probability; (b) average delay versus EA processing capacity; (c) average delay versus task timeout; (d) task drop ratio versus task-arrival probability; (e) task drop ratio versus EA processing capacity; and (f) task drop ratio versus task timeout. Average delay is negative by convention.

The result analysis will first describe the common trend of each panel, then compare ECHO with HOODIE using absolute and relative differences, and finally use queue waiting, selected-route feasibility, and fallback statistics to interpret the observed behavior. Any operating point at which ECHO is equal to or worse than HOODIE will be reported explicitly. No superiority statement or numerical improvement is inserted before the final simulation outputs are available.

E. Impact of LSTM Inclusion

The last evaluation figure isolates the contribution of the LSTM-based load representation and recovery estimate. Complete ECHO is compared with ECHO-NoLSTM, which uses the latest received destination status directly and does not replace missing or delayed information with an LSTM estimate. The experiment uses N=20, P=0.3, a one-second task timeout, and the selected alpha\_lr and gamma values; the remaining parameters follow Table 2\. The horizontal axis is training episode from 0 to 3000, and the vertical axis is average task delay using the same negative-delay convention as Fig. 7\.

\[Insert Figure 8 here\]  
Figure 8\. Average task delay of ECHO with and without the LSTM-based load-estimation component as a function of the training episode.

The analysis will compare convergence speed, final delay, and stability. The role of LSTM is considered supported only when the delay difference is consistent across seeds and, where delayed controller information is present, when the task-level logs show improved completion estimation or route selection.

F. Evaluation Protocol and Result Reporting

Every reported point is evaluated over 10 fixed random seeds and 200 held-out episodes per seed. Task traces are paired across methods within each seed, and the learning-based methods receive equal training budgets, replay capacity, batch size, optimizer, target-update frequency, and network width unless the tested panel explicitly changes one of these quantities. The selected checkpoint is determined using validation traces and the final held-out test traces are used once for reporting.

For a method, seed, and operating point, task drop ratio is computed by pooling generated and dropped task counts across the 200 episodes before taking the ratio. Reported means and 95% confidence intervals are then calculated across seeds. The implementation stores the configuration, topology, seed, checkpoint, task-level route decision, predicted completion, candidate ERT, waiting times, completion or removal slot, and drop indicator for every run. Each composite figure is exported as one publication-quality vector file and one 300-dpi PNG, while panel-level and seed-level values are retained as CSV files.

Before a result is accepted, the simulator verifies that generated tasks equal the sum of deadline-satisfied and dropped tasks, no masked action is selected by ECHO, all compared methods use identical held-out trace identifiers, and the execution model used by the simulator matches the completion estimator defined in Section III. With these settings and figure placeholders fixed, the Evaluation section is frozen until the final simulation outputs are inserted.
