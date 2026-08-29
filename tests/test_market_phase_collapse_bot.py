"""
tests/test_market_phase_collapse_bot.py — Unit tests for Market Phase Collapse Bot.
"""

import os
import pytest
from market_phase_collapse_bot import MarketPhaseCollapseBot

def test_scan_asset_phase():
    bot = MarketPhaseCollapseBot()
    res = bot.scan_asset_phase("BTC")
    assert res["asset"] == "BTC"
    assert "p_bull" in res
    assert "gamma_phi" in res
    assert res["risk"] in ["LOW", "MEDIUM", "HIGH"]

def test_run_market_scan(tmp_path):
    json_path = str(tmp_path / "test_market_report.json")
    bot = MarketPhaseCollapseBot(assets=["BTC", "ETH"])
    report = bot.run_market_scan(output_json=json_path)
    assert os.path.exists(json_path)
    assert report["total_assets_scanned"] == 2

def test_generate_social_broadcast_cards():
    bot = MarketPhaseCollapseBot(assets=["BTC"])
    cards = bot.generate_social_broadcast_cards()
    assert len(cards) == 1
    assert "Q-AI Market Phase Signal [BTC]" in cards[0]
