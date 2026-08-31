# Which DAO proposals get contested?

**2026-08-31.** A follow-up to the negative result in
[CORRECTIONS.md](CORRECTIONS.md).

```bash
python3 q_ai_governance/benchmark_contestedness.py
```

## Why ask a different question

The corrected benchmark shows that predicting a proposal's YES *share* is close
to hopeless: 74% of proposals clear 90% YES, so the variance mostly is not there,
and nothing beats predicting the historical median.

That may be the wrong question rather than a dead end. Most DAO proposals are
rubber stamps. The interesting ones are the minority that are actually fought
over, so:

> **contested** ⟺ final YES share falls in [5%, 95%]

Base rate is 26.5% across the 905-proposal dataset, and it varies sharply by
venue — Optimism 47.7%, Arbitrum 40.1%, Uniswap 17.9%, Gitcoin 12.2%, Aave 10.0%.

Two hazards, both handled rather than hidden:

* **The base rate shifts across the temporal split**, 30.0% in train to 18.4% in
  test. Threshold metrics like accuracy would flatter every model, so AUC —
  rank-based and invariant to that shift — is the headline.
* **If the venue carries all the signal**, then "we can predict contestedness"
  really means "Optimism argues more than Aave." So venue-only and content-only
  models are fitted separately and compared.

## There is real signal

Temporal split, 633 train / 272 test, 2,000-sample bootstrap CIs:

| model | AUC | 95% CI | P(AUC ≤ 0.5) |
|---|---|---|---|
| base rate constant | 0.500 | — | — |
| per-DAO base rate | 0.628 | [0.527, 0.719] | 0.0095 |
| **all features** | **0.660** | [0.555, 0.763] | 0.0010 |
| content only | 0.651 | [0.547, 0.755] | 0.0010 |
| venue only | 0.651 | — | — |

Unlike YES-share, this is genuinely predictable above chance. The confidence
interval excludes 0.5, and it survives a shifting base rate. AUC 0.66 is modest —
useful for triage, not for anything consequential — but it is real.

## But the signal is the venue, not the proposal

The pooled content-only model reaches 0.651 without seeing DAO identity at all,
which looks like evidence that something about a *proposal* predicts whether it
will be fought over. It is not. Fitting and testing that same model **inside each
DAO**:

| DAO | n | contested | content-only AUC | median duration, contested / uncontested |
|---|---|---|---|---|
| Uniswap | 123 | 17.9% | 0.516 | 5.00d / 5.00d |
| Arbitrum | 344 | 40.1% | 0.416 | 7.00d / 7.00d |
| Optimism | 88 | 47.7% | 0.541 | 12.08d / 6.96d |
| Gitcoin | 139 | 12.2% | 0.188 | 7.00d / 7.00d |
| Aave | 211 | 10.0% | 0.137 | 4.97d / 3.00d |

**Median within-DAO AUC: 0.416.** Below chance. The pooled result is Simpson's
paradox.

The mechanism is visible in the last column. The strongest content feature was
`duration_days` (standardised coefficient +0.50), but Uniswap, Arbitrum and
Gitcoin show *identical* median durations for contested and uncontested
proposals — those DAOs run a fixed voting window. Duration therefore does not
describe a proposal at all; it is a fingerprint identifying which DAO the
proposal belongs to, and DAO predicts contestedness. Pool the venues and the
correlation appears; condition on venue and it vanishes.

## The honest result

1. **Contestedness is predictable above chance**, at AUC ≈ 0.63–0.66, with the
   confidence interval excluding 0.5.
2. **All of that is venue.** Knowing which DAO a proposal belongs to is worth
   essentially everything; knowing anything about the proposal itself adds
   nothing once you condition on the venue.
3. So the practical content is a statement about organisations, not proposals:
   **some DAOs argue and others rubber-stamp, and this is stable enough to
   forecast.** Which proposal is in front of them does not measurably change
   that.

This is consistent with the YES-share result rather than a rescue of it. Both say
the same thing from different directions: at the level of individual proposals,
the pre-vote features available here carry no usable signal.

## Reproducing

```bash
python3 q_ai_governance/benchmark_contestedness.py
python3 -m pytest tests/test_contestedness.py -q
```

Seven tests pin these numbers, including the within-DAO collapse and the
fixed-voting-window confound — the two claims most easily and most misleadingly
erased by a later change.
