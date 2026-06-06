# Implementation Readiness Matrix

| Paper mechanism | Current status | Blocking severity | Blocks Phase 4 smoke? | Blocks full Phase 4? | Blocks Figure 8? | Blocks Figure 9? | Blocks Figure 10? | Blocks Figure 11? | Recommended phase |
|---|---|---:|---|---|---|---|---|---|---|
| Runtime slot phases | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 0 / Phase 1 |
| Bernoulli arrivals | COMPLETE | Low | No | No | No | No | No | No | Already covered |
| Task lifecycle tracing | COMPLETE | Low | No | No | No | No | No | No | Already covered |
| Private queue semantics | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 2 |
| Offloading queue semantics | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 2 |
| Public queue equal sharing | COMPLETE | Medium | No | No | No | No | No | No | Already covered |
| Public queue active-set audit | PARTIAL | Medium | No | Yes | Yes | Yes | Yes | Yes | Phase 2 / Phase 3 |
| Historical load matrix | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 3 |
| LSTM forecast pipeline | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 3 |
| Paper state vector | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 3 / Phase 4 |
| Paper action space | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 2 / Phase 4 |
| Delayed reward attribution | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 2 |
| Adjacency legality contract | PARTIAL | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 2 |
| Baseline policy registry | PARTIAL | Medium | No | Yes | Yes | Yes | Yes | Yes | Phase 2 |
| Trace-derived training | PARTIAL | Medium | No | Yes | Yes | Yes | Yes | Yes | Phase 3 |
| 200-episode validation | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 4 |
| Figure 8 workflow | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 5 |
| Figure 9 workflow | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 5 |
| Figure 10 workflow | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 5 |
| Figure 11 workflow | MISSING | High | Yes | Yes | Yes | Yes | Yes | Yes | Phase 5 |
| Pub-sub / recovery simulation | UNCLEAR | Medium | Yes | Yes | Yes | Yes | Yes | Yes | Phase 3 / Phase 4 |

