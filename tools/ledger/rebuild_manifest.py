#!/usr/bin/env python3
"""
rebuild_manifest.py — (re)generate tools/ledger/manifest.json.

This is the ONLY way manifest.json's sha256 fields should change. Editing them
by hand to make a failing check_ledger.py pass defeats the entire point of the
ledger; this script exists so there is never a reason to.

Run it after intentionally changing a benchmark's output, or when adding a new
entry (edit ENTRIES below first). Then diff the result:

    python3 tools/ledger/rebuild_manifest.py
    git diff tools/ledger/manifest.json

Only the hash(es) you meant to change should move.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "manifest.json"

SCHEMA_NOTE = (
    "Every number quoted in this repository's published claims must trace to a "
    "command that regenerates it. check_ledger.py enforces two things: (1) each "
    "reproducible entry's command, run fresh, byte-matches the committed output "
    "file, and (2) the doc_claims listed for every entry actually appear verbatim "
    "in the named documentation files. A claim with no entry here, or an entry "
    "whose command no longer reproduces its output, is exactly the failure mode "
    "documented in CORRECTIONS.md -- a number nobody re-ran."
)

# Source of truth. Add an entry here, then run this script; never edit
# manifest.json directly.
ENTRIES = [
    {
        "id": "snapshot-classical-benchmark",
        "description": "Classical baselines (constant/ridge) on the real Snapshot dataset — CORRECTIONS.md's headline table.",
        "reproducible": True,
        "command": ["python3", "q_ai_governance/benchmark_snapshot_real.py",
                    "--data", "data/snapshot_dao_dataset.json", "--out", "{tmp}"],
        "committed_output": "data/benchmark_classical_results.json",
        "doc_claims": [
            {"file": "README.md", "must_contain": ["historical median (**10.44 pp MAE**)"]},
            {"file": "CORRECTIONS.md", "must_contain": [
                "| **constant (train median)** | **10.44** | 26.73 | −0.125 |",
                "| ridge on pre-vote features | 11.20 | 25.04 | 0.013 |"]},
        ],
    },
    {
        "id": "ewl-equilibrium",
        "description": "EWL restricted/full-SU(2) equilibrium search and the derived entanglement threshold.",
        "reproducible": True,
        "command": ["python3", "q_ai_governance/ewl_equilibrium.py", "--out", "{tmp}"],
        "committed_output": "data/ewl_equilibrium_results.json",
        "doc_claims": [
            {"file": "EWL_EQUILIBRIUM.md", "must_contain": ["γ_c = arccos(√(3/5)) ≈ 0.684719 rad ≈ 39.23°"]},
        ],
    },
    {
        "id": "ewl-mixed-equilibrium",
        "description": "Closed-form Haar-uniform equilibrium value on the full SU(2) game.",
        "reproducible": True,
        "command": ["python3", "q_ai_governance/ewl_mixed_equilibrium.py", "--out", "{tmp}"],
        "committed_output": "data/ewl_mixed_equilibrium_results.json",
        "doc_claims": [
            {"file": "EWL_EQUILIBRIUM.md", "must_contain": [
                "Its value is (T+R+P+S)/4 = **2.25**.",
                "recovers 62.5% of the distance"]},
            {"file": "README.md", "must_contain": ["Haar-uniform equilibrium worth 2.25"]},
        ],
    },
    {
        "id": "contestedness-benchmark",
        "description": "Contestedness classification, including the within-DAO Simpson's-paradox control.",
        "reproducible": True,
        "command": ["python3", "q_ai_governance/benchmark_contestedness.py",
                    "--data", "data/snapshot_dao_dataset.json", "--out", "{tmp}"],
        "committed_output": "data/benchmark_contestedness_results.json",
        "doc_claims": [
            {"file": "README.md", "must_contain": [
                "AUC 0.660, 95% CI [0.555, 0.763]", "median within-DAO AUC is **0.416**"]},
            {"file": "CONTESTEDNESS.md", "must_contain": [
                "| **all features** | **0.660** | [0.555, 0.763] | 0.0010 |",
                "**Median within-DAO AUC: 0.416.**"]},
        ],
    },
    {
        "id": "snapshot-dataset",
        "description": "The real Snapshot DAO dataset itself.",
        "reproducible": False,
        "note": ("Fetched live from the Snapshot GraphQL hub by "
                 "q_ai_governance/fetch_snapshot_dataset.py, which requires network "
                 "access and returns whatever the hub currently holds — it is not "
                 "expected to be byte-identical across runs (new proposals close over "
                 "time). This entry pins the hash of the committed snapshot only, so a "
                 "silent hand-edit of the file is still detectable."),
        "committed_output": "data/snapshot_dao_dataset.json",
        "doc_claims": [
            {"file": "README.md", "must_contain": [
                "905 closed, cleanly-binary proposals", "6,242,940 vote records"]},
            {"file": "CORRECTIONS.md", "must_contain": [
                "| Kept (settled tally, unambiguous binary ballot) | **905** |",
                "| Vote records across kept proposals | **6,242,940** |"]},
        ],
    },
    {
        "id": "qai-agent-benchmark",
        "description": "QuantumOrchORAgent vs. classical baselines on the real Snapshot split.",
        "reproducible": False,
        "note": ("Deliberately NOT regenerated in CI. The fit accepted 0/40 moves "
                 "(CORRECTIONS.md section 7) because the loss estimator's own noise "
                 "exceeds any resolvable improvement at this rollout budget, so two "
                 "runs differ by the spread between two random seeds, not by anything "
                 "meaningful. Re-running it in CI would either flag a false mismatch "
                 "every time or, worse, train a habit of raising the tolerance until "
                 "the check goes quiet -- which is the failure this ledger exists to "
                 "prevent. Pinning only the hash of what is committed proves the file "
                 "was not edited by hand; it makes no claim that the run is "
                 "reproducible, and CORRECTIONS.md says so explicitly."),
        "committed_output": "data/benchmark_qai_results.json",
        "doc_claims": [
            {"file": "CORRECTIONS.md", "must_contain": [
                "| Q-AI agent, random initialisation | 42.98 | 47.59 | −2.564 |",
                "| Q-AI agent, after 40 fitting iterations | 28.07 | 32.62 | −0.675 |"]},
        ],
    },
    {
        "id": "narrow-contestedness-primary",
        "description": ("Pre-registered narrow-band contestedness benchmark "
                        "(contested := final YES share in [40%, 60%]) — the negative "
                        "result headlined in NARROW_CONTESTEDNESS.md."),
        "reproducible": False,
        "note": ("Deliberately NOT regenerated in CI: the engine pass is 214 test "
                 "rows x 50 rollouts x 10 weight seeds and takes roughly two hours, "
                 "far beyond the 180s budget here. This is a cost limit, not a "
                 "determinism one -- the run is seeded and does reproduce. Pinning "
                 "the hash proves the committed file was not hand-edited; it makes "
                 "no claim that CI re-derived it. The cheap half IS regenerated: "
                 "narrow-contestedness-sensitivity below reruns from the committed "
                 "raw scores in ~11s and re-derives this file's AUCs to a max drift "
                 "of 0.00e+00, so a tampered results file is still caught."),
        "committed_output": "data/benchmark_narrow_contestedness_results.json",
        "doc_claims": [
            {"file": "NARROW_CONTESTEDNESS.md", "must_contain": [
                "| quantum — point estimate (a) | 0.482 | [0.407, 0.528] | 0.868 | 0.044 |",
                "| quantum — rollout dispersion (b) | 0.419 | [0.337, 0.504] | 0.967 | 0.038 |",
                "| quantum — coherence at collapse (c) | 0.382 | [0.318, 0.458] | 1.000 | 0.037 |",
                "| logistic regression | 0.622 | [0.337, 0.880] | 0.179 | 0.194 |",
                "**9 of 214** (4.21%)",
                "| point estimate | 0.482 | 0.195 | 0.755 | 4 / 10 |",
                "| coherence at collapse | 0.382 | 0.165 | 0.775 | 4 / 10 |"]},
            {"file": "README.md", "must_contain": [
                "point\n  estimate AUC 0.482, rollout dispersion 0.419, coherence at collapse 0.382"]},
        ],
    },
    {
        "id": "narrow-contestedness-raw-scores",
        "description": ("Raw per-seed test-set scores from the narrow-band engine "
                        "pass — the input that lets any label-only re-analysis skip "
                        "the two-hour rerun."),
        "reproducible": False,
        "note": ("Same two-hour engine pass as narrow-contestedness-primary, so it "
                 "is pinned rather than regenerated. Tampering with it is caught "
                 "anyway: narrow-contestedness-sensitivity consumes this file and "
                 "IS regenerated in CI, so any edit changes that entry's output and "
                 "fails the check."),
        "committed_output": "data/narrow_contestedness_raw_scores.npz",
        "doc_claims": [],
    },
    {
        "id": "narrow-contestedness-sensitivity",
        "description": ("Disclosed (not pre-registered) sensitivity analysis: does "
                        "the narrow-band conclusion survive the abstain-excluding "
                        "YES-share denominator? Holds the model fixed, swaps labels."),
        "reproducible": True,
        "committed_output": "data/sensitivity_yes_share_definition.json",
        "command": ["python3", "q_ai_governance/sensitivity_yes_share_definition.py",
                    "--out", "{tmp}"],
        "doc_claims": [
            {"file": "NARROW_CONTESTEDNESS.md", "must_contain": [
                "| quantum — coherence | 0.382 [0.318, 0.458] | 0.377 [0.262, 0.410]  |",
                "| logistic | 0.622 [0.337, 0.880] | 0.559 [0.141, 0.810] |",
                "matches the committed primary exactly (max drift `0.00e+00`)",
                "**694 of\n905** proposals by up to **55 percentage points**"]},
        ],
    },
]


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    entries = []
    for spec in ENTRIES:
        committed = ROOT / spec["committed_output"]
        if not committed.exists():
            raise SystemExit(f"missing committed output for {spec['id']}: {committed}")
        entry = {
            "id": spec["id"],
            "description": spec["description"],
            "reproducible": spec["reproducible"],
            "committed_output": spec["committed_output"],
            "sha256": sha256_file(committed),
            "doc_claims": spec.get("doc_claims", []),
        }
        if spec["reproducible"]:
            entry["command"] = spec["command"]
        else:
            entry["note"] = spec["note"]
        entries.append(entry)

    manifest = {"$schema_note": SCHEMA_NOTE, "entries": entries}
    OUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {OUT} with {len(entries)} entries")


if __name__ == "__main__":
    main()
