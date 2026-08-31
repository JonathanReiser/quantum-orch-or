# EWL mechanism-blind tournament

This is a reproducible control ladder for the Eisert--Wilkens--Lewenstein
(EWL) two-player Prisoner's Dilemma. Its first job is **not** to demonstrate
quantum advantage. It makes the closest ordinary alternative explicit.

## Conditions

1. **Classical** — the original C/D action game. This condition is unavailable
   when a player selects `Q`, because `Q` is not a classical action.
2. **Classical correlated** — ordinary pseudorandom sampling from the exact
   probabilities calculated by EWL for the declared strategies.
3. **EWL simulator** — the same EWL statevector calculation and outcome
   distribution, followed by ordinary sampling.
4. **Hardware adapter** — a non-result protocol record. It cannot be analysed
   until it contains a backend name, job ID, shot count, measurement counts, and
   transpilation metadata.

The correlated and simulator conditions intentionally use the same seed, so
their sampled event sequences must be identical. This is a check that the
classical control is matched; it is not evidence for quantum mechanics.

## Run it

```bash
q-ai-gov ewl-tournament --p1 C --p2 D --rounds 100 --seed 7 --output report.json
```

For a strategy using EWL's `Q` operator:

```bash
q-ai-gov ewl-tournament --p1 Q --p2 D --rounds 100 --seed 7 --output report.json
```

The report has every sampled event, expected distribution, configuration, and a
SHA-256 replay hash. It contains no made-up QPU measurements.

## Human-study extension

The next evidence-bearing stage should preregister and randomize people (or
agents) across the conditions. Keep payoff distributions matched between the
classical-correlated and EWL treatments; then test cooperation, welfare,
strategy calibration, and the effect of interface framing. Archive raw choices,
instructions, randomization, exclusions, and QPU job metadata before comparing
conditions.

Neither a simulator result nor a behavioral difference establishes a quantum
biological mechanism, consciousness, or Orch-OR.

## Participant-facing pilot

Open `study.html` from the static site, or select the EWL tournament in the
Experiment Lab and choose **Launch anonymous participant pilot**. The browser
pilot provides consent language, randomized backend and disclosure assignments,
12 balanced rounds, a full debrief, and optional JSON/CSV export. Nothing is
sent to a server.

The page is a protocol and interface pilot, not an approved human-subjects
study. Obtain any required ethics review before recruitment or research use.

## Researcher console

Open `researcher.html` to import one or more participant JSON records locally.
The console verifies the protocol, 12-round structure, strategies, EWL
probabilities, random-draw replay, payoffs, cumulative totals, treatment
consistency, SHA-256 integrity, and duplicate session IDs. Accepted sessions
are summarized across the four backend × disclosure arms and can be exported as
combined event CSV or descriptive-summary JSON. The console performs no
significance testing and uploads nothing.

## The coupling levels straddle the equilibrium threshold

Not by design, but worth recording. In the restricted two-parameter strategy
space the quantised Prisoner's Dilemma acquires a cooperative equilibrium only
above an entanglement threshold, derived in closed form from the binding
deviation as

    cos^2(gamma_c) = (R - S) / (T - S) = 3/5,   gamma_c = arccos(sqrt(3/5))
                                              ~ 0.684719 rad ~ 39.23 deg

(derivation and numerical confirmation in `q_ai_governance/ewl_equilibrium.py`
on `main`). The pilot's three coupling levels fall either side of it:

| coupling | gamma | vs threshold | Q against D pays | better play |
|---|---|---|---|---|
| low | 0.000 | below | 0.00 | D |
| medium | 0.785 | above | 2.50 | Q |
| high | 1.571 | above | 5.00 | Q |

So the strategy that pays flips between `low` and the other two levels. If the
pilot is ever run with participants, that gives it a falsifiable prediction it
was not built to test: Q adoption should rise across the threshold, not merely
with coupling.

Two caveats on reading that. Nothing is sampled between gamma = 0 and
gamma = 0.785, so the data could only bracket the crossing, never locate it —
levels near 0.5 and 0.9 would be needed for that. And this is a claim about
whether people find equilibria in an unfamiliar payoff structure, not about
quantum cognition; the two backends are probability-matched by construction, so
that arm manipulates framing rather than mechanism.

## A limit of the replay check

Most strategy and coupling combinations produce a deterministic outcome — only
4 of the 27 the pilot uses are probabilistic, all at medium coupling. On a
deterministic round the recorded `random_draw` does not affect the result, so
altering it cannot be detected. It also cannot change anything, which is why the
validator does not treat it as an error. The QA fixtures deliberately contain
probabilistic rounds so that the replay check is exercised rather than vacuous;
`tests/test_research_core_integrity.js` asserts that property is retained.
