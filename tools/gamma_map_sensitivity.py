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


# Dimensionless horizon for the Q2/Q4 trajectory, in units of gamma*t. It must
# exceed both the coherence half-life (gamma*t = 2 ln 2 ~ 1.386) and Q4's
# observation point (gamma*t = 2), with headroom.
DIMENSIONLESS_HORIZON = 6.0
DIMENSIONLESS_SAMPLES = 4001


def dimensionless_trajectory(gamma: float):
    """Trajectory on a window scaled to 1/gamma, so nothing is censored.

    Amendment 4: Q2 and Q4 are measured from the solver here. Amendment 3 had
    replaced them with closed forms -- which removed the wall-clock censoring
    but also decoupled both quantities from the module they describe, leaving
    Q4 a literal exp(-1) that no measurement produces.
    """
    if gamma <= 0.0:
        return None
    return simulate(gamma, duration_s=DIMENSIONLESS_HORIZON / gamma,
                    samples=DIMENSIONLESS_SAMPLES,
                    thermal_excited_fraction=THERMAL, mindfulness_at_s=None)


def coherence_half_life(gamma: float, trajectory=None) -> float | None:
    """Half-life of coherence, measured from the solver trajectory."""
    if gamma <= 0.0:
        return None
    tr = dimensionless_trajectory(gamma) if trajectory is None else trajectory
    coh = tr.coherence_l1
    c0 = coh[0]
    if c0 <= 0:
        return None
    target = 0.5 * c0
    below = np.nonzero(coh <= target)[0]
    if below.size == 0:
        # Only reachable if DIMENSIONLESS_HORIZON is set below 2 ln 2.
        raise RuntimeError(
            f"half-life not reached within gamma*t={DIMENSIONLESS_HORIZON}; "
            "the horizon is too short, which would silently censor Q2")
    i = int(below[0])
    if i == 0:
        return 0.0
    t0, t1, y0, y1 = tr.time_s[i - 1], tr.time_s[i], coh[i - 1], coh[i]
    if y0 == y1:
        return float(t1)
    return float(t0 + (y0 - target) * (t1 - t0) / (y0 - y1))


def coherence_at_gamma_t_2(gamma: float, trajectory=None) -> float | None:
    """Coherence at dimensionless time gamma*t = 2, measured from the solver."""
    if gamma <= 0.0:
        return None
    tr = dimensionless_trajectory(gamma) if trajectory is None else trajectory
    t_star = 2.0 / gamma
    if t_star > tr.time_s[-1]:
        raise RuntimeError(
            "gamma*t=2 lies outside the dimensionless window; "
            "the horizon is too short, which would silently censor Q4")
    return _interp_at(tr.time_s, tr.coherence_l1, t_star)


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
        # Amendment 4: one gamma-scaled trajectory serves both Q2 and Q4, so
        # each is a solver measurement rather than an asserted closed form, and
        # neither is censored by the 10 s wall-clock window Q1 and Q5 use.
        dtr = dimensionless_trajectory(g)
        q1.append(_interp_at(tr.time_s, tr.coherence_l1, 5.0))
        q2.append(coherence_half_life(g, dtr))
        q4.append(coherence_at_gamma_t_2(g, dtr))
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
