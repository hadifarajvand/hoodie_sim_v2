#!/usr/bin/env python3
"""Full, paper-gated validation of official DROO (10 users, 30,000 frames)."""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
import scipy
import scipy.io as sio
import torch

PINNED_COMMIT = "563d6c7723463c3e6b77b470e3200268c5fad4f3"
DATA_BLOB = "2aa853de0c1383d1b1cdb0b749e76b0a9eef993d"
PAPER_TARGET = 0.995


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_line(values, path: Path, ylabel: str, window: int = 1, threshold=None):
    y = pd.Series(values).rolling(window, min_periods=1).mean().to_numpy()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(np.arange(1, len(y) + 1), y)
    if threshold is not None:
        ax.axhline(threshold, linestyle="--", label=f"paper threshold {threshold}")
        ax.legend()
    ax.set_xlabel("Time frame" if window > 1 else "Update")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=.25)
    fig.tight_layout(); fig.savefig(path, dpi=180); plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    repo, out = a.repo.resolve(), a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    np.random.seed(a.seed); torch.manual_seed(a.seed); torch.set_num_threads(min(2, os.cpu_count() or 1))

    commit = git(repo, "rev-parse", "HEAD")
    blob = git(repo, "rev-parse", "HEAD:data/data_10.mat")
    assert commit == PINNED_COMMIT, commit
    assert blob == DATA_BLOB, blob
    data_path = repo / "data/data_10.mat"

    sys.path.insert(0, str(repo))
    from memoryPyTorch import MemoryDNN
    from optimization import bisection

    mat = sio.loadmat(data_path)
    needed = ["input_h", "output_mode", "output_a", "output_tau", "output_obj"]
    assert all(k in mat for k in needed)
    channel_raw = np.asarray(mat["input_h"], float)
    labels = np.asarray(mat["output_mode"], np.int8)
    optimum = np.asarray(mat["output_obj"], float).reshape(-1)
    assert channel_raw.shape == labels.shape == (30000, 10)
    assert optimum.shape == (30000,)
    assert np.isfinite(channel_raw).all() and np.isfinite(optimum).all() and (optimum > 0).all()
    assert np.isin(labels, [0, 1]).all()

    N, n, K, memory_size, Delta = 10, 30000, 10, 1024, 32
    channel = channel_raw * 1_000_000
    split_idx, num_test = 24000, 6000
    mem = MemoryDNN(net=[10, 120, 80, 10], learning_rate=.01, training_interval=10,
                    batch_size=128, memory_size=memory_size)

    rate = np.zeros(n); ratio = np.zeros(n); modes = np.zeros((n, N), np.int8)
    k_index = np.zeros(n, np.int16); k_history = np.zeros(n, np.int16)
    decode_s = np.zeros(n); frame_s = np.zeros(n); violation = np.zeros(n)
    process = psutil.Process(os.getpid()); peak_rss = process.memory_info().rss
    started = time.perf_counter()

    for i in range(n):
        t0 = time.perf_counter()
        if i > 0 and i % Delta == 0:
            max_k = int(np.max(k_index[i-Delta:i-1])) + 1 if Delta > 1 else int(k_index[i-1]) + 1
            K = min(max_k + 1, N)
        idx = i % split_idx if i < 24000 else i - 30000 + num_test + split_idx
        h = channel[idx]
        td = time.perf_counter(); candidates = mem.decode(h, K, "OP"); decode_s[i] = time.perf_counter() - td
        rewards, clean = [], []
        for candidate in candidates:
            m = np.asarray(candidate, np.int8)
            assert m.shape == (N,) and np.isin(m, [0, 1]).all()
            rewards.append(float(bisection(h / 1_000_000, m)[0])); clean.append(m)
        rewards = np.asarray(rewards)
        assert np.isfinite(rewards).all() and (rewards > 0).all()
        winner = int(np.argmax(rewards)); selected = clean[winner]
        selected_reward, allocation_a, tau = bisection(h / 1_000_000, selected)
        tau = np.asarray(tau, float); total_fraction = float(allocation_a + tau.sum())
        assert allocation_a >= -1e-9 and (tau >= -1e-9).all()
        violation[i] = max(0., total_fraction - 1.); assert violation[i] <= .01
        mem.encode(h, selected)
        rate[i] = selected_reward; ratio[i] = rate[i] / optimum[idx]
        modes[i] = selected; k_index[i] = winner; k_history[i] = K
        assert np.isfinite(ratio[i]) and ratio[i] > 0
        frame_s[i] = time.perf_counter() - t0; peak_rss = max(peak_rss, process.memory_info().rss)
        if i % 3000 == 0 or i == n - 1:
            print(f"frame={i+1}/{n} elapsed_s={time.perf_counter()-started:.1f} mean_ratio={ratio[:i+1].mean():.6f} K={K}", flush=True)

    total_s = time.perf_counter() - started
    test = ratio[-num_test:]; test_modes = modes[-num_test:]; paper_modes = labels[split_idx:]
    source_metric = float(np.sum(ratio[-num_test:-1]) / num_test)
    corrected_mean = float(np.mean(test))
    checks = {
        "pinned_commit": commit == PINNED_COMMIT,
        "pinned_dataset_blob": blob == DATA_BLOB,
        "complete_30000_frames": len(ratio) == 30000,
        "all_ratios_finite_positive": bool(np.isfinite(ratio).all() and (ratio > 0).all()),
        "all_actions_binary": bool(np.isin(modes, [0, 1]).all()),
        "adaptive_K_valid": bool(((k_history >= 1) & (k_history <= 10)).all()),
        "allocation_feasible": bool(violation.max() <= .01),
        "training_loss_finite": bool(np.isfinite(np.asarray(mem.cost_his)).all()),
    }
    hard_pass = all(checks.values()); aligned = corrected_mean >= PAPER_TARGET
    status = "PASS" if hard_pass and aligned else ("PARTIAL" if hard_pass else "FAIL")

    metrics = {
        "status": status, "hard_validation_pass": hard_pass, "paper_alignment_pass": aligned,
        "paper_target_min_normalized_rate": PAPER_TARGET,
        "provenance": {"repository":"revenol/DROO", "commit":commit, "dataset_git_blob":blob,
                       "dataset_sha256":sha256(data_path), "dataset_size_bytes":data_path.stat().st_size, "seed":a.seed},
        "configuration": {"users":10,"frames":30000,"training_frames":24000,"testing_frames":6000,
                          "decoder":"OP","network":[10,120,80,10],"memory_size":1024,"adaptive_K_interval":32},
        "normalized_computation_rate": {
            "source_code_exact_metric": source_metric, "corrected_test_mean": corrected_mean,
            "train_mean": float(ratio[:24000].mean()), "test_median":float(np.median(test)),
            "test_p05":float(np.percentile(test,5)), "test_p95":float(np.percentile(test,95)),
            "test_min":float(test.min()), "test_max":float(test.max()),
            "final_1000_mean":float(ratio[-1000:].mean()),
            "fraction_test_at_or_above_0_995":float(np.mean(test >= .995)),
            "fraction_test_at_or_above_0_99":float(np.mean(test >= .99))},
        "decision_agreement_with_cd_labels": {
            "exact_mode_accuracy":float(np.mean(np.all(test_modes == paper_modes, axis=1))),
            "bit_accuracy":float(np.mean(test_modes == paper_modes))},
        "training": {"updates":len(mem.cost_his), "initial_loss":float(mem.cost_his[0]),
                     "final_loss":float(mem.cost_his[-1]), "minimum_loss":float(np.min(mem.cost_his))},
        "runtime": {"total_seconds":total_s,"mean_frame_seconds":float(frame_s.mean()),
                    "p95_frame_seconds":float(np.percentile(frame_s,95)),
                    "mean_decode_seconds":float(decode_s.mean()),
                    "p95_decode_seconds":float(np.percentile(decode_s,95)),"peak_rss_bytes":int(peak_rss)},
        "adaptive_K":{"mean":float(k_history.mean()),"min":int(k_history.min()),"max":int(k_history.max()),"final":int(k_history[-1])},
        "max_allocation_violation":float(violation.max()), "hard_checks":checks,
        "environment":{"python":sys.version,"platform":platform.platform(),"torch":torch.__version__,
                       "numpy":np.__version__,"scipy":scipy.__version__,"pandas":pd.__version__}}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    np.savez_compressed(out / "full_run_arrays.npz", rate=rate, ratio=ratio, modes=modes,
                        k_index=k_index, k_history=k_history, loss=np.asarray(mem.cost_his),
                        decode_seconds=decode_s, frame_seconds=frame_s, violation=violation)
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["metric","value"])
        for key,val in [("status",status),("source_metric",source_metric),("corrected_test_mean",corrected_mean),
                        ("paper_target",PAPER_TARGET),("total_seconds",total_s),("peak_rss_bytes",peak_rss)]: w.writerow([key,val])
    save_line(ratio, out / "normalized_computation_rate.png", "Normalized computation rate", 200, PAPER_TARGET)
    save_line(np.asarray(mem.cost_his), out / "training_loss.png", "Binary cross-entropy loss")
    save_line(k_history, out / "adaptive_K.png", "Candidate count K")
    fig,ax=plt.subplots(figsize=(9,5.5)); ax.hist(test,bins=50); ax.axvline(PAPER_TARGET,linestyle="--",label="paper threshold")
    ax.set_xlabel("Normalized computation rate"); ax.set_ylabel("Test-frame count"); ax.legend(); fig.tight_layout()
    fig.savefig(out / "test_ratio_distribution.png",dpi=180); plt.close(fig)
    report=f"""# DROO Full Paper-Baseline Validation\n\n## Verdict: **{status}**\n\n- Exact official commit: `{commit}`\n- Exact dataset blob: `{blob}`\n- Complete frames: 30,000 (24,000 training + 6,000 testing)\n- Source-code aggregation metric: **{source_metric:.6f}**\n- Corrected complete test mean: **{corrected_mean:.6f}**\n- Paper acceptance threshold: **{PAPER_TARGET:.6f}**\n- Hard checks: **{'PASS' if hard_pass else 'FAIL'}**\n- Paper metric gate: **{'PASS' if aligned else 'FAIL'}**\n- Total runtime: **{total_s/60:.2f} min**\n- Peak RSS: **{peak_rss/1024/1024:.2f} MiB**\n\nThe scientific loop imports the authors' original `MemoryDNN` and `bisection` modules. Only deterministic seeding, headless reporting, assertions, and artifact export were added.\n\n```json\n{json.dumps(checks, indent=2)}\n```\n"""
    (out / "VALIDATION_REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status":status,"corrected_test_mean":corrected_mean},indent=2))
    return 0 if status == "PASS" else 2

if __name__ == "__main__": raise SystemExit(main())
