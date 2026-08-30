# Experiment Lab

This project is a home for experiments about decision-making and
quantum-cognition ideas. It does not treat a successful simulation as proof of
consciousness, Orch-OR, or quantum processing in a brain.

Every experiment must state five things before it is run:

1. **Hypothesis** — the precise claim that could fail.
2. **Data or simulation provenance** — where inputs came from and their limits.
3. **Classical baseline** — the simplest non-quantum account that must be beaten.
4. **Metric and split** — how success is measured without looking at the answer first.
5. **Interpretation boundary** — what a positive or negative result does *not* establish.

## Current catalogue

Run the local catalogue:

```bash
q-ai-gov experiments --list
q-ai-gov experiments --run snapshot-temporal-baseline \
  --data snapshot_dao_dataset.json --output experiment_result.json
```

The first runnable experiment is the Snapshot DAO temporal benchmark. The
following companion projects are catalogued as independent experiments rather
than copied into this package:

| Experiment | Companion project | Why it matters |
| --- | --- | --- |
| DAO vote sequences | `dao-governance-research` | Tests QQ equality and sequential voting controls. |
| Speed-dating decisions | `quantum-dating-research` | Tests order effects against real preference data. |
| Geopolitical alignment | `quantum-geopolitics-research` | Tests whether apparent dependence survives bloc controls. |
| Collective valuation | `collective-valuation-research` | Tests competing-answer dependence against exposure nulls. |

## Adding an experiment

Add a concise `Experiment` record to `q_ai_governance/experiment_lab.py`, and
add tests that make the result reproducible. A runnable experiment must expose
a small function that takes explicit inputs and returns a JSON-serializable
report. An external companion should be registered with `status="external
companion"`; the catalogue will link to it but never pretend that its code ran
inside this project.

Contributor results should include the seed, data version, source revision,
baseline result, and limitations. Negative results belong in the catalogue.
