# Codex Audit Prompt

Use this prompt when re-running an audit of the HOODIE repository against OCR lines 122-747.

---

You are auditing `hadifarajvand/hoodie_sim_v2` on branch `100-hoodie-paper-base`.

Goal:
Audit the repository against the HOODIE paper System Model and HOODIE modelling sections in `resources/papers/hoodie/ocr/merged.md` lines 122-747.

Rules:
- Do not modify simulator code.
- Do not invent mechanisms.
- Do not call anything paper-faithful unless the paper contract is actually satisfied.
- Be ruthless. If a feature is proxy behavior, say so.

Primary references:
- `resources/papers/hoodie/ocr/merged.md`
- `specs/100-hoodie-paper-faithful-baseline/spec.md`
- `specs/100-hoodie-paper-faithful-baseline/checklists/system-model-ocr-122-747/system-model-checklist.md`

Audit targets:
- System architecture
- Task characteristics
- Offloading decision model
- Private queue model
- Offloading queue model
- Public queue model
- Historical load levels
- DRL state space
- DRL action space
- Reward / cost function
- Optimization problem
- HOODIE model
- LSTM forecasting
- HOODIE training algorithm
- Inference phase
- Complexity / convergence
- Pub-sub communication and recovery
- Table 4 parameters

For each item:
1. locate the repository evidence
2. compare it to the paper
3. state `COMPLETE`, `PARTIAL`, `MISSING`, `UNCLEAR`, or `NOT_APPLICABLE_YET`
4. name the concrete gap
5. recommend the next phase or repair

Explicitly flag these known gaps if they remain true:
- `state_dim=2`
- `action_count=5`
- LSTM not fully integrated into the paper state pipeline
- reward reconstructed from traces rather than natively delayed
- 5000-episode training not yet performed
- 200-episode validation not yet paper-grade
- pub-sub / recovery not convincingly simulated
- baseline proxies are not paper-perfect reimplementations

Output format:
- concise markdown table for the checklist
- a blunt gap summary
- an implementation-readiness matrix
- no claims of paper-faithful completion unless the evidence is airtight

