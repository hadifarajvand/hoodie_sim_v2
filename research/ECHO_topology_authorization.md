# ECHO Scalable Topology Construction Authorization

## Status

**Author-approved methodological addendum**

This addendum resolves the previously unspecified topology-generation rule required for the ECHO scalability experiments in Figure 6(d) and Figure 6(e).

It does not claim that the rule was provided by the HOODIE paper. It is an explicit, documented ECHO experimental-design decision derived from the approved 20-EA topology.

## Approved rule: anchored degree-profile-preserving scaling

Let `A20` be the exact approved undirected 20-EA adjacency matrix already stored in the repository.

### 1. Anchor topology

For `N = 20`, use `A20` unchanged.

The topology shown in Figure 4 must be generated directly from this exact runtime matrix.

### 2. Non-20 topology sizes

For each `N` in `{10, 15, 25, 30}`, construct one connected, undirected, simple graph by scaling the degree profile of `A20`.

The generator must:

1. Validate that `A20` is symmetric, loop-free, and connected.
2. Extract and sort the degree sequence of `A20`.
3. Produce an `N`-node target degree sequence by deterministic quantile interpolation/resampling of the sorted `A20` degree sequence.
4. Clamp every target degree to `[1, N-1]` and to the observed supported degree range where possible.
5. Adjust the sequence minimally so that:
   - its sum is even;
   - it is graphical;
   - its mean degree remains as close as possible to the mean degree of `A20`.
6. Realize the sequence as a simple graph using a deterministic Havel-Hakimi construction.
7. If the realization is disconnected, connect components through deterministic degree-preserving edge swaps.
8. Apply deterministic connected double-edge swaps to reduce Havel-Hakimi structural bias while preserving the final degree sequence.
9. Use the fixed topology seed:
   - `topology_seed(N) = 20260712 + N`
10. Canonically sort nodes and edges before serialization.

A fully connected graph is prohibited.

A fixed degree-3 random-regular rule is not approved because 3-regular graphs cannot exist for odd node counts such as `N = 15` and `N = 25`.

## Experimental reuse policy

- Generate exactly one primary topology for each `N`.
- Reuse that topology across ECHO, HOODIE, ECHO-NoLSTM, and every heuristic baseline.
- Reuse it across task-trace seeds and all main-paper panels involving that `N`.
- Do not vary topology and task traces simultaneously in the main figures.
- Record the topology file hash in every run manifest.

## Required topology artifacts

For every `N` in `{10, 15, 20, 25, 30}`, export:

- adjacency matrix;
- edge list;
- JSON metadata;
- topology visualization;
- SHA-256 hash.

Metadata must include:

- generator name and version;
- source `A20` hash;
- `N`;
- topology seed;
- target and realized degree sequences;
- edge count;
- mean/min/max degree;
- density;
- connected-component count;
- average shortest-path length;
- clustering coefficient;
- generation timestamp.

## Required tests

The implementation must test that every topology is:

- deterministic;
- connected;
- undirected;
- simple;
- loop-free;
- symmetric in adjacency form;
- reproducible from its metadata;
- identical across compared methods;
- unchanged for `N = 20` relative to the approved matrix.

The test suite must also prove that the old fully connected fallback is unreachable for the paper evaluation.

## Sensitivity check

Before finalizing the main Figure 6(d)/(e) interpretation, run a reduced validation-only topology sensitivity check using two additional topology seeds per non-20 `N`.

The main-paper topology remains the fixed primary seed. The sensitivity check is reported separately and must not be used to select a topology that makes ECHO appear stronger.

If the qualitative ECHO conclusions change materially across topology seeds, report topology sensitivity as a limitation and avoid broad topology-independent claims.

## Reporting language

The paper and final report must describe this rule as:

> a deterministic degree-profile-preserving scaling rule anchored to the approved 20-EA topology

Do not state or imply that the HOODIE authors supplied this scalable generator.

## Authorization

This addendum is sufficient authority to unblock implementation and evaluation of Figure 6(d) and Figure 6(e).
