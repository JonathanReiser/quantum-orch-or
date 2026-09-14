"""
tests/test_market_signal_api.py — Unit tests for Commercial Quantitative Trading API.
"""

from pathlib import Path

import pytest
from q_ai_governance.market_signal_api import MarketSignalAPI

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolate_generated_report(monkeypatch, tmp_path):
    """MarketSignalAPI writes a scan report as part of every request."""
    monkeypatch.chdir(tmp_path)
    yield
    assert (tmp_path / "market_signals_report.json").exists()
    assert not (REPO_ROOT / "market_signals_report.json").exists()

def test_market_signal_api_response():
    api = MarketSignalAPI()
    res = api.get_signal("BTC")
    assert res["status"] == "200 OK"
    assert res["asset"] == "BTC"
    assert "p_bullish_percent" in res["quantum_statevector"]
    assert "take_profit_target" in res["ai_trade_targets"]
    assert len(res["api_signature"]) == 64

def test_market_signal_api_unsupported_asset():
    api = MarketSignalAPI()
    res = api.get_signal("INVALID_ASSET")
    assert "error" in res
