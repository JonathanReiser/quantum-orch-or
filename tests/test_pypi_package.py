import pytest
import q_ai_governance
from q_ai_governance.cli import main

def test_pypi_package_imports():
    assert hasattr(q_ai_governance, "QuantumOrchORAgent")
    assert hasattr(q_ai_governance, "DAOBudgetAllocator")
    assert hasattr(q_ai_governance, "RealDAOBenchmarkRunner")
    assert hasattr(q_ai_governance, "LindbladMasterEquationSolver")

def test_pypi_cli_help(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "--help"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "q-ai-gov" in captured.out or "q-ai-gov" in captured.err

def test_pypi_cli_predict(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "predict", "--public-good", "9.0", "--roi", "8.5"])
    main()
    captured = capsys.readouterr()
    assert "Q-AI PREDICTIVE GOVERNANCE ORACLE RESULT" in captured.out
