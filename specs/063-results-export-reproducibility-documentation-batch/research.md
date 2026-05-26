# Research: Feature 063

## Decision: export and document only

Feature 063 packages already-produced evidence. It must not rerun training, mutate prior experiment outputs, or inflate claims.

## Decision: source-backed claims only

Every exported table row, figure-data entry, and documentation statement must map to a committed source artifact. Unsupported claims must be labeled unsupported instead of omitted or implied.

## Decision: controlled experiment language

All results must be described as controlled experiment data from the implemented simulator pipeline. Paper reproduction, production performance, and superiority claims are forbidden unless a later release gate explicitly approves them.

## Decision: reproducibility before polish

The reproducibility package must prioritize exact commands, artifact paths, seed sets, trace-bank IDs, branch/tag assumptions, and limitations over narrative polish.
