# Result — the somatic gamma map's constants decide the answer

Pre-registered in [`PREREGISTRATION_gamma_map.md`](PREREGISTRATION_gamma_map.md),
committed at `f232bb8` before the grid ran. Two pre-result amendments and one
post-result review correction are recorded there. Every figure here traces to
[`data/gamma_map_sensitivity.json`](data/gamma_map_sensitivity.json), produced by
`tools/gamma_map_sensitivity.py`.

Run with qiskit 1.3.0, qiskit-dynamics 0.6.0, numpy 2.5.3. 120 grid cells.

## Headline

**Four of the five pre-registered quantities are FRAGILE. The ROBUST quantity
is a successful structural control, not a physiological result.**

| quantity | what it stands for | spread across 120 cells | verdict |
|---|---|---|---|
| **Q1** coherence at `t = 5 s` | *"after 5 s a stressed subject has lost X coherence"* | `0.0111 → 0.7788` (**70×**) | **FRAGILE** |
| **Q2** coherence half-life | *"coherence half-life is X seconds"* | `0.77 s → 13.86 s` (**18×**) | **FRAGILE** |
| **Q3** rank corr. HRV-loss vs coherence | *"lower HRV means faster coherence loss"* | `−1.00 → −0.50` | **FRAGILE** (sign always correct) |
| **Q4** coherence at `gamma*t = 2` | the same physics in the system's own time units | `0.367879` (exactly invariant) | **ROBUST** |
| **Q5** purity change from the intervention | *"the intervention changes the outcome"* | `−1.1e-05 → +0.0342`, **sign flips** | **FRAGILE** |

## What this means, stated plainly

**Any claim in seconds is arbitrary.** Q1 and Q2 are the shape every readable
claim about this bridge would take. Feed the *identical* physiological input —
a 50% drop in HRV — into the same code, and the reportable answer moves by a
factor of 70, purely by choosing `floor` and `scale` differently. Nothing in
the repository says which choice is right, because nothing derives these
constants from anything. "Coherence half-life is 3.3 seconds" is true at the
defaults and equally true at 0.77 s or 13.86 s elsewhere in the grid.

**The robust quantity is a useful structural control, not physiological
evidence.** Q4 is exactly invariant because coherence at `gamma*t = 2` is
`exp(−1)` for every positive-gamma subject, cell and input. That successfully
checks the generator's scale covariance. It does not discriminate between
subjects: choosing each observation time as `2/gamma` forces the common value.

**The intervention's sign is not determined.** Q5 is positive in 84 cells and
negative in 36. Whether the "mindfulness" rotation *helps* or *hurts* final
purity is decided by constants chosen without justification. The effect is also
tiny in absolute terms (≤ 0.034 of a purity that starts at 1.0).

**The rank claim is the only survivor with content.** Q3 keeps the correct sign
in all 120 cells: more HRV loss always means less coherence. It degrades from
`−1.00` to `−0.50` only where the ceiling clip saturates the map — 51 cells have
tied `gamma` values. This is the one conclusion worth stating, and it is also
the weakest: it says the map is monotone, which is true by construction.

## The map has structural defects independent of the sensitivity question

**The ceiling is inert at the defaults.** `0.02 + 0.80 × 1.0 = 0.82 < 1.00`. The
top clip cannot bind for any input. It is a parameter that does nothing — and
across the grid it binds in **53 of 120** cells, where its only effect is to
destroy discriminability by mapping distinct subjects onto identical `gamma`.

**The dynamic range is itself a free choice**, spanning **2× to 200×** across the
grid (41× at the defaults). A map near 1× cannot distinguish a calm subject from
a stressed one no matter how correct the downstream physics is.

**`floor = 0` is degenerate at `drop = 0`.** In 20 of the 120 parameter cells,
`gamma = 0` at rest, so Q2 and Q4 are genuinely undefined there. Positive-gamma
values are no longer confused with observations beyond the 10-second window.

## How to read the robustness verdicts

The 10% boundary is the pre-registered operational rule, not a physically
privileged constant. The JSON therefore also reports continuous range,
log-range, IQR/median and MAD/median summaries at the midpoint and for every
drop value. For the signed Q5 effect, its signed range, maximum absolute effect
and sign counts are more meaningful than a relative spread across zero.

The midpoint is an illustrative estimand, not a summary of the whole response
surface. Near `drop = 0`, the floor dominates; at intermediate drops, scale
dominates; and near `drop = 1`, ceiling saturation can dominate. The per-drop
summaries expose those regimes.

Finally, the 16× scale grid is a global structural stress test under complete
parameter non-identification, not a calibrated uncertainty interval. A future
physiological calibration should motivate a separate, local grid around the
default values.

## Corrections found in this analysis

The first two were caught before results were written; the third was found by
post-result adversarial review.

1. **Q1/Q3/Q4 were contaminated by a fixed-wall-clock intervention** that breaks
   the `gamma*t` scaling symmetry. Q4 looked FRAGILE when theory said it must be
   exactly invariant — which the pre-registration had already designated as a
   bug signal rather than a finding. Fixed in Amendment 1; Q4 then came out
   ROBUST at 1e-4, as predicted.
2. **The rank statistic inverted its own sign under ties.** `argsort(argsort(.))`
   assigns tied values distinct ranks in index order. The ceiling clip *produces*
   ties, so this hit exactly the cells under test: it reported **+0.5** where the
   tie-averaged Spearman is **−0.5**. Left in place it would have manufactured
   "more HRV loss, *more* coherence" out of a saturation artifact. Fixed in
   Amendment 2.
3. **Q2 and Q4 were silently censored at 10 seconds.** This excluded 12 and 16
   positive-gamma midpoint cells respectively while the report said "across 120
   cells." Q2's corrected range is 0.77–13.86 s; Q4 is exactly `exp(-1)` in all
   120 midpoint cells. Fixed in Amendment 3.

## What this does not establish

This tests whether conclusions move when the constants move. It does **not**
test whether the constants are right, and it cannot: there is no ground-truth
measurement anywhere in this repository linking HRV to a decoherence rate.

It is also worth restating a disclosure from the pre-registration, because it
bears on every number above. This repository's own papers give the thermal
decoherence rate at 310 K as `gamma ~ 1e13 s^-1`
(`q_ai_governance_paper.md:56`), against the somatic bridge's `[0.02, 0.82]
s^-1` — about **13 orders of magnitude** apart — and the papers' operator is
`sqrt(gamma) sigma_z` (pure dephasing) where the code uses `sigma_-`/`sigma_+`
(thermal relaxation). These are different quantities that share a name. No
choice of `floor`, `scale` or `ceiling` closes that gap.

## Recommendation

The map should not be presented as a measurement. Either:

1. **State conclusions in dimensionless time** and accept that they are then
   statements about `exp(−x)` rather than about physiology; or
2. **State only rank-ordered conclusions**, which survive here, and drop the
   ceiling (inert at defaults, harmful where it binds); or
3. **Derive the constants** from something — a calibration against a measured
   quantity — at which point this study should be re-run against that
   derivation.

Until one of those happens, wall-clock numbers produced through this bridge
should be treated as outputs of a chosen parameterisation, not as results.
