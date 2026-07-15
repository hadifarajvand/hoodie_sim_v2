# Prompt — Continue HOODIE After Observation and DDQN Milestone

The second implementation milestone already exists locally:

- Commit: `2cac377`
- Message: `HOODIE: add observation and DDQN learner`
- Focused tests: `python -m pytest tests/test_ddqn.py tests/test_hoodie_kernel.py tests/test_phase1.py`
- Result: `15 passed`

Preserve commits `0d5fa65` and `2cac377` exactly. Do not reset, squash away, or abandon them.

Remote authentication remains unavailable:

- `gh auth status` reports an invalid keyring token;
- `ssh -T git@github.com` cannot resolve the GitHub hostname.

This is not an implementation blocker. Continue locally and retry authentication only after the next milestone or when network resolution returns.

## 1. Next milestone

Implement, test, and commit:

```text
HOODIE: implement delayed reward distributed training and policies
```

This milestone must include the following.

## 2. Source-backed delayed reward

Before coding, resolve and record in a typed source contract:

- reward equation;
- whether the learner maximizes reward or minimizes cost;
- completion reward or delay cost sign;
- drop and timeout penalty;
- action/offloading cost terms;
- normalization and clipping, when present;
- exact slot/event at which reward becomes observable;
- ownership of a delayed reward when execution completes at another node;
- terminal transition semantics;
- discounting across delayed completion;
- treatment of unfinished tasks at episode end.

Use this authority order:

1. original HOODIE PDF;
2. OCR checked against the PDF;
3. recovered parameter and approved-assumption registries;
4. existing paper-mechanism audits and focused tests;
5. the narrowest explicit implementation assumption.

Do not reintroduce ECHO lateness, ERT, risk, deadline-mask, or event-SMDP reward terms. Do not fabricate values from plotted paper curves.

Create a reward API that is independent of the DDQN network and physical kernel. It must consume typed task/decision/outcome records and return typed reward records with provenance.

## 3. Transition assembly and ownership

Implement:

- pending decision records keyed by task and owning agent;
- exact pairing of observation, action, delayed reward, next observation, terminal flag, and legal next-action mask;
- one transition emitted exactly once per resolved decision;
- timeout/drop transitions;
- episode-end handling for unresolved work;
- deterministic transition ordering;
- transition provenance linking task, trace, agent, decision slot, completion/drop slot, and reward contract hash;
- invariant checks preventing duplicate, missing, or cross-agent transitions.

The physical kernel must remain learning-independent.

## 4. Distributed HOODIE training

Implement the learner ownership model established by the source contract.

At minimum provide:

- one learner state per edge agent when the paper requires independent learners;
- independent replay, optimizer, epsilon, target network, and checkpoint state per learner;
- deterministic seed derivation per run, episode, agent, and component;
- a coordinator that advances the common environment without becoming a second learner;
- training and evaluation modes;
- checkpoint/resume for the entire distributed learner set;
- aggregate and per-agent metrics;
- no hidden single global HOODIE learner unless the source contract explicitly requires it.

Add a deterministic multi-agent training smoke test proving that at least two agents receive and learn from distinct owned transitions.

## 5. Common policy interface

Create one typed policy port used by HOODIE and every baseline. It must expose equivalent access to:

- current observation;
- legal action mask;
- topology and destination identifiers allowed by the observation contract;
- deterministic RNG where required;
- evaluation/training mode;
- action plus policy-decision metadata.

No baseline may bypass the neutral kernel, inject task outcomes, alter arrivals, inspect future trace entries, or use privileged information unavailable under its defined method.

## 6. Implement the six article baselines

Implement and source-document:

- FLC;
- RO;
- HO;
- VO;
- BCO;
- MLEO.

For each baseline:

- identify the paper definition and any explicit parameters;
- use the common action vocabulary;
- respect topology and legal masks;
- handle no-valid-horizontal-destination cases deterministically;
- expose a stable policy name and configuration schema;
- produce decision records through the same instrumentation path as HOODIE;
- add deterministic policy-contract tests.

Do not implement `ADAPTIVE` as a HOODIE alias. Do not silently substitute a heuristic for trained HOODIE.

## 7. Paired evaluation foundation

Add the first paired evaluation layer:

- immutable trace reuse across compared policies;
- identical exogenous task IDs and attributes;
- identical topology and physical configuration;
- task-level outcome records;
- delay, drop ratio, completion count, and action-distribution metrics;
- equality checks for offered task counts and trace hashes;
- deterministic aggregation for a fixed seed set.

Full figure sweeps come later, but the evaluation API must already support all seven policies on the same traces.

## 8. Required tests

Add focused tests covering:

1. reward sign and formula fixtures;
2. completion, timeout, and drop reward timing;
3. exactly-once delayed transition emission;
4. transition ownership by agent;
5. no duplicate transitions after resume;
6. distributed learner state independence;
7. distributed checkpoint round-trip;
8. all six baseline policy contracts;
9. legal action enforcement for all policies;
10. paired trace/task equality across policies;
11. deterministic evaluation metrics;
12. zero imports from ECHO modules in the new milestone code.

Run the existing focused tests as regression coverage in addition to the new tests.

## 9. Commit and continuation

Commit locally even when remote access remains unavailable.

Required milestone message:

```text
HOODIE: implement delayed reward distributed training and policies
```

After committing, continue automatically with:

1. complete paired evaluation and fairness validation;
2. full removal of ECHO, ERT, ECHO masks, ECHO rewards, and event-SMDP behavior from active paths;
3. experiment DAG and reproducibility layer;
4. Figures 8–11 dataset generation and rendering;
5. full campaign and final verification.

Do not stop after implementing only one or two baselines. Do not return an inventory or Phase 0 report.

## 10. Authentication retry

After the local milestone is committed, perform one bounded retry.

Because DNS resolution failed, first check network resolution without exposing credentials:

```bash
python - <<'PY'
import socket
for host in ("github.com", "api.github.com"):
    try:
        print(host, socket.getaddrinfo(host, 443)[0][4][0])
    except Exception as exc:
        print(host, "UNRESOLVED", repr(exc))
PY
```

When GitHub resolves and interactive login is possible, repair the invalid GitHub CLI session through browser authentication:

```bash
gh auth logout -h github.com
gh auth login -h github.com -p https --web
gh auth setup-git
git remote set-url origin https://github.com/hadifarajvand/hoodie_sim_v2.git
git fetch origin --prune
BRANCH="$(git branch --show-current)"
git push -u origin "$BRANCH"
```

Do not perform `gh auth logout` unless an interactive re-login can be completed in the same session. Do not request, print, or store a token. Never force-push and never push to `main`.

## 11. Output rule

Continue local engineering while authentication is unavailable. Return only after the complete HOODIE implementation and Figures 8–11 campaign finish, or after a genuine blocker prevents further local implementation.
