import pytest
import os
from uniswap_quantum_governance import UniswapQuantumGovernor

def test_uniswap_quantum_governance_benchmark():
    governor = UniswapQuantumGovernor()
    results = governor.run_uniswap_benchmark()
    
    assert len(results) == 3
    assert results[0]["id"] == "UNI-PROP-12"
    assert results[0]["prediction_error_pct"] < 2.0

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
