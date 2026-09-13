# Result — the somatic gamma map's constants decide the answer

Pre-registered in [`PREREGISTRATION_gamma_map.md`](PREREGISTRATION_gamma_map.md),
committed at `f232bb8` before the grid ran. Two amendments, both recorded there
before any number below was written. Every figure here traces to
[`data/gamma_map_sensitivity.json`](data/gamma_map_sensitivity.json), produced by
`tools/gamma_map_sensitivity.py`.

Run with qiskit 1.3.0, qiskit-dynamics 0.6.0, numpy 2.5.3. 120 grid cells.

## Headline

**Four of the five pre-registered quantities are FRAGILE. The one that is
ROBUST is robust because it is vacuous.**

| quantity | what it stands for | spread across 120 cells | verdict |
|---|---|---|---|
| **Q1** coherence at `t = 5 s` | *"after 5 s a stressed subject has lost X coherence"* | `0.0111 → 0.7788` (**70×**) | **FRAGILE** |
| **Q2** coherence half-life | *"coherence half-life is X seconds"* | `0.77 s → 9.24 s` (**12×**) | **FRAGILE** |
| **Q3** rank corr. HRV-loss vs coherence | *"lower HRV means faster coherence loss"* | `−1.00 → −0.50` | **FRAGILE** (sign always correct) |
| **Q4** coherence at `gamma*t = 2` | the same physics in the system's own time units | `0.367879 → 0.367916` (**1e-4**) | **ROBUST** |
| **Q5** purity change from the intervention | *"the intervention changes the outcome"* | `−1.1e-05 → +0.0342`, **sign flips** | **FRAGILE** |

## What this means, stated plainly

**Any claim in seconds is arbitrary.** Q1 and Q2 are the shape every readable
claim about this bridge would take. Feed the *identical* physiological input —
a 50% drop in HRV — into the same code, and the reportable answer moves by a
factor of 70, purely by choosing `floor` and `scale` differently. Nothing in
the repository says which choice is right, because nothing derives these
constants from anything. "Coherence half-life is 3.3 seconds" is true at the
defaults and equally true at 0.77 s or 9.24 s elsewhere in the grid.

**The robust quantity carries no information.** Q4 is invariant to 1 part in
10⁴ — but only because coherence at `gamma*t = 2` is `exp(−1)` for *every*
subject, every cell, every input. It is a property of the exponential, not of
the person wearing the watch. Stating conclusions in dimensionless time makes
them constant-independent and simultaneously drains them of physiological
content. **Robustness here is not reassurance.**

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

**`floor = 0` is degenerate.** In 12 of 120 cells the half-life is undefined
because `gamma = 0` at rest means no dynamics at all. Reported, not dropped.

## Two bugs found in this analysis, both before results were written

Recorded because the pre-registration required it, and because the second one
matters beyond this study.

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
