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
