# Paper Distributed-Agent Audit

Source: resources/papers/hoodie/ocr/merged.txt

| item | status | evidence |
|---|---|---|
| each EA runs its own DRL model (per-EA distributed agents) | exact | OCR lines 138, 401, 405: 'each EA runs a DRL model'; 'each EA acts as a DRL agent' |
| per-EA model parameters theta_n | exact | OCR Table 2: theta_n = Q-model parameters of DRL agent n |
| per-EA target model theta_hat_n | exact | OCR line 587 + Table 2: target theta_hat_n; 'every N_copy training episodes' |
| Algorithm 1 is single-agent training, replicated per EA | exact | OCR line 587: 'pseudocode for training a single-agent model'; line 591 'in EA n' |
| agents do not share decisions / autonomy | exact | OCR lines 99, 109: 'each HOODIE agent does not require knowledge on the decisions made by other agents' |
| per-EA experience replay | inferred | OCR line 587/Table 4: N_R=10000; Algorithm 1 framed per EA n |
| N_EA = 20, N_E = 5000 | exact | OCR Table 4: N=20, N_E=5000 |
| shared optimizer vs per-agent optimizer | inferred | Table 4 lists Adam/lr; per-agent optimizer inferred from per-agent models |
| evaluation routing to per-EA models | approximated | OCR line 694: 'deploying distributed HOODIE models (only the Q-models) at each of the N EA sites' |

All core per-EA items exact: True
Remaining approximations/inferred: ['per-EA experience replay', 'shared optimizer vs per-agent optimizer', 'evaluation routing to per-EA models']
No proposed method: True