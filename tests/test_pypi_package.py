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
    assert "EXPLORATORY STATEVECTOR SIMULATION" in captured.out
    assert "not a validated vote forecast" in captured.out


def test_pypi_cli_benchmark_uses_real_dataset(monkeypatch, tmp_path, capsys):
    output = tmp_path / "benchmark.json"
    monkeypatch.setattr("sys.argv", [
        "q-ai-gov",
        "benchmark",
        "--data", "data/snapshot_dao_dataset.json",
        "--output", str(output),
    ])
    main()
    report = __import__("json").loads(output.read_text())
    captured = capsys.readouterr()

    assert "temporal split, no hindsight" in captured.out
    assert report["split"]["n_total"] == 905
    assert "ridge_prevote_features" in report["results"]


def test_pypi_cli_lists_experiments(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "experiments", "--list"])
    main()
    captured = capsys.readouterr()

    assert "snapshot-temporal-baseline" in captured.out
    assert "external companion" in captured.out
