import pytest
from crypto_recommendations import QuantumCryptoRecommendationOracle

def test_crypto_recommendation_oracle():
    oracle = QuantumCryptoRecommendationOracle()
    summary = oracle.generate_recommendations()
    
    assert summary["assets_evaluated"] == 5
    assert len(summary["recommendations"]) == 5
    
    rec0 = summary["recommendations"][0]
    assert rec0["asset"] in ["BTC", "ETH", "SOL", "ARB", "OP"]
    assert rec0["signal"] in ["BULLISH_BUY", "BEARISH_SELL", "NEUTRAL_HOLD"]
    assert rec0["stop_loss_price"] > 0

def test_recommend_cli_command(monkeypatch, capsys):
    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "recommend"])
    main()
    
    captured = capsys.readouterr()
    assert "QUANTUM-COGNITIVE CRYPTO RECOMMENDATION ORACLE" in captured.out
