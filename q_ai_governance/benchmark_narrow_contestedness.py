"""
benchmark_narrow_contestedness.py — can anything rank DAO proposals by how
contested they will be, under the narrow band locked in
PREREGISTRATION_narrow_contestedness.md?

    contested  <=>  final YES share in [0.40, 0.60]

This is a much harder question than the [0.05, 0.95] band used by
CONTESTEDNESS.md, and deliberately so: [0.05, 0.95] admits a 6%-YES landslide as
"contested", while [0.40, 0.60] means the vote was genuinely close. The cost is
prevalence — roughly 3% of proposals rather than 26%.

Everything here is fixed by the pre-registration: the band, the filters, the
temporal split on proposal END date, the seed, the score functions, the
baselines, the metrics, and the success criterion. Nothing is chosen after
seeing a result.

    python3 q_ai_governance/benchmark_narrow_contestedness.py

Writes data/benchmark_narrow_contestedness_results.json. Every number in
NARROW_CONTESTEDNESS.md traces to that file.
"""

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q_ai_governance.quantum_agent import QuantumOrchORAgent  # noqa: E402

# ---- locked by the pre-registration -----------------------------------------
CONTESTED_LO, CONTESTED_HI = 40.0, 60.0     # YES share, percent. LOCKED.
MIN_VOTERS = 100                            # turnout filter
MIN_USABLE_N = 150                          # below this: report and stop
TEST_FRAC = 0.30                            # temporal, on END date
SEED = 20260904
N_ROLLOUTS = 50
N_WEIGHT_SEEDS = 10
N_BOOTSTRAP = 2000
NUM_QUBITS = 4

DAOS = ["Uniswap", "Arbitrum", "Optimism", "Gitcoin", "Aave"]

FEATURE_NAMES = (
    [f"dao_{d.lower()}" for d in DAOS]
    + ["log_body_len", "title_len_100", "duration_days", "n_choices",
       "has_quorum", "has_abstain", "prior_dao_yes", "log_prior_dao_n",
       "prior_dao_contested", "log_prior_dao_contested_n"]
)

YES_LIKE = {"for", "yes", "approve", "approve funding", "accept"}
NO_LIKE = {"against", "no", "reject", "reject funding", "deny"}


# ---- data -------------------------------------------------------------------
def is_binary_ish(p):
    """For/Against (+ optional Abstain). YES share is undefined otherwise."""
    if not (2 <= len(p["choices"]) <= 3):
        return False
    low = [c.strip().lower() for c in p["choices"]]
    return any(c in YES_LIKE for c in low) and any(c in NO_LIKE for c in low)


def load_and_filter(path):
    payload = json.load(open(path))
    props = payload["proposals"]
    kept, drop = [], {"not_binary_ish": 0, "low_turnout": 0, "no_tally": 0}
    for p in props:
        if not p.get("scores_total"):
            drop["no_tally"] += 1
        elif not is_binary_ish(p):
            drop["not_binary_ish"] += 1
        elif p["voter_count"] < MIN_VOTERS:
            drop["low_turnout"] += 1
        else:
            kept.append(p)
    return payload, kept, drop


def build_features(props):
    """Sort by END date and build strictly past-only features.

    End-order matters: a proposal that ended earlier has a settled tally, so
    using it in an expanding prior is legitimate. Sorting by creation date
    would let a long-running proposal contribute a prior before its own tally
    existed.
    """
    rows = sorted(props, key=lambda p: p["end"])
    yes_hist = {d: [] for d in DAOS}
    con_hist = {d: [] for d in DAOS}
    X, y, meta = [], [], []

    for p in rows:
        dao = p["dao"]
        yh, ch = yes_hist[dao], con_hist[dao]
        prior_yes = sum(yh) / len(yh) if yh else 84.0
        prior_con = sum(ch) / len(ch) if ch else 0.03
        dur_days = max(0.0, (p["end"] - p["start"]) / 86400.0)

        X.append([1.0 if dao == d else 0.0 for d in DAOS] + [
            math.log1p(p["body_len"]),
            len(p["title"]) / 100.0,
            dur_days,
            float(len(p["choices"])),
            1.0 if p["quorum"] else 0.0,
            1.0 if len(p["choices"]) > 2 else 0.0,
            prior_yes / 100.0,
            math.log1p(len(yh)),
            prior_con,
            math.log1p(len(ch)),
        ])
        yes_pct = 100.0 * p["yes_vp"] / p["scores_total"]
        label = 1.0 if CONTESTED_LO <= yes_pct <= CONTESTED_HI else 0.0
        y.append(label)
        meta.append(p)
        yh.append(yes_pct)
        ch.append(label)

    return np.array(X, dtype=float), np.array(y, dtype=float), meta


# ---- metrics ----------------------------------------------------------------
def auc(y_true, scores):
    """Mann-Whitney U / rank AUC, ties get average ranks. Null is 0.5."""
    y_true = np.asarray(y_true, dtype=bool)
    n_pos, n_neg = int(y_true.sum()), int((~y_true).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    s = np.asarray(scores, dtype=float)
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    ranks[order] = np.arange(1, len(s) + 1)
    ss = s[order]
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return float((ranks[y_true].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def average_precision(y_true, scores):
    """PR-AUC. Its null baseline is the POSITIVE PREVALENCE, not 0.5.

    Tied scores are resolved at the END of their tied block. Without this a
    constant scorer would inherit the array's own ordering and report whatever
    the data happened to be sorted by -- here, time -- instead of prevalence.
    """
    y = np.asarray(y_true, dtype=float)
    if y.sum() == 0:
        return float("nan")
    s = np.asarray(scores, dtype=float)
    order = np.argsort(-s, kind="mergesort")
    y, ss = y[order], s[order]
    tp = np.cumsum(y)
    k = np.arange(1, len(y) + 1)
    # last index of each tied block, so every tie shares one precision value
    block_end = np.arange(len(y))
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        block_end[i:j + 1] = j
        i = j + 1
    precision = tp[block_end] / k[block_end]
    return float((precision * y).sum() / y.sum())


def bootstrap_auc_ci(y, score_fn, rng, n_boot=N_BOOTSTRAP):
    """Percentile CI by resampling TEST ROWS. score_fn(idx) -> scores for idx."""
    n = len(y)
    out = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y[idx].sum() == 0 or y[idx].sum() == len(idx):
            continue
        a = auc(y[idx], score_fn(idx))
        if not math.isnan(a):
            out.append(a)
    if not out:
        return {"lo": float("nan"), "hi": float("nan"),
                "p_le_half": float("nan"), "n_valid": 0}
    arr = np.array(out)
    return {
        "lo": float(np.percentile(arr, 2.5)),
        "hi": float(np.percentile(arr, 97.5)),
        "p_le_half": float(np.mean(arr <= 0.5)),
        "n_valid": int(len(arr)),
    }


# ---- classical baseline -----------------------------------------------------
def fit_logistic(X, y, l2=1.0, iters=200):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = np.hstack([(X - mu) / sd, np.ones((len(X), 1))])
    w = np.zeros(Z.shape[1])
    ridge = l2 * np.eye(Z.shape[1])
    ridge[-1, -1] = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-Z @ w))
        grad = Z.T @ (p - y) + ridge @ w
        s = np.clip(p * (1 - p), 1e-9, None)
        H = Z.T @ (Z * s[:, None]) + ridge
        step = np.linalg.solve(H, grad)
        w -= step
        if np.max(np.abs(step)) < 1e-10:
            break
    return {"w": w, "mu": mu, "sd": sd}


def predict_logistic(m, X):
    Z = np.hstack([(X - m["mu"]) / m["sd"], np.ones((len(X), 1))])
    return 1.0 / (1.0 + np.exp(-Z @ m["w"]))


# ---- quantum score functions ------------------------------------------------
def quantum_scores(Xte_std, weight_seed, n_rollouts=N_ROLLOUTS, verbose=False):
    """Run the engine on each test row; return the three pre-registered scores.

    (a) point   : 1 - 2*|yes_frac - 0.5|, yes_frac = share of even collapse idx
    (b) disperse: Shannon entropy of the collapsed-index distribution
    (c) coherence: coherence_at_collapse (deterministic given the observation)
    """
    np.random.seed(weight_seed)
    agent = QuantumOrchORAgent(num_qubits=NUM_QUBITS, state_dim=Xte_std.shape[1])
    n_states = 2 ** NUM_QUBITS
    point, disp, coh = [], [], []

    for r, obs in enumerate(Xte_std):
        o = np.asarray(obs, dtype=np.float32)
        counts = np.zeros(n_states, dtype=float)
        c_last = 1.0
        for _ in range(n_rollouts):
            idx, _, c, _, _ = agent.deliberate_and_act(o)
            counts[idx] += 1.0
            c_last = c
        yes_frac = counts[0::2].sum() / n_rollouts
        p = counts / counts.sum()
        nz = p[p > 0]
        point.append(1.0 - 2.0 * abs(yes_frac - 0.5))
        disp.append(float(-(nz * np.log(nz)).sum()))
        coh.append(float(c_last))
        if verbose and (r + 1) % 25 == 0:
            print(f"    seed {weight_seed}: {r + 1}/{len(Xte_std)} rows", flush=True)

    return {"quantum_point": np.array(point),
            "quantum_dispersion": np.array(disp),
            "quantum_coherence": np.array(coh)}


# ---- main -------------------------------------------------------------------
def run(data_path, out_path, n_weight_seeds=N_WEIGHT_SEEDS, n_rollouts=N_ROLLOUTS):
    payload, kept, drop = load_and_filter(data_path)
    print(f"dataset : {data_path}")
    print(f"fetched : {payload['fetched_at']}")
    print(f"kept    : {len(kept)} of {len(payload['proposals'])}  dropped: {drop}")

    if len(kept) < MIN_USABLE_N:
        print(f"\nSTOP: {len(kept)} usable proposals < pre-registered minimum "
              f"{MIN_USABLE_N}. No point estimate is reported.")
        json.dump({"status": "STOPPED_INSUFFICIENT_DATA", "n_usable": len(kept),
                   "min_usable_n": MIN_USABLE_N},
                  open(out_path, "w"), indent=2)
        return None

    X, y, meta = build_features(kept)
    cut = int(len(y) * (1 - TEST_FRAC))
    Xtr, ytr, Xte, yte = X[:cut], y[:cut], X[cut:], y[cut:]
    split_end = meta[cut]["end"]

    n_con_te = int(yte.sum())
    prevalence_te = float(yte.mean())
    print(f"\nsplit   : train {len(ytr)} / test {len(yte)} on END date "
          f"(test starts at unix {split_end})")
    print(f"contested (band [{CONTESTED_LO:.0f},{CONTESTED_HI:.0f}]%): "
          f"train {int(ytr.sum())} ({ytr.mean():.2%}) / "
          f"test {n_con_te} ({prevalence_te:.2%})")
    if n_con_te < 20:
        print(f"\n  *** WARNING: only {n_con_te} contested proposals in the test "
              f"set. Every metric below is UNSTABLE. Confidence intervals will\n"
              f"      be wide and point estimates should not be trusted. ***")

    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    Xte_std = (Xte - mu) / sd

    rng = np.random.default_rng(SEED)
    results, scores = {}, {}

    # 1. trivial constant
    scores["trivial_constant"] = np.full(len(yte), ytr.mean())
    # 2. logistic on identical features
    scores["logistic"] = predict_logistic(fit_logistic(Xtr, ytr), Xte)

    for name in ("trivial_constant", "logistic"):
        s = scores[name]
        ci = bootstrap_auc_ci(yte, lambda i, s=s: s[i], rng)
        results[name] = {"auc": auc(yte, s), "ci95": ci,
                         "pr_auc": average_precision(yte, s),
                         "pr_auc_null_prevalence": prevalence_te}

    # 3. quantum score functions, over N weight seeds
    print(f"\nrunning quantum engine: {len(yte)} rows x {n_rollouts} rollouts "
          f"x {n_weight_seeds} seeds ...", flush=True)
    per_seed = {k: [] for k in ("quantum_point", "quantum_dispersion", "quantum_coherence")}
    seed_scores = {k: [] for k in per_seed}
    for k_seed in range(n_weight_seeds):
        ws = SEED + k_seed
        qs = quantum_scores(Xte_std, ws, n_rollouts=n_rollouts, verbose=True)
        for k, v in qs.items():
            seed_scores[k].append(v)
            per_seed[k].append(auc(yte, v))
        print(f"  seed {ws}: " + "  ".join(
            f"{k.replace('quantum_', '')} AUC {auc(yte, v):.3f}" for k, v in qs.items()),
            flush=True)

    for k in per_seed:
        aucs = np.array(per_seed[k], dtype=float)
        mat = np.vstack(seed_scores[k])          # (n_seeds, n_test)

        def med_auc(idx, mat=mat):
            return float(np.median([auc(yte[idx], mat[j][idx]) for j in range(len(mat))]))

        boot = []
        for _ in range(N_BOOTSTRAP):
            idx = rng.integers(0, len(yte), len(yte))
            if yte[idx].sum() == 0:
                continue
            a = med_auc(idx)
            if not math.isnan(a):
                boot.append(a)
        barr = np.array(boot)
        results[k] = {
            "auc": float(np.median(aucs)),
            "auc_per_seed": [float(a) for a in aucs],
            "auc_seed_min": float(np.min(aucs)), "auc_seed_max": float(np.max(aucs)),
            "ci95": {"lo": float(np.percentile(barr, 2.5)),
                     "hi": float(np.percentile(barr, 97.5)),
                     "p_le_half": float(np.mean(barr <= 0.5)),
                     "n_valid": int(len(barr))},
            "pr_auc": float(np.median([average_precision(yte, m) for m in mat])),
            "pr_auc_null_prevalence": prevalence_te,
        }

    logi = results["logistic"]["auc"]
    verdict = {}
    for k in per_seed:
        r = results[k]
        verdict[k] = {
            "ci_lower_above_half": bool(r["ci95"]["lo"] > 0.5),
            "beats_logistic": bool(r["auc"] > logi),
            "PASSES_PREREGISTERED_CRITERION":
                bool(r["ci95"]["lo"] > 0.5 and r["auc"] > logi),
        }

    out = {
        "status": "COMPLETE",
        "config": {
            "contested_band_yes_pct": [CONTESTED_LO, CONTESTED_HI],
            "min_voters": MIN_VOTERS, "min_usable_n": MIN_USABLE_N,
            "test_frac": TEST_FRAC, "split_on": "proposal end date",
            "split_end_unix": int(split_end),
            "seed": SEED, "n_rollouts": n_rollouts,
            "n_weight_seeds": n_weight_seeds, "n_bootstrap": N_BOOTSTRAP,
            "num_qubits": NUM_QUBITS,
            "feature_names": FEATURE_NAMES,
            "dataset": os.path.basename(data_path),
            "dataset_fetched_at": payload["fetched_at"],
        },
        "counts": {
            "n_input": len(payload["proposals"]), "n_kept": len(kept),
            "dropped": drop, "n_train": len(ytr), "n_test": len(yte),
            "n_contested_train": int(ytr.sum()), "n_contested_test": n_con_te,
            "prevalence_train": float(ytr.mean()), "prevalence_test": prevalence_te,
        },
        "auc_null": 0.5,
        "results": results,
        "preregistered_criterion":
            "ROC-AUC 95% CI lower bound > 0.5 AND point estimate > logistic baseline",
        "verdict": verdict,
    }
    json.dump(out, open(out_path, "w"), indent=2)
    print_summary(out)
    return out


def print_summary(out):
    c, r = out["counts"], out["results"]
    print("\n" + "=" * 78)
    print(f"contested := final YES share in "
          f"[{out['config']['contested_band_yes_pct'][0]:.0f}%, "
          f"{out['config']['contested_band_yes_pct'][1]:.0f}%]   (LOCKED)")
    print(f"n_train {c['n_train']}  n_test {c['n_test']}  "
          f"n_contested_test {c['n_contested_test']} "
          f"({c['prevalence_test']:.2%} prevalence)")
    print("=" * 78)
    print(f"{'model':<24}{'ROC-AUC':>9}{'95% CI':>18}{'P(<=0.5)':>10}{'PR-AUC':>9}")
    print(f"{'':<24}{'null 0.5':>9}{'':>18}{'':>10}"
          f"{'null ' + format(c['prevalence_test'], '.3f'):>9}")
    print("-" * 78)
    for k in ("trivial_constant", "logistic", "quantum_point",
              "quantum_dispersion", "quantum_coherence"):
        v = r[k]
        ci = f"[{v['ci95']['lo']:.3f}, {v['ci95']['hi']:.3f}]"
        pa = v["pr_auc"]
        print(f"{k:<24}{v['auc']:>9.3f}{ci:>18}{v['ci95']['p_le_half']:>10.3f}"
              f"{pa:>9.3f}")
    print("-" * 78)
    print("\npre-registered criterion: CI lower bound > 0.5 AND AUC > logistic")
    for k, v in out["verdict"].items():
        print(f"  {k:<22} {'PASS' if v['PASSES_PREREGISTERED_CRITERION'] else 'FAIL'}"
              f"   (CI>0.5: {v['ci_lower_above_half']}, "
              f"beats logistic: {v['beats_logistic']})")
    print("\nAUC is a ranking metric. These scores are NOT calibrated "
          "probabilities and\nare not described as such.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/snapshot_dao_dataset.json")
    ap.add_argument("--out", default="data/benchmark_narrow_contestedness_results.json")
    ap.add_argument("--seeds", type=int, default=N_WEIGHT_SEEDS)
    ap.add_argument("--rollouts", type=int, default=N_ROLLOUTS)
    a = ap.parse_args()
    run(a.data, a.out, n_weight_seeds=a.seeds, n_rollouts=a.rollouts)
