import pytest
import os
from quantum_economics import QuantumMarketSentimentModel, QuantumFinancialOrderEffect, QuantumLiquidityContagion, run_quantum_econ_benchmark

def test_quantum_market_sentiment_evolution():
    model = QuantumMarketSentimentModel(initial_sentiment="superposition")
    res = model.evolve_sentiment(market_shock=0.1, steps=10)
    
    assert len(res["p_bullish"]) == 10
    assert len(res["p_bearish"]) == 10
    assert 0.0 <= res["p_bullish"][0] <= 1.0

def test_quantum_financial_order_effects():
    order_engine = QuantumFinancialOrderEffect()
    res = order_engine.simulate_news_sequence(angle_A=0.5, angle_B=0.8)
    
    assert 0.0 <= res["path_AB_bullish_pct"] <= 100.0
    assert 0.0 <= res["path_BA_bullish_pct"] <= 100.0
    assert res["order_effect_delta"] >= 0.0

def test_quantum_liquidity_contagion():
    contagion = QuantumLiquidityContagion(num_institutions=2)
    res = contagion.simulate_contagion(shock_severity=0.8)
    
    assert 0.0 <= res["p_both_solvent"] <= 1.0
    assert 0.0 <= res["p_both_default"] <= 1.0
    assert 0.0 <= res["contagion_correlation"] <= 1.0

def test_quantum_econ_cli_runner(tmp_path):
    plot_path = os.path.join(tmp_path, "econ_plot.png")
    res = run_quantum_econ_benchmark(output_plot=str(plot_path))
    
    assert os.path.exists(plot_path)
    assert "sentiment" in res
    assert "order_effect" in res
    assert "contagion" in res
