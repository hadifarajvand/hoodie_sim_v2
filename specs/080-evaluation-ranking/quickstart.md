# Quickstart for Feature 080 — HOODIE Proposed Method Implementation

## Setup

1. Clone repo and checkout branch `080-hoodie-proposed-method-spec-repair`.
2. Activate Python environment: `src/.venvmac/bin/python`.
3. Install dependencies: `pip install -r requirements.txt`.

## Running Feature 080

- Unit tests: `python -m unittest discover tests/unit -p 'test_hoodie_proposed_method_*.py'`
- Integration tests: `python -m unittest discover tests/integration -p 'test_hoodie_proposed_method_*.py'`

## Notes
- Epsilon-greedy schedule, replay memory, and LSTM are all stubbed for initial testing.
- Do not run any thesis/DCQ code.