# HOODIE Reproduction Pipeline

Canonical reproduction entry point:

```bash
python3 scripts/run_hoodie_reproduction_pipeline.py \
  --config configs/hoodie_reproduction.json \
  --output-dir artifacts/hoodie_reproduction/hoodie_reproduction
```

Scope:
- baseline FIFO and deterministic heuristic routing only
- no DRL, LSTM, or learning-based optimization
- paper-faithful runtime mode uses deterministic seeds and explicit provenance

Non-canonical paths:
- legacy training wrappers under `training/`
- experimental wrappers under `evaluation/experimental_layers.py`
- placeholder aliases that do not trace back to the paper runtime
