import hashlib
import os
from pathlib import Path

import numpy as np
import pytest

from uniswap_quantum_governance import UniswapQuantumGovernor

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACKED_PROPOSAL = REPO_ROOT / "UNISWAP_GOVERNANCE_PROPOSAL.md"

def test_uniswap_quantum_governance_benchmark():
    governor = UniswapQuantumGovernor()
    results = governor.run_uniswap_benchmark(rng=np.random.default_rng(20260913))

    assert len(results) == 3
    assert results[0]["id"] == "UNI-PROP-12"
    assert all(0.0 <= result["q_ai_predicted_yes_pct"] <= 100.0 for result in results)
    assert all(result["prediction_error_pct"] >= 0.0 for result in results)

def test_uniswap_forum_proposal_generation(tmp_path):
    proposal_path = os.path.join(tmp_path, "UNISWAP_TEST_PROPOSAL.md")
    governor = UniswapQuantumGovernor()
    governor.generate_uniswap_forum_proposal(output_md=str(proposal_path))
    
    assert os.path.exists(proposal_path)
    with open(proposal_path, "r") as f:
        content = f.read()
    assert "[Proposal] Q-AI Governance Oracle" in content
    assert "UNI-PROP-12" in content

def test_uniswap_cli_command(monkeypatch, capsys, tmp_path):
    """The CLI must write only where it is told. Previously this test ran with
    the default --output, so it overwrote the tracked UNISWAP_GOVERNANCE_PROPOSAL.md
    on every run with numbers from one unseeded stochastic draw (issue #12)."""
    output_path = tmp_path / "UNISWAP_GOVERNANCE_PROPOSAL.md"
    tracked = REPO_ROOT / "UNISWAP_GOVERNANCE_PROPOSAL.md"
    before = tracked.read_bytes()

    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "uniswap", "--output", str(output_path)])
    main()

    captured = capsys.readouterr()
    assert "UNISWAP Q-AI GOVERNANCE ORACLE BENCHMARK" in captured.out
    assert output_path.exists(), "the requested output path was not written"
    assert tracked.read_bytes() == before, (
        "running the CLI modified the tracked proposal; --output was ignored")


# --- regression tests for issue #12 -----------------------------------------


def test_seeded_runs_are_reproducible():
    """Same explicit seed, same forecasts. Guards against the seed being ignored
    or the RNG being re-created per call."""
    first = UniswapQuantumGovernor().run_uniswap_benchmark(rng=np.random.default_rng(20260913))
    second = UniswapQuantumGovernor().run_uniswap_benchmark(rng=np.random.default_rng(20260913))
    assert [r["q_ai_predicted_yes_pct"] for r in first] == \
           [r["q_ai_predicted_yes_pct"] for r in second]


def test_different_seeds_give_different_forecasts():
    """The complement of the test above: if these matched, 'reproducible' would
    be meaningless because the generator would be constant."""
    a = UniswapQuantumGovernor().run_uniswap_benchmark(rng=np.random.default_rng(1))
    b = UniswapQuantumGovernor().run_uniswap_benchmark(rng=np.random.default_rng(999))
    assert [r["q_ai_predicted_yes_pct"] for r in a] != \
           [r["q_ai_predicted_yes_pct"] for r in b]


def test_benchmark_does_not_disturb_the_global_numpy_rng():
    """A seeded run must not advance or reseed process-global numpy state, or it
    would silently change the draws every other test sees."""
    np.random.seed(4242)
    expected = np.random.random(5).tolist()

    np.random.seed(4242)
    UniswapQuantumGovernor().run_uniswap_benchmark(rng=np.random.default_rng(7))
    after = np.random.random(5).tolist()

    assert after == expected, "the benchmark consumed or reseeded the global RNG"


def test_proposal_generation_writes_only_where_asked(tmp_path):
    before = TRACKED_PROPOSAL.read_bytes()
    target = tmp_path / "proposal.md"
    UniswapQuantumGovernor().generate_uniswap_forum_proposal(
        output_md=str(target), rng=np.random.default_rng(3))
    assert target.exists()
    assert TRACKED_PROPOSAL.read_bytes() == before


def test_tracked_proposal_publishes_no_single_run_accuracy_claim():
    """Issue #12: the committed 3.4pp mean absolute error came from one unseeded
    stochastic run and is not reproducible. It must not return -- in that form or
    any other per-run accuracy figure."""
    text = TRACKED_PROPOSAL.read_text(encoding="utf-8")
    assert "Mean Absolute Error on this sample" not in text
    assert "% Error" not in text, "per-run error column reintroduced into the table"
    assert "Prediction Error" not in text
    # Both unsupported figures must remain explicitly retracted.
    assert "No per-run accuracy figure is published here" in text
    assert "No valid held-out accuracy estimate" in text
    assert "32.74pp leave-one-out result" in text
    assert "That is the figure to cite" not in text


def test_tracked_proposal_matches_its_generator(tmp_path):
    """The committed document must be exactly what the generator produces, so it
    cannot drift from the code that claims to produce it."""
    target = tmp_path / "regenerated.md"
    UniswapQuantumGovernor().generate_uniswap_forum_proposal(output_md=str(target))
    fresh = hashlib.sha256(target.read_bytes()).hexdigest()
    committed = hashlib.sha256(TRACKED_PROPOSAL.read_bytes()).hexdigest()
    assert fresh == committed, (
        "the committed proposal is not what the generator emits; regenerate it "
        "and update the ledger entry")
