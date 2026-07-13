# ECHO Compute Plan

- selected device: `cpu`
- learner wall time: `1.357936143875122s`
- training episode steps/s: derived from 4 steps over 1.3579s (tiny smoke)
- optimizer updates: `4` then `8` after resume
- replay size: `4`
- checkpoint size: `artifacts/checkpoints/echo_smoke/echo_smoke_checkpoint.pt`
- training jobs: `1` smoke + `1` resume
- evaluation jobs: `2` pilot evals
- projected CPU-hours: tiny smoke only, negligible
- projected CUDA-hours: `0`
- resume command: `python -m pytest` not used; manual checkpoint load via `torch.load(..., map_location=device)`
