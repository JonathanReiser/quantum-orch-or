import pytest
import os
from uniswap_quantum_governance import UniswapQuantumGovernor

def test_uniswap_quantum_governance_benchmark():
    governor = UniswapQuantumGovernor()
    results = governor.run_uniswap_benchmark()

    assert len(results) == 3
    assert results[0]["id"] == "UNI-PROP-12"
    # UNI-PROP-12 is part of the training set used to fit
    # trained_uniswap_agent_weights.npz (see train_uniswap_governance_agent.py),
    # so this is an in-sample sanity check, not a generalization claim — the
    # honest held-out estimate is uniswap_agent_loo_cv_results.json's
    # leave-one-out MAE (~33pp on n=5, i.e. don't expect tight accuracy on a
    # genuinely new proposal). Bound below is empirical: 9 observed runs of
    # this exact prediction ranged 2.4-10.4pp error; 20pp leaves real margin
    # against sampling variance in the 50-rollout Monte Carlo estimate while
    # still catching an actual regression (e.g. weights failing to load).
    assert results[0]["prediction_error_pct"] < 20.0

def test_uniswap_forum_proposal_generation(tmp_path):
    proposal_path = os.path.join(tmp_path, "UNISWAP_TEST_PROPOSAL.md")
    governor = UniswapQuantumGovernor()
    governor.generate_uniswap_forum_proposal(output_md=str(proposal_path))
    
    assert os.path.exists(proposal_path)
    with open(proposal_path, "r") as f:
        content = f.read()
    assert "[Proposal] Q-AI Governance Oracle" in content
    assert "UNI-PROP-12" in content

def test_uniswap_cli_command(monkeypatch, capsys):
    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "uniswap"])
    main()
    
    captured = capsys.readouterr()
    assert "UNISWAP Q-AI GOVERNANCE ORACLE BENCHMARK" in captured.out
