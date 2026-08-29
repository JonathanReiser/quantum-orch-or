"""
tests/test_quantum_economics_engine.py — Unit tests for Quantum Economics Simulator.
"""

import os
import pytest
from quantum_economics_engine import QuantumEconomicsSimulator

def test_ellsberg_ambiguity():
    sim = QuantumEconomicsSimulator()
    p_class, p_quant = sim.simulate_ellsberg_ambiguity(ambiguity_level=0.7)
    assert abs(p_class - 0.5) < 0.01
    assert p_quant < p_class # Quantum cognitive interference models ambiguity aversion

def test_market_liquidity_collapse():
    sim = QuantumEconomicsSimulator()
    path = sim.simulate_market_liquidity_collapse(steps=20, shock_step=10)
    assert len(path) == 20
    # Before shock (step 5), confidence > 0.3
    assert path[5] > 0.3

def test_run_economics_benchmark(tmp_path):
    plot_file = str(tmp_path / "test_econ_plot.png")
    paper_file = str(tmp_path / "test_econ_paper.md")
    sim = QuantumEconomicsSimulator()
    out_paper = sim.run_economics_benchmark(output_plot=plot_file, output_paper=paper_file)
    assert os.path.exists(plot_file)
    assert os.path.exists(paper_file)
    assert "Quantum Macroeconomics & Finance" in open(paper_file).read()
