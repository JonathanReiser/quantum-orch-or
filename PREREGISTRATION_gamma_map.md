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

---

# Amendment 1 — 2026-09-13, written after a first grid run, before any result is reported

## The defect

The first run of the locked grid returned **FRAGILE for Q4**, the quantity that
prediction **P1** said must be *exactly invariant*. Under the rule fixed above —

> If the grid contradicts P1, P2 or P3, that is a bug in this analysis or in the
> module, and gets reported as such rather than as a finding about the bridge.

— this was investigated before anything was written up. It is a bug in this
analysis, and the original specification of Q1–Q4 is at fault.

Q1, Q3 and Q4 were all measured on a trajectory produced with the module default
`mindfulness_at_s = 4.0`, i.e. an instantaneous rotation at a **fixed wall-clock
time**. That rotation breaks the `gamma*t` scaling symmetry, because as `gamma`
varies the intervention lands at a different *dimensionless* time `gamma*4.0`.
Q1/Q3/Q4 therefore measured the gamma map's constants **confounded with the
intervention's relative timing**, which is a separate parameter that this study
does not vary and never intended to test.

Direct evidence, run on intervention-free trajectories:

| gamma | coherence at `gamma*t = 2` |
|---|---|
| 0.02 | 0.3678794642 |
| 0.10 | 0.3678794642 |
| 0.40 | 0.3678794412 |
| 0.82 | 0.3678795626 |
| 2.00 | 0.3678794412 |

against `exp(-1) = 0.3678794412`. **P1 holds exactly**, to ~1e-7, across two
orders of magnitude in `gamma`. The apparent fragility was entirely an artifact
of the fixed-time rotation.

The same contamination hit Q3. With no clip binding and no intervention, the
Spearman rho is `-1.0000` exactly, as **P2** predicted. With the intervention it
ranged from `-0.99` to `+0.50` — the rotation can invert the apparent
relationship between HRV loss and coherence loss.

## The correction

**Q1, Q3 and Q4 are measured on intervention-free trajectories**
(`mindfulness_at_s = None`). Q5 is unchanged: it is *defined* as the difference
the intervention makes, so it must keep it, and its fixed wall-clock timing is
part of what it measures.

Nothing else moves. The grid, the drop sweep, the ROBUST/FRAGILE thresholds and
the simulation settings are as locked above. The first (contaminated) run is
superseded and its numbers are not reported as results.

## A finding that survives the correction, recorded here because it is not a bug

The ceiling clip **binds in 53 of the 120 cells**. Where it binds, multiple
values of `drop` map to the same `gamma`, the map stops being injective, and
rank discriminability degrades on its own — Spearman rho at
`(floor=0.02, scale=3.20, ceiling=1.00)` is `-0.4909` with no intervention at
all, against `-1.0000` where nothing clips. That is a real property of the map,
not an artifact, and it is reported as a result.

---

# Amendment 2 — 2026-09-13, written before any result is reported

## The defect

After Amendment 1, Q3 still reported a span of 1.5, which requires some cell to
have a **positive** Spearman rho between HRV loss and coherence at 5 s on an
intervention-free trajectory. That is physically impossible here: `gamma` is
non-decreasing in `drop`, and coherence at fixed `t` is strictly decreasing in
`gamma`, so rho can only be negative or, under ties, zero.

The cause is the rank implementation in `tools/gamma_map_sensitivity.py`. It used
`argsort(argsort(x))`, which assigns **distinct ranks to tied values in index
order** instead of averaging them. The ceiling clip produces exact ties — that is
its entire effect — so the cells where the clip binds are precisely the cells
where the naive ranking misbehaves.

Worked example, `floor=0.20, scale=3.20, ceiling=0.50`, where ten of the eleven
`drop` values clip to `gamma = 0.50`:

| method | rho |
|---|---|
| `argsort(argsort(.))` (what was used) | **+0.5** |
| `scipy.stats.spearmanr` (tie-averaged) | **−0.5** |

The naive estimator does not merely lose precision — it **inverts the sign of the
conclusion**, turning "more HRV loss, less coherence" into its opposite. Had this
gone unnoticed it would have manufactured a positive finding out of a tie.

## The correction

Q3 uses `scipy.stats.spearmanr`, which averages tied ranks. `scipy` is already a
dependency of this repository (`requirements.txt`: `scipy>=1.10.0`). Ties are
reported explicitly per cell (`n_distinct_gamma`) so that a degraded rho can be
read as saturation rather than noise.

Nothing else moves. The grid, quantities, thresholds and settings stay as locked.
Runs prior to this amendment are superseded and are not reported as results.

---

# Amendment 3 — 2026-09-13, post-result review correction

## The defect

An adversarial review after the result was written found that Q2 and Q4 were
silently censored by the fixed 10-second trajectory. `_half_life` returned
`None` both when `gamma = 0` (genuinely undefined) and when a positive-gamma
half-life merely occurred after 10 seconds. Q4 likewise returned `None` when
`2/gamma > 10`, although Q4's dimensionless observation time is not logically
limited by the wall-clock window used for Q1 and Q5.

At the pre-specified aggregation point `drop = 0.5`, this excluded 12 Q2 cells
and 16 Q4 cells. The report nevertheless described both ranges as being across
all 120 cells. The stated Q2 maximum, 9.24 s, was therefore a window artifact;
the correct maximum is `2 ln(2) / 0.10 = 13.8629 s`.

## The correction

Q2 and Q4 are now evaluated from the pre-registered, solver-validated closed
form: `Q2 = 2 ln(2) / gamma` and `Q4 = exp(-1)` for every `gamma > 0`.
They remain undefined only at `gamma = 0`. The categorical verdicts do not
change: Q2 remains FRAGILE and Q4 remains ROBUST.

Continuous summaries (range, log-range where defined, IQR/median, MAD/median,
maximum absolute value and sign counts) are now recorded at `drop = 0.5` and at
all 11 drop values. These are descriptive additions; the pre-registered 10%
decision rule is retained and explicitly labelled as an operational threshold,
not a physically privileged boundary.
