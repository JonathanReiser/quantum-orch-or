"""
tests/test_market_signal_api.py — Unit tests for Commercial Quantitative Trading API.
"""

import pytest
from q_ai_governance.market_signal_api import MarketSignalAPI

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
