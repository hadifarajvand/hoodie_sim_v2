# Quickstart: Task Execution Time & Compute Resource Modeling

## 1. Define compute capacity settings

Choose deterministic per-slot capacities for local, edge, and cloud execution. The repository uses an explicit capacity fixture because the OCR-backed paper text does not fully recover exact slot-level capacity values.

## 2. Generate a task with known compute budget

Use an existing traffic trace or a handcrafted task and verify that required compute budget is derived from task size and processing density.

## 3. Advance execution through the existing environment boundary

Run the task through the existing `HoodieGymEnvironment` loop and confirm the remaining compute budget decreases slot by slot until completion or drop.

## 4. Inspect the terminal outcome

Verify that reward appears only after the task is complete or dropped and that the task is removed from active execution at terminal resolution.

## No dependency change required

This feature does not require Gymnasium, ns-3, ns-3-gym, or any new package. It uses the repository’s existing Python stack and deterministic compute configuration only.
