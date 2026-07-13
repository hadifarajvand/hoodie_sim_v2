# ECHO Scalable Topology Construction Authorization — Revision 2

## Status

**Author-approved methodological addendum**

This document **supersedes** the earlier `research/ECHO_topology_authorization.md`.

The earlier addendum incorrectly required the approved 20-EA anchor topology to be connected. The repository evidence shows that the approved matrix is intentionally disconnected and follows a deterministic five-cluster pattern. The connectivity precondition and connected-graph requirement are therefore withdrawn.

## Authoritative anchor

Let `A20` be the exact approved 20-EA adjacency matrix currently stored in the repository.

For `N = 20`:

- use `A20` unchanged;
- preserve its exact hash;
- generate Figure 4 directly from it;
- display all disconnected components honestly;
- do not add bridging edges;
- do not relabel it as connected.

## Approved scalable rule

For every `N` in `{10, 15, 20, 25, 30}`, number EAs from `1` to `N`.

Because every approved `N` is divisible by five, partition the EAs into five deterministic clusters according to their residue class modulo five:

\[
C_r(N)=\{\,i\in\{1,\ldots,N\}\mid ((i-1)\bmod 5)=r\,\},
\qquad r\in\{0,1,2,3,4\}.
\]

Create an undirected edge between two distinct EAs if and only if they belong to the same cluster:

\[
G_N(i,j)=
\begin{cases}
1, & i\neq j \text{ and } ((i-1)\bmod 5)=((j-1)\bmod 5),\\
0, & \text{otherwise}.
\end{cases}
\]

Therefore, the topology for each `N` is the disjoint union of five complete subgraphs:

\[
G_N = 5K_{N/5}.
\]

This is the approved interpretation of “preserving the same connectivity-generation rule.”

## Expected properties

For each approved `N`:

- number of connected components: `5`;
- size of each component: `N / 5`;
- degree of every node: `(N / 5) - 1`;
- number of edges:
  `5 * ((N/5) * ((N/5)-1) / 2)`;
- no self-loops;
- no inter-cluster horizontal links;
- symmetric binary adjacency;
- deterministic generation with no random seed.

Expected values:

| N | Component structure | Degree per EA | Total edges |
|---:|---|---:|---:|
| 10 | 5 × K2 | 1 | 5 |
| 15 | 5 × K3 | 2 | 15 |
| 20 | 5 × K4 | 3 | 30 |
| 25 | 5 × K5 | 4 | 50 |
| 30 | 5 × K6 | 5 | 75 |

## Required validation against the repository anchor

Before using this rule, verify that the stored `A20` exactly satisfies:

```text
A20[i,j] = 1
iff
i != j and ((i-1) mod 5) == ((j-1) mod 5)
```

using the repository's node-index convention.

The validation must compare every matrix entry, not only node degrees or a small sample.

If the exact comparison passes:

- record the `A20` hash;
- record that the modular five-cluster rule reproduces it exactly;
- proceed without further topology approval.

If the exact comparison fails:

- stop only the topology-dependent experiments;
- report the precise mismatching entries;
- do not silently repair the matrix.

## Experimental reuse policy

For each `N`, generate one deterministic topology and reuse it across:

- ECHO;
- ECHO-NoLSTM;
- HOODIE;
- Random Offloader;
- Full Local Computing;
- Vertical Offloader;
- Horizontal Offloader;
- Balanced Cyclic Offloader;
- Minimum Latency Estimation Offloader;
- every seed;
- every relevant Figure 6 panel.

The adjacency hash must be stored in every run manifest.

## Required topology artifacts

For every `N` in `{10, 15, 20, 25, 30}`, export:

- adjacency matrix CSV;
- canonical edge-list CSV;
- JSON metadata;
- SVG visualization;
- 300-dpi PNG visualization;
- SHA-256 hash.

Metadata must include:

- generator name: `modular-five-cluster-v1`;
- `N`;
- formula used;
- component count;
- component memberships;
- component sizes;
- node degree sequence;
- edge count;
- density;
- adjacency hash;
- source `A20` hash;
- exact-anchor-match status for `N=20`.

## Required tests

Tests must prove:

1. deterministic generation;
2. symmetric binary adjacency;
3. no self-loops;
4. exactly five connected components;
5. every component has size `N/5`;
6. every component is complete;
7. no edge exists between components;
8. every node has degree `(N/5)-1`;
9. total edge count matches the table above;
10. generated `N=20` adjacency exactly equals approved `A20`;
11. all methods use the same topology hash for a given `N`;
12. the old fully connected fallback is unreachable in paper evaluation.

The previous test requiring graph connectedness must be removed or replaced because it contradicts the approved anchor.

## Scientific reporting requirement

The paper and final report must state:

> The edge topology was generated using a deterministic five-cluster modular rule anchored to the approved 20-EA adjacency matrix. For each tested system size, EAs were divided into five equal disconnected edge clusters, with full horizontal connectivity inside each cluster and no horizontal links across clusters. Vertical cloud offloading remained available to every EA.

Do not describe the edge graph as connected.

Do not imply that EAs in different clusters can horizontally offload to one another.

## Interpretation limitation

Increasing `N` increases each cluster size and therefore increases horizontal degree from `1` at `N=10` to `5` at `N=30`.

Consequently, Figure 6(d) and Figure 6(e) measure scalability under the approved topology family, not under constant-degree topology scaling.

This limitation must be disclosed in the final report and must not be hidden when interpreting scalability.

## Authorization

This revision resolves the topology contradiction and authorizes implementation of Figure 4, Figure 6(d), and Figure 6(e).

It supersedes every connectedness requirement in the previous topology addendum.
