# Pre-registration — sensitivity of the somatic gamma map

**Written 2026-09-13, committed before any sensitivity grid was run.**
Everything below is fixed at the moment of this commit. Nothing in it may be
changed once results exist; if something here turns out to be a bad choice, the
bad choice gets reported alongside the result rather than quietly repaired.

Drafted with Claude (Opus 5) at the repository owner's direction. The structural
probes in "Known properties" below were run *before* this file was written and
are disclosed here rather than presented later as discoveries.

## The object under test

`quantum_orch_or/somatic_bridge.py` maps a fractional drop in heart-rate
variability to a rate named `gamma`, which `quantum_orch_or/cognitive_lindblad.py`
then uses as the dissipation rate of a one-qubit open system:

```python
drop  = clip((baseline - current) / baseline, 0.0, 1.0)
gamma = clip(floor + scale * drop, floor, ceiling)     # 0.02 + 0.80 * drop, ceiling 1.00
```

`floor = 0.02`, `scale = 0.80`, `ceiling = 1.00` are **undetermined constants**.
Nothing in the repository derives them from measurement or theory. This
pre-registration exists because that is the load-bearing assumption of the
somatic → quantum bridge, and it has never been tested.

## Disclosure of what was already known at write time

A pre-registration written with results already in hand is worthless, so here is
everything that had been established before this file existed.

1. **Nothing consumes these modules.** `git grep` over the branch shows the only
   references to `somatic_bridge` / `cognitive_lindblad` are their own two test
   files and one descriptive line in `REPOSITORY_MAP.md`. **No published claim
   in this repository currently rests on the gamma map.** This study is therefore
   genuinely prospective: there is no result to defend.
2. **The ceiling is inert at the default constants.** `0.02 + 0.80 * 1.0 = 0.82`,
   which is below `ceiling = 1.00`. The clip at the top can never bind for any
   input. Verified numerically. This is disclosed in advance so it cannot later
   be presented as an explanation for a null sensitivity to `ceiling`.
3. **The dynamics depend on `gamma` and `t` only through the product `gamma*t`.**
   `cognitive_lindblad.simulate` passes `static_hamiltonian=np.zeros((2,2))`, and
   both dissipators carry `sqrt(gamma)`, so `drho/dt = gamma * L[rho]` exactly.
   Verified numerically: `simulate(0.40, duration_s=10)` and
   `simulate(0.80, duration_s=5)` agree to `<= 1.0e-09` on all three observables.
4. **The trajectory has a closed form**, confirmed against the solver to
   `<= 7.3e-10`:
   `coherence_l1(t) = coherence_l1(0) * exp(-gamma*t/2)`
   `p_choice_1(t)   = p_th + (0.5 - p_th) * exp(-gamma*t)`, `p_th = 0.10`.
5. **The repository's own papers state a different gamma by ~13 orders of
   magnitude.** `q_ai_governance_paper.md:56` gives thermal dephasing at 310 K as
   `gamma ~ 1e13 s^-1`. The somatic bridge emits `gamma` in `[0.02, 0.82] s^-1`.
   The papers' operator is `sqrt(gamma) sigma_z` (pure dephasing); the code's
   operators are `sqrt(down) sigma_-` and `sqrt(up) sigma_+` (thermal
   relaxation). These are **different quantities that share a name.** Recorded
   here because it is bad news, and it belongs on the record before results.

## What follows analytically from (3), stated before the grid runs

Because the trajectory is a function of `gamma*t` alone, `scale` is **exactly a
reparameterization of time**. Doubling `scale` is indistinguishable from doubling
the observation window. Three predictions follow, and they are committed here:

* **P1.** Any conclusion stated in **dimensionless time** `gamma*t` is *exactly*
  invariant to `floor` and `scale`. Expected max deviation: solver tolerance,
  `< 1e-8`.
* **P2.** Any conclusion that depends only on the **rank ordering** of subjects
  or windows is invariant to `floor` and `scale` for any `scale > 0`, because
  the map is affine and monotone in `drop` while no clip binds.
* **P3.** Any conclusion stated at a **fixed wall-clock time** is sensitive to
  `scale`, and the sensitivity is not a discovery about physiology — it is the
  time rescaling in P1 restated.

If the grid contradicts P1, P2 or P3, that is a bug in this analysis or in the
module, and gets reported as such rather than as a finding about the bridge.

## Locked grid

`floor` in `{0.00, 0.01, 0.02, 0.05, 0.10, 0.20}`
`scale` in `{0.20, 0.40, 0.80, 1.60, 3.20}`
`ceiling` in `{0.50, 0.82, 1.00, 2.00}`
Full factorial, 120 cells. Defaults `(0.02, 0.80, 1.00)` are in the grid.

`drop` is swept over `{0.0, 0.1, ..., 1.0}` (11 values), covering the full
reachable range of the map. No wearable data is used; `drop` is the map's only
input and is swept directly, so nothing here depends on a dataset.

Simulation settings held fixed at the module defaults:
`duration_s = 10.0`, `samples = 301`, `thermal_excited_fraction = 0.10`,
`mindfulness_at_s = 4.0`, `mindfulness_angle = -pi/5`.

## Pre-specified quantities and the claims they stand for

For each grid cell, and for each `drop`:

* **Q1 — `coherence_l1` at `t = 5 s`** (fixed wall-clock). Stands for a claim of
  the form *"after five seconds, a stressed subject has lost X coherence."*
* **Q2 — coherence half-life** `t` such that `coherence_l1(t) = 0.5`, in seconds
  (fixed wall-clock). Stands for *"coherence half-life is X seconds."*
* **Q3 — Spearman rank correlation between `drop` and `Q1`** across the 11 `drop`
  values. Stands for *"lower HRV means faster coherence loss"* — a rank claim.
* **Q4 — `coherence_l1` at dimensionless time `gamma*t = 2`.** Stands for the
  same physics as Q1 but stated in the system's own time units.
* **Q5 — purity at `t = 10 s`** minus purity at `t = 10 s` with
  `mindfulness_at_s = None`. Stands for *"the intervention changes the outcome."*

## Success / failure criterion, fixed in advance

A quantity is declared **ROBUST** iff, across all 120 cells, its value varies by
less than **10% in relative terms** (for Q3, by less than **0.05 in absolute
Spearman rho**). Otherwise it is **FRAGILE**.

The headline result is the **partition** of {Q1..Q5} into ROBUST and FRAGILE.
Both outcomes are reportable. A finding that every magnitude claim is FRAGILE is
a real result and is to be reported as the headline, not buried.

Additionally reported, because it is the number that matters for whether the map
has any discriminative content at all:

* **dynamic range** `gamma(drop=1) / gamma(drop=0)` per cell. At defaults this is
  `0.82 / 0.02 = 41`. As `floor` grows the map compresses toward a constant; at
  `floor = 0.20, scale = 0.20` it is `2.0`. A map with range near 1 cannot
  distinguish a calm subject from a stressed one regardless of the physics
  downstream.

## Guardrails

* **No clamping** of any reported metric.
* **No hardcoded numbers.** Every figure traces to the committed results JSON.
* **Tests must be able to fail.** No assertion on an `abs()` that cannot be false.
* The results file records the full grid, all settings, and the module versions
  (`qiskit`, `qiskit-dynamics`) used to produce it.
* `floor = 0.00` is included deliberately: it makes `gamma = 0` at `drop = 0`,
  which means no dynamics at all. If that produces a degenerate or undefined
  half-life, the degeneracy is reported, not silently dropped.

## What this study cannot establish

It tests whether *downstream conclusions move when the constants move*. It does
**not** test whether the constants are correct, and it cannot: there is no
ground-truth measurement anywhere in this repository linking HRV to a
decoherence rate. Robustness under perturbation is **not** evidence that the map
is physically meaningful. Given disclosure (5), the honest reading of a ROBUST
result is "this conclusion does not depend on constants that are themselves
unvalidated" — which is weaker than it sounds, and must not be reported as
support for the Orch-OR framing.
