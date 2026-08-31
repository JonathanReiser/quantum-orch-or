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
