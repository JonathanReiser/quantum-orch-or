import pytest
import os
from quantum_crypto_engine import QuantumCryptoPredictor

def test_quantum_crypto_predictor_execution():
    predictor = QuantumCryptoPredictor(asset="BTC")
    res = predictor.predict_market_direction()
    
    assert res["asset"] == "BTC"
    assert res["current_price"] > 0
    assert res["q_ai_target_price"] > 0
    assert 0.0 <= res["prob_bullish_pct"] <= 100.0
    assert res["risk_level"] in ["LOW", "MEDIUM", "HIGH"]

def test_quantum_crypto_plot_generation(tmp_path):
    plot_path = os.path.join(tmp_path, "crypto_test.png")
    predictor = QuantumCryptoPredictor(asset="ETH")
    res = predictor.predict_market_direction()
    
    predictor.generate_crypto_chart(res, output_plot=str(plot_path))
    assert os.path.exists(plot_path)

def test_crypto_cli_command(monkeypatch, capsys):
    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "crypto", "--asset", "SOL"])
    main()
    
    captured = capsys.readouterr()
    assert "Q-AI Crypto Market Forecast for SOL" in captured.out
