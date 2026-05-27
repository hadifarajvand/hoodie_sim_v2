# Research: Feature 065

## Decision: repair state/action fidelity before more training

The current release-gated pipeline is useful but the state/action abstraction is too coarse for a paper-faithful HOODIE mechanism. Feature 065 must repair the contract before any new distributed training feature.

## Decision: exact-destination action registry

The generic three-action mapping is insufficient because horizontal offloading must select a specific destination Edge Agent. The paper-faithful contract therefore defines a per-source action registry with local/self, exact legal neighboring Edge-Agent destinations, and Cloud.

## Decision: structured state before flattened tensor

The implementation must keep a structured state contract so paper components remain inspectable. Flattening is allowed only as a deterministic adapter layer.

## Decision: LSTM input is load-history matrix

The LSTM path must be driven by node active queue load history with shape `W × (N+1)`. The existing 3-column replay state can remain only as a legacy compatibility path.

## Decision: no training rerun in this feature

This feature repairs the environment/training interface. It does not rerun the full campaign or create paper reproduction claims.
