# Can anything rank DAO proposals by how contested they will be?

**2026-09-04. No. Not at this band, and not with this test set.**

```bash
python3 q_ai_governance/benchmark_narrow_contestedness.py
python3 q_ai_governance/sensitivity_yes_share_definition.py
```

Pre-registered in [PREREGISTRATION_narrow_contestedness.md](PREREGISTRATION_narrow_contestedness.md)
and committed before the analysis ran. Every number below comes from
[`data/benchmark_narrow_contestedness_results.json`](data/benchmark_narrow_contestedness_results.json).

## The question

This replaces the retracted claim that the model predicts a proposal's final YES
share (it does not — 32.74pp MAE, see [CORRECTIONS.md](CORRECTIONS.md)) with a
weaker one that might have held: can proposals be *ranked* by how contested they
will be?

> **contested** ⟺ final YES share ∈ **[40%, 60%]**. Locked.

This is a much stricter band than the [5%, 95%] used in
[CONTESTEDNESS.md](CONTESTEDNESS.md), which counts a 6%-YES landslide as
"contested". [40%, 60%] means the vote was genuinely close. **The two documents
answer different questions and their numbers are not comparable.**

The cost of the stricter band is prevalence. Of 713 proposals surviving the
filters, 42 are contested (5.89%); in the test set, **9 of 214** (4.21%).

## Result: all three score functions fail

Temporal split on proposal **end** date, 499 train / 214 test, 2,000-sample
bootstrap CIs, 10 weight seeds. **AUC null is 0.5. PR-AUC null is the 0.042
prevalence, not 0.5.**

| model | ROC-AUC | 95% CI | P(AUC ≤ 0.5) | PR-AUC (null 0.042) |
|---|---|---|---|---|
| trivial constant | 0.500 | [0.500, 0.500] | 1.000 | 0.042 |
| logistic regression | 0.622 | [0.337, 0.880] | 0.179 | 0.194 |
| quantum — point estimate (a) | 0.482 | [0.407, 0.528] | 0.868 | 0.044 |
| quantum — rollout dispersion (b) | 0.419 | [0.337, 0.504] | 0.967 | 0.038 |
| quantum — coherence at collapse (c) | 0.382 | [0.318, 0.458] | 1.000 | 0.037 |

Pre-registered criterion — CI lower bound > 0.5 **and** point estimate above the
logistic baseline:

| score function | CI > 0.5 | beats logistic | verdict |
|---|---|---|---|
| point estimate | no | no | **FAIL** |
| rollout dispersion | no | no | **FAIL** |
| coherence at collapse | no | no | **FAIL** |

The hypothesis behind (b) and (c) — that the machinery is better at representing
*uncertainty* than at point prediction — is not supported. Both land below the
point estimate they were meant to improve on.

## The honest reading is not "classical won"

The logistic baseline's CI is **[0.337, 0.880]**. It covers 0.5. The classical
model does not clear chance either.

So this is not quantum-loses-to-classical. **Nothing here resolves at this band.**
With 9 positives in the test set, the data cannot distinguish a useful ranker
from a coin, and no amount of modelling fixes that. The binding constraint is
`n_contested_test = 9`, and it is the first thing that would have to change.

## A single seed would have manufactured a result

The engine's weights are random at initialisation. The pre-registration required
10 seeds and the median, specifically so one draw could not become a headline.
It would have:

| score function | median | min | max | seeds above 0.5 |
|---|---|---|---|---|
| point estimate | 0.482 | 0.195 | 0.755 | 4 / 10 |
| rollout dispersion | 0.419 | 0.170 | 0.755 | 4 / 10 |
| coherence at collapse | 0.382 | 0.165 | 0.775 | 4 / 10 |

Every score function exceeds chance on 4 of 10 seeds and reaches ≈0.76 on its
best one. **A single-seed run had a 40% chance of producing an above-chance
number, and could have reported AUC 0.76 as a discovery.** That is the
methodological finding here, and it generalises past this repo.

It also means the CIs in the first table are narrower than the real uncertainty:
they resample test rows while conditioning on these 10 fixed seeds. The interval
for (c), [0.318, 0.458], excludes 0.5 on the low side, but **this is not evidence
of a reliable inverted signal** — that same score function ranges from 0.165 to
0.775 depending only on the random draw.

## Why accuracy is not reported

Always predicting "not contested" is **95.8% accurate** (1 − prevalence), with an
AUC of exactly 0.500 and a PR-AUC of exactly 0.042. At this prevalence accuracy
measures the base rate and nothing else, which is why the pre-registration made
AUC the headline before any number existed.

PR-AUC is what exposes the practical uselessness that ROC-AUC hides: logistic's
0.194 against a 0.042 null is the only figure in the table that is meaningfully
above its baseline, and its ROC-AUC still cannot clear chance.

## What the "quantum" score functions actually are

Established by probe (`tools/probe_engine_degeneracy.py`) and recorded in the
pre-registration **before** any result, so it cannot read as an after-the-fact
excuse:

* Given a fixed observation, `coherence_at_collapse` and the step count are
  **deterministic** — std `0.000e+00` across 50 rollouts.
* The initial circuit applies only per-qubit `rx`/`ry`: **no entangling gates**,
  so the state is a product state.
* The ZZ coupling accumulates **7.6e-04 rad** over an entire run. It is
  numerically inert; the evolution is indistinguishable from identity.

So the engine is a deterministic nonlinear map from the observation to a fixed
probability vector, plus one multinomial draw. All three score functions are a
**fixed random nonlinear feature map**. Had any of them scored well, that would
have been evidence about random feature maps, not about Orch-OR — which is why
the pre-registration committed to describing it that way in advance.

## Sensitivity: the YES-share denominator

The task brief defines YES share as `yes_vp / scores_total`, which **includes**
abstentions. This repo's own `fetch_snapshot_dataset.py:133` uses
`yes_vp / (yes_vp + no_vp)`, which **excludes** them. They disagree on **694 of
905** proposals by up to **55 percentage points**. The pre-registration
originally contained both, contradictorily; see Amendment 1.

The primary analysis keeps the brief's formula. The alternative is a
**sensitivity analysis, not pre-registered**, holding the model and its scores
fixed and swapping only labels
([`data/sensitivity_yes_share_definition.json`](data/sensitivity_yes_share_definition.json)):

| model | A: incl. abstain (9 contested) | B: excl. abstain (3 contested) |
|---|---|---|
| logistic | 0.622 [0.337, 0.880] | 0.559 [0.141, 0.810] |
| quantum — point | 0.482 [0.407, 0.528] | 0.414 [0.188, 0.596] |
| quantum — dispersion | 0.419 [0.337, 0.504] | 0.409 [0.215, 0.439] |
| quantum — coherence | 0.382 [0.318, 0.458] | 0.377 [0.262, 0.410]  |

The conclusion is unchanged, and definition B is worse still: **3** contested
proposals in the test set. The re-derivation of A from the persisted raw scores
matches the committed primary exactly (max drift `0.00e+00`).

## What would actually be needed

Not a better model. More positives.

1. **More contested proposals.** 9 is not enough for any method. That means many
   more spaces, or many more years, not a cleverer estimator.
2. **Features describing the proposal.** [CONTESTEDNESS.md](CONTESTEDNESS.md)
   already showed the wider-band signal was venue, not proposal — `duration_days`
   fingerprints which DAO ran the vote. The body text is not even persisted in
   this dataset (only `body_len`), so nothing here reads what a proposal says.
3. **A reason to expect the engine to help.** With no entangling gates and an
   inert coupling, there is no mechanism by which this architecture would beat a
   random feature map.

## Reproducing

```bash
python3 tools/probe_engine_degeneracy.py
python3 q_ai_governance/benchmark_narrow_contestedness.py
python3 q_ai_governance/sensitivity_yes_share_definition.py
python3 -m pytest tests/test_narrow_contestedness.py -q
```

21 tests pin these numbers. Each was mutation-checked to confirm it can fail:
widening the band to [5, 95], dropping PR-AUC's tied-block handling, clamping
AUC to ≥ 0.5, and de-temporalising the split were each applied and each broke
the matching test.

The engine pass takes about two hours. `data/narrow_contestedness_raw_scores.npz`
holds the raw per-seed test-set scores so any re-analysis that changes only
labels needs no re-run.
