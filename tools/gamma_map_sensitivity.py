#!/usr/bin/env python3
"""Sensitivity of downstream conclusions to the somatic gamma map's constants.

Pre-registered in PREREGISTRATION_gamma_map.md, committed before this ran.
Grid, quantities and the ROBUST/FRAGILE criterion are fixed there; this script
implements them and nothing else.
"""
from __future__ import annotations

import argparse
import json
from importlib.metadata import version as _pkg_version

import numpy as np
from scipy.stats import spearmanr

from quantum_orch_or.cognitive_lindblad import simulate

FLOORS = (0.00, 0.01, 0.02, 0.05, 0.10, 0.20)
SCALES = (0.20, 0.40, 0.80, 1.60, 3.20)
CEILINGS = (0.50, 0.82, 1.00, 2.00)
DROPS = tuple(round(0.1 * i, 1) for i in range(11))

DURATION_S = 10.0
SAMPLES = 301
THERMAL = 0.10
MINDFUL_AT_S = 4.0
MINDFUL_ANGLE = -np.pi / 5

DEFAULTS = (0.02, 0.80, 1.00)


def gamma_of(drop: float, floor: float, scale: float, ceiling: float) -> float:
    return float(np.clip(floor + scale * drop, floor, ceiling))


def _interp_at(t_grid, y, t):
    return float(np.interp(t, t_grid, y))


def coherence_half_life(gamma: float) -> float | None:
    """Exact half-life for coherence exp(-gamma*t/2).

    Amendment 3: measuring this only inside the fixed 10 s trajectory falsely
    labelled positive-gamma half-lives beyond the window as undefined.
    """
    return None if gamma <= 0.0 else float(2.0 * np.log(2.0) / gamma)


def coherence_at_gamma_t_2(gamma: float) -> float | None:
    """Exact Q4 value. Dimensionless time is undefined when gamma is zero."""
    return None if gamma <= 0.0 else float(np.exp(-1.0))


def _spearman(a, b):
    """Tie-averaged Spearman. Amendment 2: argsort(argsort(.)) breaks ties by
    index order, which INVERTS the sign of rho when the ceiling clip creates
    ties -- and creating ties is exactly what the ceiling clip does."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.all(np.isnan(b)) or np.unique(b[~np.isnan(b)]).size < 2:
        return None
    rho = spearmanr(a, b).statistic
    return None if np.isnan(rho) else float(rho)


def cell(floor, scale, ceiling):
    q1, q2, q4, q5, gammas = [], [], [], [], []
    for drop in DROPS:
        g = gamma_of(drop, floor, scale, ceiling)
        gammas.append(g)
        # Amendment 1: Q1/Q3/Q4 are measured WITHOUT the intervention, whose
        # fixed wall-clock timing breaks the gamma*t scaling symmetry and would
        # confound the map's constants with the intervention's relative timing.
        tr = simulate(g, duration_s=DURATION_S, samples=SAMPLES,
                      thermal_excited_fraction=THERMAL, mindfulness_at_s=None)
        # Q5 keeps it: Q5 is defined as the difference the intervention makes.
        with_intervention = simulate(g, duration_s=DURATION_S, samples=SAMPLES,
                                     thermal_excited_fraction=THERMAL,
                                     mindfulness_at_s=MINDFUL_AT_S,
                                     mindfulness_angle=MINDFUL_ANGLE)
        base = tr
        q1.append(_interp_at(tr.time_s, tr.coherence_l1, 5.0))
        q2.append(coherence_half_life(g))
        # Q4 is defined at t=2/gamma even when that time exceeds the separate
        # 10 s wall-clock observation window used by Q1 and Q5.
        q4.append(coherence_at_gamma_t_2(g))
        q5.append(float(with_intervention.purity[-1] - base.purity[-1]))
    q3 = _spearman(DROPS, q1)
    return {
        "floor": floor, "scale": scale, "ceiling": ceiling,
        "gamma_min": gammas[0], "gamma_max": gammas[-1],
        "dynamic_range": (gammas[-1] / gammas[0]) if gammas[0] > 0 else None,
        "ceiling_binds": bool(floor + scale * 1.0 > ceiling),
        "drops": list(DROPS), "gammas": gammas,
        "Q1_coherence_at_5s": q1,
        "Q2_half_life_s": q2,
        "Q3_spearman_drop_vs_Q1": q3,
        "n_distinct_gamma": int(len(set(gammas))),
        "Q4_coherence_at_gamma_t_2": q4,
        "Q5_purity_delta_from_intervention": q5,
    }


def spread(values):
    """Relative spread max/min over finite values, per the pre-registered rule."""
    v = [x for x in values if x is not None and np.isfinite(x)]
    if len(v) < 2:
        return None
    lo, hi = min(v), max(v)
    if lo <= 0:
        return None if hi <= 0 else float("inf")
    return (hi - lo) / lo


def continuous_summary(values):
    """Scale-aware descriptive statistics; no categorical threshold."""
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], float)
    out = {"n_defined": int(v.size), "n_total": len(values)}
    if v.size == 0:
        return out
    lo, hi = float(np.min(v)), float(np.max(v))
    median = float(np.median(v))
    q25, q75 = (float(x) for x in np.percentile(v, [25, 75]))
    mad = float(np.median(np.abs(v - median)))
    out.update({"min": lo, "max": hi, "median": median,
                "iqr_over_abs_median": ((q75 - q25) / abs(median)) if median else None,
                "mad_over_abs_median": (mad / abs(median)) if median else None,
                "max_abs": float(np.max(np.abs(v))),
                "n_negative": int(np.sum(v < 0)), "n_zero": int(np.sum(v == 0)),
                "n_positive": int(np.sum(v > 0))})
    if lo > 0:
        out["max_over_min"] = hi / lo
        out["log_range"] = float(np.log(hi / lo))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()

    cells = [cell(f, s, c) for f in FLOORS for s in SCALES for c in CEILINGS]

    # Aggregate each quantity at a representative drop (0.5) across all cells,
    # which is what "the conclusion" would be stated at.
    mid = DROPS.index(0.5)
    agg = {
        "Q1_coherence_at_5s": [c["Q1_coherence_at_5s"][mid] for c in cells],
        "Q2_half_life_s": [c["Q2_half_life_s"][mid] for c in cells],
        "Q4_coherence_at_gamma_t_2": [c["Q4_coherence_at_gamma_t_2"][mid] for c in cells],
        "Q5_purity_delta_from_intervention": [c["Q5_purity_delta_from_intervention"][mid] for c in cells],
    }
    verdict = {}
    for k, vals in agg.items():
        s = spread(vals)
        verdict[k] = {
            "relative_spread": s,
            "n_defined": sum(1 for x in vals if x is not None and np.isfinite(x)),
            "n_cells": len(vals),
            "verdict": "ROBUST" if (s is not None and s < 0.10) else "FRAGILE",
        }
    rhos = [c["Q3_spearman_drop_vs_Q1"] for c in cells]
    finite_rhos = [r for r in rhos if r is not None]
    rho_span = (max(finite_rhos) - min(finite_rhos)) if len(finite_rhos) > 1 else None
    verdict["Q3_spearman_drop_vs_Q1"] = {
        "absolute_span": rho_span,
        "min": min(finite_rhos) if finite_rhos else None,
        "max": max(finite_rhos) if finite_rhos else None,
        "n_defined": len(finite_rhos), "n_cells": len(rhos),
        "verdict": "ROBUST" if (rho_span is not None and rho_span < 0.05) else "FRAGILE",
    }

    payload = {
        "preregistration": "PREREGISTRATION_gamma_map.md",
        "defaults": {"floor": DEFAULTS[0], "scale": DEFAULTS[1], "ceiling": DEFAULTS[2]},
        "settings": {"duration_s": DURATION_S, "samples": SAMPLES,
                     "thermal_excited_fraction": THERMAL,
                     "mindfulness_at_s": MINDFUL_AT_S,
                     "mindfulness_angle": float(MINDFUL_ANGLE)},
        "grid": {"floors": list(FLOORS), "scales": list(SCALES),
                 "ceilings": list(CEILINGS), "drops": list(DROPS),
                 "n_cells": len(cells)},
        "versions": {p_: _pkg_version(p_) for p_ in ("qiskit", "qiskit-dynamics", "numpy")},
        "aggregate_at_drop_0.5": verdict,
        "continuous_summary_at_drop_0.5": {
            k: continuous_summary(v) for k, v in agg.items()
        },
        "continuous_summary_by_drop": {
            str(drop): {
                k: continuous_summary([c[k][i] for c in cells])
                for k in agg
            }
            for i, drop in enumerate(DROPS)
        },
        "cells": cells,
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print(f"grid cells: {len(cells)}")
    print(f"ceiling binds in {sum(c['ceiling_binds'] for c in cells)}/{len(cells)} cells")
    print()
    for k, v in verdict.items():
        extra = (f"span={v['absolute_span']:.3g}" if "absolute_span" in v
                 else (f"rel spread={v['relative_spread']:.3g}"
                       if v["relative_spread"] is not None else "rel spread=undefined"))
        print(f"  [{v['verdict']:8s}] {k:36s} {extra}  ({v['n_defined']}/{v['n_cells']} defined)")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
