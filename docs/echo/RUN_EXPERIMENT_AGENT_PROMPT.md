# Bounded trained-pilot execution prompt

Copy everything below into the execution agent **after pulling the clean validated `main` branch and running `scripts/echo/bootstrap_main.sh`**.

---

You are the execution agent for the ECHO bounded trained-pilot run.

Read and obey:

1. `AGENTS.md`
2. `README.md`
3. `docs/echo/TRAINED_PILOT_AGENT_PROMPT.md`
4. this prompt, which overrides conflicting reporting, blocker, recovery, and campaign-location instructions in earlier documents.

## Fixed scope

Use only:

```text
Repository: hadifarajvand/hoodie_sim_v2
Branch: main
Checkout: /Users/hadi/Documents/GitHub/hoodie_sim_v2
External application root: /Volumes/ADATA-1TB-External/echo_outputs
```

Never create a second repository, clone, branch, worktree, fork, mirror, or remote. Never switch away from `main`. Never force-push. Never write runtime output into Git.

Never access, inspect, resume, modify, move, rename, or delete any path containing:

```text
figures-8-11-7587c7c6382c
```

Do not start the paper-scale 10-seed × 200-held-out-episode campaign. This task ends with the bounded trained pilot and its verified external archive.

## Start gate

Before any experiment process:

- verify the repository using `scripts/echo/verify_single_repository.sh`;
- require a clean `main` worktree;
- fetch `origin/main`;
- require local `HEAD` and `origin/main` to match;
- run `scripts/echo/bootstrap_main.sh`;
- use the installed `hoodie-experiments` entrypoint;
- verify all required `echo-*` help commands;
- record the exact starting SHA.

Do not reinterpret a clean validated checkout as a request to redesign the CLI. Repair source only after a real installed-CLI command exposes a concrete defect.

## Campaign creation is already authorized

Create exactly one new, unique bounded campaign. Do not look for or reuse the historical missing path `figures-8-11-trial`. Do not ask the user to provide a campaign directory. Do not ask for authorization to create the bounded campaign.

Use a unique campaign ID beginning with:

```text
echo-trained-pilot-
```

Resolve it through the canonical external layout under:

```text
/Volumes/ADATA-1TB-External/echo_outputs/campaigns/<campaign-id>
```

Persist the selected campaign ID and absolute campaign root before training. Every later stage must use that same campaign and manifest.

## Blocker policy

A missing campaign, missing checkpoint, bad manifest, parser error, Python exception, failed test, aggregation failure, rendering failure, verification failure, incompatible checkpoint, or learner/runtime defect is **not** an external blocker. Diagnose it, repair it, rerun the same real CLI command, and continue.

`EXTERNAL_BLOCKER` is permitted only for direct operating-system or credential evidence of one of:

- external volume not mounted;
- `Permission denied`;
- `Read-only file system`;
- `No space left on device`;
- `Input/output error`;
- Git authentication or push rejection that cannot be repaired locally.

`FileNotFoundError` is never a storage blocker.

Do not ask for permission to continue after ordinary code or campaign failures.

## Execution and recovery guardrails

- Run one foreground experiment process at a time.
- Record the exact command, PID, stdout, stderr, start time, exit code, source SHA, and campaign root externally.
- Before launching a command, prove no prior command for that stage is still active by checking only its exact recorded PID.
- Resume the one campaign after interruption; do not create a duplicate.
- Never use `kill`, `killall`, `pkill`, negative PID signals, process-group signals, or broad process matching.
- Never launch a second run merely because output is temporarily quiet.
- Normal failures must not leave completed markers.
- Do not use projected, placeholder, fabricated, or synthetic learner results.

## Required bounded sequence

Execute the detailed scientific requirements in `TRAINED_PILOT_AGENT_PROMPT.md`, in this order:

1. bounded real learner-backed training;
2. disjoint held-out evaluation in a new process;
3. checkpoint save/load round-trip with mismatch count `0`;
4. fixed-trace HOODIE versus explicitly ECHO-disabled differential with mismatch count `0`;
5. invalid-input and trace-separation probes with expected nonzero exits;
6. bounded trained pilot for `HOODIE`, `ECHO`, and `ECHO-NoLSTM`, seeds `101`, `202`, `303`, moderate and high-tight scenarios;
7. external aggregation;
8. verification;
9. PDF, SVG, and 300-dpi PNG rendering;
10. sealed bundle and ZIP archive;
11. SHA-256 verification;
12. final `hoodie-experiments echo-verify-run` success.

Label all results:

```text
TRAINED PILOT — NOT PAPER EVIDENCE
```

No acceptance rule requires ECHO to outperform HOODIE.

## Source repairs during execution

When a real command reveals a code defect:

1. capture the complete traceback and exact command;
2. make the smallest coherent repair on `main`;
3. add focused regression coverage for the observed defect;
4. rerun the same installed CLI command;
5. run compile, focused tests, deterministic smoke, and non-long tests relevant to the change;
6. inspect `git diff --check` and staged files;
7. commit source/test/docs only;
8. push normally to `origin/main`;
9. require a clean matching local/remote SHA before continuing the decisive run.

Never commit generated campaign output.

## Reporting policy

Do not send repetitive `in progress`, `next step`, `still broken`, authorization, or missing-campaign messages. Continue autonomously through ordinary failures.

Useful milestone updates are allowed only when they contain new execution evidence such as a completed stage, checkpoint hash, mismatch result, pilot seed completion, figure export, or archive verification.

The final response must include:

- final pushed `main` SHA;
- absolute campaign root;
- exact commands and exit codes;
- log paths;
- training and held-out trace hashes and separation proof;
- replay/loss/checkpoint evidence;
- checkpoint round-trip mismatch count `0`;
- ECHO-disabled mismatch count `0`;
- invalid-probe results;
- trained-pilot seed metrics and paired differences;
- task-conservation proof;
- figure paths;
- sealed bundle and archive paths and SHA-256 values;
- confirmation that runtime output stayed outside Git;
- confirmation that no projected values were used;
- confirmation that paper-scale execution was not started;
- confirmation that the protected legacy campaign was untouched;
- confirmation that no process was killed.

Begin with the start gate, create the one authorized unique campaign, and execute the bounded sequence end to end.
