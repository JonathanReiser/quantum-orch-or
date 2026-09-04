# Pre-registration — narrow-band contestedness, quantum vs classical

**Written 2026-09-04, committed before any model was fitted or any metric computed.**
Everything below is fixed at the moment of this commit. Nothing in it may be
changed once results exist; if something here turns out to be a bad choice, the
bad choice gets reported alongside the result rather than quietly repaired.

Task brief: rank closed Snapshot DAO proposals by how *contested* they will be.
This replaces the retracted point-prediction claim (predicting final YES share,
which failed at 32.74pp MAE — see `CORRECTIONS.md`).

## Disclosure of what was already known at write time

Honesty requires listing what had been looked at before this file was written,
because a pre-registration written with results already in hand is worthless.

1. **The band was locked externally, by the task brief, not chosen by me.** It is
   `[0.40, 0.60]`, and it was fixed before any of this ran.
2. **The label prevalence was computed before this file was written**: under the
   locked band and the turnout filter below, 26 of 861 proposals are contested
   (3.0%). This is a property of the labels alone. No model had been fitted, no
   split made, and no metric computed. It is disclosed because it is the one
   number I saw early, and because it is bad news that I want on the record
   *before* the results rather than as an excuse after them.
3. **The engine was probed for degeneracy before this file was written** — see
   "Known properties of the engine" below. Those probes touched no labels.
4. An **earlier, different** analysis exists in this repo (`CONTESTEDNESS.md`),
   using a much wider band `[0.05, 0.95]` and no quantum score functions. Its
   band is *not* the band here and its numbers are not comparable. This
   pre-registration does not reuse, extend, or defend it.

## Locked definitions

* **contested** ⟺ final YES share ∈ `[0.40, 0.60]`, inclusive. **Locked.**
  YES share = `yes_vp / scores_total`, as persisted in the committed dataset.
* **Dataset**: `data/snapshot_dao_dataset.json`, fetched 2026-08-30T15:08:41Z
  from `https://hub.snapshot.org/graphql`, 905 closed proposals across 5 spaces.
  Every number below must be reproducible from that committed file with no
  network access.
* **Filters**, applied in this order:
  1. binary-ish only — `len(choices) <= 3` with a For-like and Against-like
     choice. (The fetch already dropped 955 multi-option/ranked proposals.)
  2. turnout — `voter_count >= 100`.
* **Minimum usable n**: 150 proposals after filtering. Below that: report and
  stop, no point estimate. *(n = 861 after filtering, so this gate passes.)*
* **Split**: temporal, never random. Sort ascending by proposal **end** date;
  earliest 70% train, latest 30% test. The split timestamp is recorded in the
  results file.
* **Seed**: `20260904`, fixed and recorded in the results file.

## Score functions to compare

All three are computed from `QuantumOrchORAgent.deliberate_and_act`, fed the
**identical** feature vector the logistic baseline sees (`state_dim` = n
features). Higher score = more contested, for every function.

* **(a) point estimate** — `1 - |yes_frac - 0.5| * 2`, where `yes_frac` is the
  fraction of 50 rollouts collapsing to an even basis index (the repo's existing
  YES convention). Expected to be weak; it is the mechanism that already failed.
* **(b) rollout dispersion** — Shannon entropy of the collapsed-index
  distribution over 50 rollouts.
* **(c) coherence at collapse** — `coherence_at_collapse`, which
  `deliberate_and_act` already returns and which nothing in the repo currently
  consumes.

All three are reported. The winner is not selected and reported alone.

## Mandatory baselines

1. **trivial** — constant "not contested" (present to show accuracy is useless
   at 3% prevalence, not as a serious competitor).
2. **logistic regression** on the **identical** features, L2, standardised on
   train only.
3. the three quantum score functions above.

If (3) does not beat (2), **that is the headline finding** and gets reported
plainly as such.

## Metrics

* **ROC-AUC** with a 95% CI from **2,000** bootstrap resamples of the test set.
  Never a bare point estimate. **Null is 0.5** and is restated every time.
* **PR-AUC / average precision**, always printed next to the **positive-class
  prevalence**, which is its null baseline — *not* 0.5. At ~3% prevalence ROC-AUC
  can look respectable while the model is useless in practice; PR-AUC is what
  exposes that.
* **n_train, n_test, n_contested_test** reported. If `n_contested_test` is small,
  say so loudly and treat every interval as unstable.
* AUC is a **ranking** metric and says nothing about calibration. Scores are
  never described as probabilities.

## Success criterion

> ROC-AUC 95% CI **lower bound > 0.5** *and* the point estimate **exceeds the
> logistic baseline**.

Anything else is a **negative result**, which is a real result and is reported as
one.

## Pre-registered robustness check

The agent's weights are **random at init** and are not trained here. A single
random draw is therefore a hidden researcher degree of freedom: one lucky seed
could manufacture a positive result. So the entire quantum evaluation is repeated
over **10 weight seeds** (`20260904 + 0..9`), and the **full distribution** of
AUCs is reported, not the best one. The headline quantum number is the **median**
across seeds.

## Known properties of the engine, established by probe before any result

Recorded here so they cannot be presented later as discoveries that happen to
explain away a bad number. Probes are in `tools/probe_engine_degeneracy.py`.

* Given a fixed observation, `coherence_at_collapse` and the step count are
  **deterministic** (std ≈ 4e-16, i.e. floating-point zero, over 50 rollouts).
* The **only** stochastic element is the final `np.random.choice` over a
  probability vector that is itself a deterministic function of the observation.
  So score (b)'s 50 rollouts are a Monte-Carlo estimate of a quantity computable
  exactly from the statevector; the rollout noise is added by the estimator, not
  by the model.
* The initial circuit applies only per-qubit `rx`/`ry` — **no entangling gates**,
  so the state is a product state.
* The ZZ coupling accumulates a total phase of ~2.1e-04 rad over a full run,
  i.e. the "coupling" term is numerically inert; the evolution is
  indistinguishable from identity.

Consequence, stated in advance: all three score functions are deterministic
nonlinear transforms of the input features (up to rollout sampling noise in (a)
and (b)). Whatever they achieve, the mechanism is a **fixed random nonlinear
feature map**, not quantum uncertainty. A positive result would have to be
described that way, and would not be evidence for the Orch-OR framing.

## Guardrails (failure modes already found in this repo)

* **No clamping.** `benchmark_real_dao_data.py:128` does
  `max(0.0, min(0.98, r2_score))`, capping reported R² at 0.98 and flooring a
  negative R² to 0.0. Nothing here clamps any metric.
* **No hardcoded metrics.** `quantum_crypto_engine.py:84` contains
  `"q_ai_directional_accuracy": 92.8` — a literal no measurement produces. Every
  number emitted here traces to a computation over the committed dataset.
* **No tautological tests.** `tests/test_quantum_economics.py:19` asserts
  `order_effect_delta >= 0.0` on an `abs()` value, which cannot fail. Tests
  written for this must be able to fail.
* Results go to a committed JSON carrying the full config — seed, band, split
  timestamp, feature definitions, all n's. Prose anywhere else cites that file.
