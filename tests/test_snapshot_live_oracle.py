import pytest
import os
import json
from snapshot_live_oracle import SnapshotLiveOracle

def test_snapshot_fallback_proposals():
    oracle = SnapshotLiveOracle()
    props = oracle._fallback_proposals()
    
    assert len(props) >= 2
    assert "uniswap" in props[0]["space"]["id"].lower()
    assert props[0]["votes"] > 0

def test_snapshot_live_predictions():
    oracle = SnapshotLiveOracle()
    summary = oracle.predict_live_proposals()
    
    assert summary["total_proposals"] > 0
    assert len(summary["proposals"]) > 0
    assert summary["proposals"][0]["predicted_yes_pct"] >= 0.0
    assert summary["proposals"][0]["consensus_risk"] in ["LOW", "MEDIUM", "HIGH"]

def test_cli_live_command(monkeypatch, capsys, tmp_path):
    out_json = os.path.join(tmp_path, "live.json")
    from q_ai_governance.cli import main
    
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "live", "--output", str(out_json)])
    main()
    
    assert os.path.exists(out_json)
    with open(out_json, "r") as f:
        data = json.load(f)
        assert data["total_proposals"] > 0
