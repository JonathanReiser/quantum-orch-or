# Corrections to this repository's empirical claims

**Dated 2026-08-30.** This file records claims previously published in this
repository, on Zenodo, and in grant proposals that the code does not support,
together with what the real data actually shows. It supersedes the numbers in
`README.md`, `full_quantum_governance_paper.md`, `EXECUTIVE_WHITEPAPER.md`,
`WEB3_QUANTUM_AI_PROTOCOL_PITCH.md`, `DAO_GRANT_PROPOSAL.md`,
`uniswap_grant_proposal.md`, `UNISWAP_GOVERNANCE_PROPOSAL.md`,
`Q_AI_COMMERCIAL_ACTION_PLAN.md`, `Q_AI_GOVERNANCE_SYNTHESIS.md`,
`PLATO_QUANTUM_GOVERNANCE.md`, and `q_ai_governance_paper.md` wherever they
disagree.

---

## 1. "Validated across 835,000 real Snapshot DAO votes"

**Not supported.** No such dataset existed anywhere in the repository. The
benchmark behind this figure, `benchmark_real_dao_data.py`, contained five
hardcoded proposals (`REAL_DAO_HISTORICAL_DATA`) with a combined turnout of
73,800. The number 835,000 does not appear in, and cannot be derived from, any
data or code in this project.

The forecast table in `UNISWAP_GOVERNANCE_PROPOSAL.md` was likewise a set of
hardcoded strings, not output from the benchmark it cited.

## 2. "86.7% error reduction, 1.3% MAE, R² = 0.98"

**Not supported, and partly impossible to obtain.**

* The MAE figures came from those same five hand-written proposals.
* Their two input features, `public_good_score` and `roi_score`, were assigned
  by the author *after* the outcomes were known. They are not observable before
  a vote, so any error computed from them is a description, not a forecast.
* The reported R² was clamped in code:
  `r2_score = float(max(0.0, min(0.98, r2_score)))`. The published "R² = 0.98"
  is the ceiling of that clamp, not a measurement. The same expression also
  silently converted every negative R² to 0.0.
* The model producing the "Q-AI" column was an untrained `QuantumOrchORAgent`
  with randomly initialised weights. `update_policy()` was never called by any
  prediction path, so the same proposal scored differently on every run.

## 3. "GHZ entanglement doubles public-good approval from 40% to 80%"

**Not what the code does.** In `governance_integration.py`, the GHZ statevector
is constructed and its probabilities computed — and then never read. The actual
mechanism is:

```python
if self.entangled_consensus and idx > 0:
    if np.random.rand() < 0.75:
        vote = votes[0]
```

That is a 75% chance of copying voter 0. It contains no entanglement and no
reference to the public good.

The quantity it moves is `consensus_metric = max(yes, no) / num_voters`, which
measures agreement in *either* direction. Copying one voter necessarily raises
it. Measured independently by `q_ai_governance/measure_ghz_effect.py`
(5 seeds x 20 proposals x 8 voters, impact vector `[0.9, 0.1]` — strong public
good, low private profit), toggling `entangled_consensus`:

| seed | YES off | YES on | ΔYES | consensus off | consensus on | Δconsensus |
|---|---|---|---|---|---|---|
| 0 | 90.0% | 80.6% | −9.4 | 90.0% | 95.6% | +5.6 |
| 1 | 99.4% | 100.0% | +0.6 | 99.4% | 100.0% | +0.6 |
| 2 | 95.0% | 91.2% | −3.7 | 95.0% | 97.5% | +2.5 |
| 3 | 93.1% | 90.0% | −3.1 | 93.1% | 97.5% | +4.4 |
| 4 | 94.4% | 95.6% | +1.3 | 94.4% | 95.6% | +1.3 |
| **mean** | **94.4%** | **91.5%** | **−2.9** | **94.4%** | **97.2%** | **+2.9** |

Consensus rose in **5 of 5 seeds** — it cannot do otherwise, because a copy
operation mechanically increases `max(yes, no)`. The public-good YES rate rose
in only **2 of 5 seeds** and *fell* on average, by 2.9pp.

So the mechanism reliably manufactures agreement and, if anything, slightly
reduces public-good approval. The published claim reports the first as though it
were the second. They are different quantities, and only one of them moves.

There is also no 40% baseline anywhere near this configuration: un-entangled
public-good approval measures 94.4%, not 40%.

## 4. "R² = 0.98 fitting Gallup question order effects, 84% on the Linda problem"

**Not supported.** In `benchmark_human_cognition.py` these are literals:

```python
q_simulated_rate = 0.84   # the "84% Linda accuracy"
r2_classical = 0.32
r2_quantum   = 0.98       # the "98% coefficient of determination"
```

No regression is run and no fit is performed. The quantum circuit's actual
conjunction-fallacy output (`q_fallacy_score`) is computed and discarded.

The accompanying "QQ equality" test is circular: it evaluates
`|(p_YY + p_NN) − (q_YY + q_NN)|` on the empirical Gallup values alone
(0.489 + 0.172 = 0.661 and 0.563 + 0.098 = 0.661). It compares the dataset to
itself and is zero by construction. The model never enters the comparison.

## 5. "92.8% directional accuracy" on crypto price forecasts

**Not supported.** In `quantum_crypto_engine.py` (and its byte-identical copy in
`q_ai_governance/`) these are literals:

```python
"q_ai_directional_accuracy": 92.8,   # Empirical test accuracy
"classical_directional_accuracy": 64.2,
```

The comment says "Empirical test accuracy". There is no backtest, no price
history, and no held-out evaluation anywhere in the repository that could
produce either number.

## 6. The on-chain "quantum proof" oracles verify nothing

**Not supported.** `submitQuantumNonProfitProof` is `onlyOwner` and accepts
`impactScore` and `qiskitProofHash` as arguments. Nothing checks that the hash
corresponds to any computation, or that the score came from one. The only
requirement is that the owner-supplied number clears the owner-defined
threshold.

`q_ai_giving_engine.py` derives its "proof" hash from
`f"BASE-Q-GIVING:{charity_id}:{impact_score}:BASE-PUBLIC-GOODS"` with
`impact_score` defaulting to `8850`. The hash commits to the claim, not to
evidence for it. The claim that this "doubles charitable grant allocation
efficiency" has no support in either repository.

The same pattern appears in this repository. `q_ai_governance/uniswap_v4_hook_oracle.py`
builds its "Qiskit proof hash" as:

```python
raw_str = f"Q-AI-PROOF:{proposal_id}:{consensus_score}:GHZ-ENTANGLEMENT-80-PCT"
proof_hash = "0x" + hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
```

The hash is taken over the asserted `consensus_score` and a constant string. It
is a commitment to the number being submitted, not evidence that any quantum
computation produced it. A verifier who recomputes the hash learns only that the
submitter typed that number. Neither oracle establishes anything about the
computation it names.

## 7. The agent trainer can report a converged fit while having learned nothing

Not a published claim, but it undermines the one honest number this project had.

`q_ai_governance/train_uniswap_governance_agent.py` fits weights with a (1+1)
hill climb whose objective is estimated from a small number of stochastic
rollouts, so every loss measurement is noisy. It scores the incumbent **once**
and thereafter compares every fresh candidate against that single measurement:

```python
loss = _train_loss(weights, bias, train_examples, n_rollouts)   # measured once
for _ in range(n_iters):
    cand_loss = _train_loss(cand_w, cand_b, train_examples, n_rollouts)
    if cand_loss < loss:                     # incumbent never re-measured
        weights, bias, loss = cand_w, cand_b, cand_loss
```

If that first measurement happens to land low, no candidate can ever beat it and
the search accepts nothing for the entire run. The failure is silent: the loss
history goes flat, which is indistinguishable from convergence.

This is not hypothetical. The first run of the new Snapshot benchmark used the
same structure and accepted **zero moves in 60 iterations**, reporting an
identical loss of 1261.54 at every checkpoint — a perfectly flat curve that
reads as convergence but means the reported "fitted" weights were still the
random initialisation.

Re-scoring the incumbent on a fresh seed each iteration (one extra evaluation
per step) removes the ratchet, and `q_ai_governance/benchmark_qai_real.py` now
does this and reports the accepted-move count so a dead search cannot pass as a
converged one. With the fix the loss visibly moves (1250.83 → 1525.59 → 1471.14
→ 1309.41), which is what exposes the real problem: at 8 rollouts per proposal
the estimator's noise is larger than any improvement the search could resolve,
so it still accepted 0 of 40 moves. Distinguishing "converged" from "never
moved" requires reporting the accepted-move count; a loss curve alone cannot.

The previously reported 32.74pp leave-one-out error for the trained agent was
produced by the un-fixed procedure and should not be treated as a fit.

---

## What the real data shows

`q_ai_governance/fetch_snapshot_dataset.py` pulls the actual record from the
Snapshot GraphQL hub. Every closed proposal from the five DAOs the claims name:

| | |
|---|---|
| Closed proposals retrieved | 1,864 |
| Kept (settled tally, unambiguous binary ballot) | **905** |
| Dropped as not cleanly binary | 955 |
| Dropped (unsettled or untallied) | 4 |
| Vote records across kept proposals | **6,242,940** |
| Date range | 2020-09-11 to 2026-08-20 |
| Fetched | 2026-08-30 |

Per DAO: Arbitrum 344, Aave 211, Gitcoin 139, Uniswap 123, Optimism 88.

**The distribution is the finding.** DAO votes overwhelmingly pass:
the median proposal carries **99.75% YES**, and 74% of proposals clear 90% YES.
This makes the prediction task very different from the one the published claims
describe.

`q_ai_governance/benchmark_snapshot_real.py` evaluates on a temporal split —
fit on the earlier 633 proposals, test on the later 272 — so nothing is
predicted with hindsight. R² is reported as computed, including when negative.

| model | MAE (pp) | RMSE (pp) | R² |
|---|---|---|---|
| constant (train mean) | 21.66 | 26.55 | −0.109 |
| **constant (train median)** | **10.44** | 26.73 | −0.125 |
| per-DAO historical mean | 17.26 | 24.55 | 0.052 |
| ridge on pre-vote features | 11.20 | 25.04 | 0.013 |

The best mean absolute error on real data comes from ignoring the proposal
entirely and predicting the historical median every time. A ridge model given
DAO identity, proposal length, ballot shape, voting-window length, quorum, and
the DAO's own prior approval history does **worse** than that constant, and
every R² sits within noise of zero.

That is the honest headline: **from information available before a vote closes,
the YES share of a DAO proposal is close to unpredictable beyond "it will
probably pass."** No model in this repository beats that, and the previously
published 1.3% MAE and R² = 0.98 are not attainable on the real record.

### The quantum agent on the same split

`q_ai_governance/benchmark_qai_real.py` puts `QuantumOrchORAgent` on exactly the
same temporal split, fed the same standardised pre-vote features.

| model | MAE (pp) | RMSE (pp) | R² |
|---|---|---|---|
| constant (train median) — best classical | **10.44** | 26.73 | −0.125 |
| Q-AI agent, random initialisation | 42.98 | 47.59 | −2.564 |
| Q-AI agent, after 40 fitting iterations | 28.07 | 32.62 | −0.675 |

Both are far worse than predicting a constant, and both R² values are strongly
negative — meaning the agent's predictions are worse than the test-set mean.

**The bottom row is not a trained model.** The fit accepted **0 of 40** proposed
moves, so those weights are still the initial random draw; only the seed differs
from the row above it. The 15pp gap between the two Q-AI rows is therefore the
spread between two random initialisations, not the effect of learning — which is
itself a measure of how much an unfitted agent's output depends on nothing but
its starting weights.

The fit did not stall because of the ratchet in §7 — that was fixed before this
run, and the incumbent's re-measured loss visibly moves (1250.83 → 1525.59 →
1471.14 → 1309.41 across the run). It stalled because at 8 rollouts per
proposal the loss estimator's own noise (±275 MSE, roughly 35–39pp RMSE) is
larger than any improvement the search could resolve. At this budget the fit is
not identifiable.

None of this rescues the retracted numbers, and none of it is needed to reject
them: ridge regression is a strong linear baseline, it was given the same
features, and it already found essentially no signal (R² = 0.013). A two-qubit
policy over those same features cannot recover signal that is not there. The
Q-AI rows confirm the classical result rather than adding to it.

---

## Status of external citations

* **Zenodo DOI 10.5281/zenodo.22151233** — the record is real and resolves
  (published 2026-08-29). Its abstract repeats the 835,000-votes, 86.7%,
  R² = 0.98, and 40%→80% claims, all of which are corrected above. The record
  needs a corrected version or a withdrawal.
* Correction sent: PsyArXiv withdrawal.
* Corrections still outstanding: Uniswap, Arbitrum, Base.

## Reproducing

```bash
python3 q_ai_governance/fetch_snapshot_dataset.py --out data/snapshot_dao_dataset.json
python3 q_ai_governance/benchmark_snapshot_real.py
python3 q_ai_governance/benchmark_qai_real.py
```
