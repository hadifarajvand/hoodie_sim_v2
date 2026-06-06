# Research: Feature 060A

## Decision: audit before repair

Feature 060 appears to generate campaign artifacts through deterministic scalar logic instead of the real Torch/TorchRL trainer. This must be audited before writing a repair so the failure mode is machine-readable and preserved.

## Decision: environment proof is required

The local environment shows both `torch` and `torchrl` are installed. The audit must capture interpreter path and package availability so future claims about missing dependencies are not vague.

## Decision: binding means import plus execution

A real binding is not just having torch installed. Feature 060 must import and execute the real trainer or learner path. If it manually simulates replay/loss/optimizer counts, it is not a real campaign execution.
