# Results ledger

`manifest.json` lists every reproducible artifact behind this repository's
published claims. `check_ledger.py` verifies two things for each entry:

1. **Reproducibility.** For entries marked `reproducible`, the listed command
   is re-run and its output is byte-compared to the committed file. A
   mismatch fails the build.
2. **Documentation.** Every `doc_claims` string is checked for literal
   presence in the named file. A published number that has drifted from the
   artifact it cites fails the build too.

Two entries are marked `reproducible: false` on purpose, with a stated reason
in `note`: `snapshot-dataset` (a live network fetch, not expected to be
byte-identical run to run) and `qai-agent-benchmark` (a fit that
[CORRECTIONS.md](../../CORRECTIONS.md) section 7 shows is noise-dominated at
its rollout budget — re-running it would either flag false mismatches or train
a habit of loosening the tolerance until the check goes quiet, which is what
this ledger exists to prevent). Both are still pinned by hash, so a silent
hand-edit is still caught; only genuine non-reproducibility is exempted, and
only when the repo already says so.

## Why this exists

[CORRECTIONS.md](../../CORRECTIONS.md) retracts seven claims that were never
regenerable from anything — a clamped R^2, an untrained model, a fixture
incapable of failing, a validation methodology that didn't exist. Every one of
them would have been caught by the rule this ledger enforces: **a published
number is only valid if a command reproduces it, or if the repo says plainly
that it can't.**

## Running it

```bash
python3 tools/ledger/check_ledger.py                       # everything
python3 tools/ledger/check_ledger.py --entry ewl-equilibrium  # one entry
```

Runs in CI on every push and PR to `main` (see `.github/workflows/tests.yml`,
job `results-ledger`).

## Adding or updating an entry

When a script's output changes intentionally, or a new claim is published:

```bash
python3 tools/ledger/rebuild_manifest.py
git diff tools/ledger/manifest.json   # confirm only the expected hash moved
```

Never hand-edit a `sha256` field to make a failing check pass. If the check is
failing, either the change was unintentional and should be reverted, or it was
intentional and the manifest should be regenerated — never patched directly.

## Cross-platform reproducibility of float artifacts

A raw float64 dump is not byte-reproducible. The same code, the same committed
dataset and the same seed produce different low-order bits on different BLAS
backends, because the reduction order differs. That is not a bug in the
benchmark and it is not a stale committed file — it is a property of floating
point, and a sha256 comparison will fail on it every time.

Measured on 2026-09-13 by regenerating both benchmarks on three platforms
(local arm64 macOS, `macos-latest`, `ubuntu-latest`) and diffing field by field
across all 640 floats:

| artifact | fields differing | worst relative | worst absolute |
|---|---|---|---|
| `benchmark_classical_results.json` | 130 / 574 | `9.494e-14` | `3.411e-13` |
| `benchmark_contestedness_results.json` | 3 / 66 | `1.261e-16` | `5.551e-17` |

The `9.494e-14` outlier is `results.ridge_prevote_features.r2`. That R² is
~0.0129 — a small difference between two much larger sums — so cancellation
amplifies its relative error even though the absolute error is 1.2e-15.

**The fix is canonicalisation, not tolerance.** `q_ai_governance/canonical_json.py`
rounds every float to `SIGNIFICANT_DIGITS = 6` before serialisation, so the
artifact stops recording digits the computation cannot reproduce. The ledger's
byte comparison stays exact; nothing is widened, and no platform's output is
blessed over another's.

Six significant digits sits between two hard constraints:

* **Above the noise.** The relative rounding step is at least `1e-6`, about
  `1e7` times the measured `9.494e-14` noise floor. A value only changes its
  rounded form if it falls within the noise of a rounding boundary — roughly
  `1e-7` per value, `~6e-5` across all 640. Rounding is a very strong guarantee,
  not a proof; the `results-ledger` matrix over `ubuntu-latest` and
  `macos-latest` is what verifies it on every run.
* **Below every published claim.** The most precise number any document asserts
  is four significant digits (`10.44` pp MAE); the rest are three (`0.660`,
  `-0.125`, `0.416`) or two (`0.0010`). Six keeps two digits more than the
  finest published claim, so every documented value formats identically before
  and after. `tests/test_canonical_json.py` pins all eleven of them.

Do not raise `SIGNIFICANT_DIGITS` without redoing that arithmetic. At nine
digits the per-run collision risk is a few percent, which would make the ledger
flaky rather than reproducible.
