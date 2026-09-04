"""
sensitivity_yes_share_definition.py — does the narrow-band result survive the
other reasonable definition of "final YES share"?

NOT PRE-REGISTERED. This is the disclosed sensitivity analysis required by
Amendment 1 of PREREGISTRATION_narrow_contestedness.md, and it is labelled as
such everywhere it appears.

The task brief defines YES share as yes_vp / scores_total, which INCLUDES
abstentions. The dataset's own stored field instead uses yes_vp / (yes_vp +
no_vp), which EXCLUDES them. They disagree on 694 of 905 proposals by up to
55pp. The primary analysis uses the brief's formula; this asks whether that
changes the answer.

Method: the model and its scores are held FIXED (read from the raw-scores file
the main run persists) and only the LABELS are swapped. That isolates the label
definition and needs no second multi-hour engine pass.

Limitation, stated up front: the features carry a past-only prior_dao_contested
term built from definition-A labels, so this answers "does the definition-A
ranking still separate definition-B labels?", not "what would a model trained
under B from scratch do?"

    python3 q_ai_governance/sensitivity_yes_share_definition.py
"""

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q_ai_governance.benchmark_narrow_contestedness import (  # noqa: E402
    auc, average_precision, SEED, N_BOOTSTRAP)

MODELS = ["trivial_constant", "logistic", "quantum_point",
          "quantum_dispersion", "quantum_coherence"]


def eval_under(y, scores_by_model, rng):
    """scores_by_model[name] is either (n,) or (n_seeds, n) for quantum scores."""
    out = {}
    prev = float(y.mean())
    for name, s in scores_by_model.items():
        mat = s if s.ndim == 2 else s[None, :]
        aucs = [auc(y, m) for m in mat]
        boot = []
        for _ in range(N_BOOTSTRAP):
            idx = rng.integers(0, len(y), len(y))
            if y[idx].sum() == 0:
                continue
            a = float(np.median([auc(y[idx], m[idx]) for m in mat]))
            if not math.isnan(a):
                boot.append(a)
        b = np.array(boot)
        out[name] = {
            "auc": float(np.median(aucs)),
            "auc_per_seed": [float(a) for a in aucs],
            "ci95": {"lo": float(np.percentile(b, 2.5)),
                     "hi": float(np.percentile(b, 97.5)),
                     "p_le_half": float(np.mean(b <= 0.5)),
                     "n_valid": int(len(b))},
            "pr_auc": float(np.median([average_precision(y, m) for m in mat])),
            "pr_auc_null_prevalence": prev,
        }
    return out, prev


def main(scores_path, primary_path, out_path):
    z = np.load(scores_path)
    primary = json.load(open(primary_path))
    scores = {n: z[n] for n in MODELS}

    y_primary = z["y_test"]
    y_alt = z["y_test_alt_labeldef"]
    rng = np.random.default_rng(SEED)

    res_p, prev_p = eval_under(y_primary, scores, rng)
    res_a, prev_a = eval_under(y_alt, scores, rng)

    # sanity: the re-derived primary must match the committed primary run
    drift = {k: abs(res_p[k]["auc"] - primary["results"][k]["auc"]) for k in MODELS}
    worst = max(drift.values())

    out = {
        "status": "COMPLETE",
        "not_preregistered": True,
        "note": ("Disclosed sensitivity analysis per Amendment 1. Model and scores "
                 "held fixed; only labels swapped."),
        "definitions": {
            "A_primary_preregistered": "yes_vp / scores_total (includes abstain)",
            "B_sensitivity": "yes_vp / (yes_vp + no_vp) (excludes abstain)",
        },
        "n_test": int(len(y_primary)),
        "n_contested_test": {"A_primary": int(y_primary.sum()), "B_sensitivity": int(y_alt.sum())},
        "prevalence_test": {"A_primary": prev_p, "B_sensitivity": prev_a},
        "n_labels_changed": int((y_primary != y_alt).sum()),
        "auc_null": 0.5,
        "results_A_primary_rederived": res_p,
        "results_B_sensitivity": res_a,
        "rederivation_max_auc_drift_vs_committed_primary": float(worst),
    }
    json.dump(out, open(out_path, "w"), indent=2)

    print("SENSITIVITY ANALYSIS — NOT PRE-REGISTERED (Amendment 1)")
    print(f"model and scores held fixed; only the label definition changes\n")
    print(f"n_test {out['n_test']}   labels changed by the redefinition: "
          f"{out['n_labels_changed']}")
    print(f"contested: A(incl. abstain) {int(y_primary.sum())} ({prev_p:.2%})   "
          f"B(excl. abstain) {int(y_alt.sum())} ({prev_a:.2%})")
    print(f"\nre-derivation check vs committed primary: max AUC drift "
          f"{worst:.2e} {'OK' if worst < 1e-9 else 'MISMATCH'}\n")
    print(f"{'model':<22}{'A AUC':>8}{'A 95% CI':>18}{'B AUC':>8}{'B 95% CI':>18}")
    print("-" * 74)
    for k in MODELS:
        a, b = res_p[k], res_a[k]
        ci_a = "[{:.3f}, {:.3f}]".format(a["ci95"]["lo"], a["ci95"]["hi"])
        ci_b = "[{:.3f}, {:.3f}]".format(b["ci95"]["lo"], b["ci95"]["hi"])
        print(f"{k:<22}{a['auc']:>8.3f}{ci_a:>18}{b['auc']:>8.3f}{ci_b:>18}")
    print("-" * 74)
    print(f"AUC null is 0.5. PR-AUC null is prevalence: "
          f"A {prev_p:.3f}, B {prev_a:.3f}.")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default="data/narrow_contestedness_raw_scores.npz")
    ap.add_argument("--primary", default="data/benchmark_narrow_contestedness_results.json")
    ap.add_argument("--out", default="data/sensitivity_yes_share_definition.json")
    a = ap.parse_args()
    main(a.scores, a.primary, a.out)
