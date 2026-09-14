# Quantum-Orch-OR research sandbox

[![Tests](https://github.com/JonathanReiser/quantum-orch-or/actions/workflows/tests.yml/badge.svg)](https://github.com/JonathanReiser/quantum-orch-or/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains exploratory governance models, open-system simulations,
and reproducibility tooling. Quantum formalism is used as a mathematical
modeling language. The repository does **not** establish that cognition is
quantum, validate Orch-OR as neuroscience, demonstrate quantum advantage, or
provide a medical or financial product.

## Read this first

An audit found that several previously promoted empirical claims were not
produced by the code that cited them. The claims—including 835,000 analyzed DAO
votes, an 86.7% error reduction, R² = 0.98, and a 40% → 80% approval
improvement—are retracted.

- [Corrections](CORRECTIONS.md) is the authoritative record.
- [Checks that cannot fail](VERIFICATION_THEATER.md) explains the verification
  failures that allowed the claims through.
- [Historical publications](archive/README.md) are retained for transparency,
  not as current evidence.

## Current evidence

| Study | Result | Reproduction |
| --- | --- | --- |
| [DAO vote-share benchmark](CORRECTIONS.md#what-the-real-data-shows) | The dataset contains 905 closed, cleanly-binary proposals and 6,242,940 vote records. On a temporal split, the historical median (**10.44 pp MAE**) beats the tested pre-vote models. | `python3 q_ai_governance/benchmark_snapshot_real.py` |
| [Contestedness](CONTESTEDNESS.md) | AUC 0.660, 95% CI [0.555, 0.763], but median within-DAO AUC is **0.416**; the pooled signal is driven by venue differences. | `python3 q_ai_governance/benchmark_contestedness.py` |
| [EWL equilibrium](EWL_EQUILIBRIUM.md) | Reproduces the restricted-strategy result and its failure under full SU(2); the full space retains a Haar-uniform equilibrium worth 2.25. | `python3 q_ai_governance/ewl_equilibrium.py` |
| [Gamma-map sensitivity](GAMMA_MAP_SENSITIVITY.md) | Four of five preregistered quantities are fragile to unvalidated bridge constants; the robust quantity is a structural control. | `python3 tools/gamma_map_sensitivity.py` |

The gamma study was [preregistered](PREREGISTRATION_gamma_map.md) before the
grid ran. Versioned outputs live in [`data/`](data/), and
[`tools/ledger/check_ledger.py`](tools/ledger/check_ledger.py) verifies published
results against their generators in CI.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`q_ai_governance/`](q_ai_governance/) | Governance experiments and Python package |
| [`quantum_orch_or/`](quantum_orch_or/) | Open-system simulations and somatic bridge |
| [`data/`](data/) | Versioned inputs and generated results |
| [`tools/ledger/`](tools/ledger/) | Reproducibility manifest and checker |
| [`tests/`](tests/) | Automated tests |
| [`archive/`](archive/) | Superseded publications and unvalidated concept notes |

See [REPOSITORY_MAP.md](REPOSITORY_MAP.md) for status and compatibility details.

## Install and test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m pytest -q
python tools/ledger/check_ledger.py
```

The package is also published as `q-ai-governance`, but repository results
should be reproduced from the pinned source revision and dependencies recorded
with each study.

## Scope and limitations

- Governance and market outputs are research prototypes, not decision advice.
- Smart contracts in [`contracts/`](contracts/) are experimental and unaudited.
- Somatic parameters are not physiologically validated; see the gamma study.
- Historical papers, pitches, PDFs, and submission bundles remain available in
  the archive so the correction trail is inspectable.

## License

[MIT](LICENSE)
