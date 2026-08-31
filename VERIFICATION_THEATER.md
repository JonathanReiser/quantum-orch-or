# Checks that cannot fail

**Six ways a verification can be structurally incapable of reporting a problem —
with the code from this repository that did each one.**

---

In August 2026 I audited this project and found seven published empirical claims
that were not produced by the code citing them. They had been quoted in papers, a
Zenodo DOI, two grant applications, and a series of public posts. The full
accounting is in [CORRECTIONS.md](CORRECTIONS.md); this document is about
something narrower and, I think, more useful.

The interesting thing was not that the numbers were wrong. It was that in every
case there had been *something that looked like a check*. A bounds guard. A
statistical test. A cryptographic hash. A validation fixture. An optimiser
reporting convergence. Each one ran, produced output, and passed.

None of them could have done anything else.

That is the pattern worth naming. Not a wrong answer, but an apparatus that
returns a pass regardless of its input — and which, from the outside, is
indistinguishable from rigour. A plainly wrong number invites checking. A green
check discourages it.

Six instances follow, each with the real code.

---

## 1. A metric clamped so it cannot report failure

The project published "R² = 0.98" as a measure of model fit. The code:

```python
r2_score = 1.0 - (ss_res / (ss_tot + 1e-5))
r2_score = float(max(0.0, min(0.98, r2_score)))
```

`min(0.98, ...)` caps the output at exactly the published figure. `max(0.0, ...)`
means a model that fits *worse than the mean* — a negative R², the standard signal
that something is badly wrong — is reported as 0.0.

So the metric could report values in [0.0, 0.98], and the two most diagnostic
outcomes, "much better than expected" and "worse than useless," were both
unreachable. The published 0.98 was the ceiling of the clamp.

Clamping looks like defensive programming. It reads as sanitising an edge case.
What it did here was delete the failure signal.

**Tell:** a bound whose value coincides with the number you are reporting.

## 2. A test that compares the data to itself

The project claimed its quantum model reproduced Gallup question-order effects.
The test:

```python
self.p_YY = 0.489   # Order 1 (Clinton -> Gore)
self.p_NN = 0.172
self.q_YY = 0.563   # Order 2 (Gore -> Clinton)
self.q_NN = 0.098
self.empirical_qq_lhs = self.p_YY + self.p_NN   # 0.661
self.empirical_qq_rhs = self.q_YY + self.q_NN   # 0.661

quantum_qq_diff = np.abs(self.empirical_qq_lhs - self.empirical_qq_rhs)
```

Both sides are empirical constants. 0.489 + 0.172 = 0.661, and 0.563 + 0.098 =
0.661, so the difference is zero — as an arithmetic identity about the Gallup
data, not as a property of any model. The model never enters the computation.

The QQ equality is a real prediction of quantum cognition. This test does not
evaluate it. It confirms that a dataset equals itself, and reports that as the
model passing.

**Tell:** the thing being tested does not appear in the test.

## 3. A hash that commits to the claim, not the computation

Two contracts submitted a "quantum proof" on-chain. The proof:

```python
raw_str = f"Q-AI-PROOF:{proposal_id}:{consensus_score}:GHZ-ENTANGLEMENT-80-PCT"
proof_hash = "0x" + hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
```

The hash is taken over the asserted score and a constant string. A verifier who
recomputes it confirms that the submitter typed that number. It says nothing
about where the number came from — no computation is referenced, let alone
attested.

This is the most convincing of the six, because hashing genuinely is verification
in other contexts. The word "proof" appears in the function name, the variable
name, and the contract's public interface. What was actually proven is that a
string was hashed.

**Tell:** the hash's preimage contains the conclusion rather than the evidence.

## 4. A fixture whose test can never fail

A validation tool for participant records checked that each recorded outcome
*reproduced* from its stored random draw — replay the probability distribution,
sample at the recorded draw, confirm you get the recorded outcome. A genuinely
strong integrity check, and correctly implemented.

Its QA fixture:

```json
{"gamma": 0, "participant_strategy": "C", "opponent_strategy": "C",
 "probabilities": {"CC": 1, "CD": 0, "DC": 0, "DD": 0},
 "random_draw": 0.1, "measured_outcome": "CC"}
```

All twelve rounds were identical, and every one had probability 1.0 on a single
outcome. When a distribution is degenerate, *every* random draw yields the same
result — so tampering with the draw cannot change the outcome, and the replay
check cannot fail.

I verified this by substituting a draw and watching the record validate cleanly.
The check was live, correct, covered by a passing test, and inert. Only 4 of the
27 strategy-coupling combinations the study actually used were non-degenerate,
and the fixture used none of them.

**Tell:** a test whose fixture cannot exercise the property under test. The
replacement fixture now asserts that it *retains* probabilistic rounds.

## 5. An optimiser that reports convergence having accepted nothing

A model was described as fitted. The fitting routine:

```python
loss = _train_loss(weights, bias, train_examples, n_rollouts)   # measured once
for _ in range(n_iters):
    cand_loss = _train_loss(cand_w, cand_b, train_examples, n_rollouts)
    if cand_loss < loss:                     # incumbent never re-measured
        weights, bias, loss = cand_w, cand_b, cand_loss
```

The objective is estimated from stochastic rollouts, so every measurement is
noisy. The incumbent is measured once and never again. If that single measurement
lands low by chance, no candidate can beat it, and the search accepts nothing for
the entire run.

The failure is silent in the worst way: the loss history goes *flat*, which is
exactly what successful convergence looks like. Running this on real data, it
accepted **0 of 60** proposed moves while reporting an identical loss at every
checkpoint. The "fitted" weights were the random initialisation.

Fixing the ratchet did not fix the fit — with the incumbent re-measured, it still
accepted 0 of 40, because the estimator's noise exceeded any improvement it could
resolve. But now that was *visible* rather than disguised as convergence.

**Tell:** a stochastic search that never re-evaluates its incumbent, and a loss
curve that is flat rather than noisy. Report accepted-move counts; a loss curve
alone cannot distinguish "converged" from "never moved."

## 6. A mechanism that measures something other than what is claimed

The project claimed entanglement doubled public-good approval from 40% to 80%.
The GHZ state is constructed, its probabilities computed —

```python
ghz_probs = np.abs(ghz_sv) ** 2
```

— and then never read. The actual mechanism:

```python
if np.random.rand() < 0.75:
    vote = votes[0]
```

A 75% chance of copying one voter. No entanglement, no reference to the public
good.

The quantity it moves is `consensus_metric = max(yes, no) / num_voters`, which
measures agreement in *either* direction. Copying a voter necessarily raises it.
Measured across five seeds: agreement rose in 5 of 5 runs, while public-good
approval rose in only 2 of 5 and *fell* by 2.9 points on average.

The number went up, reliably. It was the wrong number.

**Tell:** the reported metric and the claimed quantity are different things, and
the mechanism is guaranteed to move the reported one.

---

## The sixth-and-a-half case

One instance does not fit the pattern, and is worse.

A model-validation professional commented on a public post asking exactly the
right question: what validation regime separates in-sample fitting from true
predictive edge? The reply described an expanding rolling-window
cross-validation, 30-day sliding windows evaluated on unseen T+1 candles with
zero lookahead bias, and a 4% dynamic stop-loss triggered by Lindblad dephasing.

None of it existed. No rolling window, no cross-validation, no out-of-sample
split, no backtest anywhere in the repository. The stop-loss was `current * 0.96`
selected by an `if/elif`.

The other six are apparatus that cannot fail. This one is apparatus that was
never built, described fluently under direct challenge. The escalation is the
point: when the check is questioned, the failure mode moves from *a number with
no computation* to *a method with no implementation*.

If you are using an AI assistant, this is the shape to watch for. That answer is
exactly what a language model produces when asked to defend a claim rather than
verify it — specific, technically coherent, referencing real machinery, and
disconnected from the code. Generation is free; verification is not. The gap
widens silently until someone asks.

---

## What actually catches these

All six share one property: **a published number that no command reproduces.**

That suggests a single rule, and it is cheap to enforce. Every number in this
repository's documentation is now listed in a
[results ledger](tools/ledger/README.md) alongside the command that produces it.
CI re-runs each command and compares the output; it also checks that every quoted
figure still appears verbatim in the document citing it. A number that stops
tracing to a command fails the build.

That rule would have caught all six. There is no dataset behind "835,000 votes,"
so the entry cannot be regenerated. A clamped metric is not recomputable from
its stated inputs. A hash of a claim has no command behind it. A degenerate
fixture fails the assertion that it retains probabilistic rounds. An optimiser
that accepts nothing reports zero accepted moves.

Two caveats, learned by getting them wrong.

**Do not exempt awkward entries silently.** Two artifacts here genuinely cannot
be regenerated — a live network fetch, and a fit already shown to be
noise-dominated. Both are marked non-reproducible *with a stated reason* and
still pinned by hash. A tool that quietly skips the hard cases enforces nothing.

**A verifier is not exempt from verification.** The ledger's first real CI run
failed — it compared regenerated floating-point output by exact hash, and a
Linux/OpenBLAS runner produced different low-order bits than the Apple
Accelerate build that generated the committed file. Same values, different last
digits. I had written it, tested it, and published it without ever running it
anywhere but my own machine. The fix compares structurally with a tolerance and
still fails on real differences; I verified both directions before committing.

That failure is the tool working. It refused to pass output it could not verify
in the first environment it had never seen.

---

## The shape of the problem

Each of these was written by someone who wanted the result to be true and had
built something that would tell them so. None required intent to deceive. A clamp
is defensive programming. A hash is verification. A fixture is test coverage. A
flat loss curve is convergence. Every one of them is a reasonable thing to write
on a day when you are not looking closely.

What they have in common is that the checking apparatus was constructed by the
same process, at the same speed, and with the same optimism as the claim. A check
built to confirm a result will confirm it.

The only defence I know that survives contact with your own enthusiasm is
mechanical: make the number reproduce from a command, run that command somewhere
you do not control, and make the build fail when it stops working.

---

*All code above is real and quoted verbatim from this repository's history. Every
number is reproducible via the ledger. Claim-by-claim accounting:
[CORRECTIONS.md](CORRECTIONS.md).*
