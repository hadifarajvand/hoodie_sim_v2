# Feature 090-A Runtime Core Validation

- Phase: 090-A runtime core only
- Trained HOODIE policy: not implemented
- Figure 8/9/10/11 claims: not allowed
- Forecast mode: `gated_no_lstm_trace`
- Topology mode: `complete_edge_graph`
- Topology temporary: `True`
- Drain phase active: yes
- Public CPU sharing active: yes
- Delayed reward collection active: yes
- Bernoulli arrivals active: yes
- Private queue active: yes
- Offloading queue active: yes
- Completion/drop status separated: yes

## Summary
{
  "arrival_opportunities": 2000,
  "arrival_rate_configured": 0.5,
  "arrival_rate_observed": 0.5175,
  "arrived_tasks": 1035,
  "completed_tasks": 379,
  "dropped_tasks": 44,
  "reward_event_count": 423,
  "unresolved_tasks": 612
}

## Warnings
[
  "complete_edge_graph used as explicit temporary topology mode",
  "some tasks remain unresolved at episode end"
]
