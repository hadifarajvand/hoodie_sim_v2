# Controlled Mechanistic Sweeps

## Metadata
- **feature_id**: 020-controlled-mechanistic-sweeps
- **generated_by**: controlled_mechanistic_sweeps
- **deterministic**: True
- **source_refs**: ['specs/020-controlled-mechanistic-sweeps/spec.md', 'specs/020-controlled-mechanistic-sweeps/plan.md', 'specs/020-controlled-mechanistic-sweeps/research.md', 'src/environment/traffic_config.py', 'src/environment/traffic_generator.py', 'src/environment/traffic_observer.py', 'src/environment/gym_adapter.py']

## Sweep Definitions
### arrival_probability
- parameter: arrival_probability
- values: [0.2, 0.5, 0.8]
- fixed_seeds: [7]
- expected_direction: nondecreasing
- control_source: TrafficConfig.arrival_probability
### timeout
- parameter: timeout_slots
- values: [1, 2, 3]
- fixed_seeds: [7]
- expected_direction: nonincreasing
- control_source: TrafficConfig.timeout_slots
### cpu_capacity
- parameter: cpu_capacity_per_slot_agent
- values: [1.0, 2.0, 4.0]
- fixed_seeds: [7]
- expected_direction: nondecreasing
- control_source: ComputeConfig.cpu_capacity_per_slot_agent
### link_rate
- parameter: link_rate
- values: ['low', 'medium', 'high']
- fixed_seeds: [7]
- expected_direction: nondecreasing
- control_source: unsupported
### topology_density
- parameter: topology_density
- values: ['sparse', 'default', 'dense']
- fixed_seeds: [7]
- expected_direction: nondecreasing
- control_source: TopologyGraph.legal_adjacency

## Fixed Inputs
- arrival_probability seed=7 value=0.2 trace=paper_default-7
- arrival_probability seed=7 value=0.5 trace=paper_default-7
- arrival_probability seed=7 value=0.8 trace=paper_default-7
- timeout seed=7 value=1 trace=controlled-mechanistic-sweeps-7
- timeout seed=7 value=2 trace=controlled-mechanistic-sweeps-7
- timeout seed=7 value=3 trace=controlled-mechanistic-sweeps-7
- cpu_capacity seed=7 value=1.0 trace=controlled-mechanistic-sweeps-7
- cpu_capacity seed=7 value=2.0 trace=controlled-mechanistic-sweeps-7
- cpu_capacity seed=7 value=4.0 trace=controlled-mechanistic-sweeps-7
- link_rate seed=7 value=low trace=unsupported-link_rate-low
- link_rate seed=7 value=medium trace=unsupported-link_rate-medium
- link_rate seed=7 value=high trace=unsupported-link_rate-high
- topology_density seed=7 value=sparse trace=controlled-mechanistic-sweeps-7
- topology_density seed=7 value=default trace=controlled-mechanistic-sweeps-7
- topology_density seed=7 value=dense trace=controlled-mechanistic-sweeps-7

## Observations
- arrival_probability seed=7 value=0.2 indicator=0.3333333333333333 evidence=True summary=arrivals=2, observed_probability=0.3333333333333333
- arrival_probability seed=7 value=0.5 indicator=0.6666666666666666 evidence=True summary=arrivals=4, observed_probability=0.6666666666666666
- arrival_probability seed=7 value=0.8 indicator=1.0 evidence=True summary=arrivals=6, observed_probability=1.0
- timeout seed=7 value=1 indicator=1.0 evidence=True summary=dropped=1.0 final_outcomes=['dropped']
- timeout seed=7 value=2 indicator=1.0 evidence=True summary=dropped=1.0 final_outcomes=['dropped']
- timeout seed=7 value=3 indicator=0.0 evidence=True summary=dropped=0.0 final_outcomes=['completed']
- cpu_capacity seed=7 value=1.0 indicator=0.0 evidence=True summary=completed=0.0 final_outcomes=['dropped']
- cpu_capacity seed=7 value=2.0 indicator=1.0 evidence=True summary=completed=1.0 final_outcomes=['completed']
- cpu_capacity seed=7 value=4.0 indicator=1.0 evidence=True summary=completed=1.0 final_outcomes=['completed']
- link_rate seed=7 value=low indicator=None evidence=False summary=no direct public control for link rate; instrumentation gap recorded
- link_rate seed=7 value=medium indicator=None evidence=False summary=no direct public control for link rate; instrumentation gap recorded
- link_rate seed=7 value=high indicator=None evidence=False summary=no direct public control for link rate; instrumentation gap recorded
- topology_density seed=7 value=sparse indicator=0.0 evidence=True summary=offload_opportunities=0
- topology_density seed=7 value=default indicator=1.0 evidence=True summary=offload_opportunities=1
- topology_density seed=7 value=dense indicator=2.0 evidence=True summary=offload_opportunities=2

## Monotonic Checks
- arrival_probability: pass (full) - arrival_probability rose monotonically: [0.3333333333333333, 0.6666666666666666, 1.0].
- timeout: pass (full) - timeout fell monotonically: [1.0, 1.0, 0.0].
- cpu_capacity: pass (full) - cpu_capacity rose monotonically: [0.0, 1.0, 1.0].
- link_rate: instrumentation_gap (none) - link_rate has no direct public control source: unsupported.
- topology_density: pass (full) - topology_density rose monotonically: [0.0, 1.0, 2.0].

## Warnings
- None

## Instrumentation Gaps
- link rate: No direct public link-rate hook exists in the current environment interface.

## Limitations
- This feature is diagnostic only and does not prove paper-level completeness.
- Unsupported or unobservable dimensions remain classified instead of being patched.

## No Campaign Rerun Disclaimer
No baseline campaigns were rerun to generate this report.

## No Paper Validity Disclaimer
This report is not a paper-validity or reproduction-completeness claim.

## Reproducibility
- **approved_interpreter**: /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
- **fixed_seeds**: [7]
- **deterministic_ordering**: definitions -> fixed inputs -> observations -> checks
- **run_count_per_value**: 1

## Overall Status
instrumentation_gap
