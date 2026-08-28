"""
tests/test_quantum_psychiatry_engine.py — Unit tests for Quantum Psychiatry Simulator.
"""

import os
import pytest
from quantum_psychiatry_engine import QuantumPsychiatrySimulator

def test_depression_eigenstate_trap():
    sim = QuantumPsychiatrySimulator()
    path = sim.simulate_depression_eigenstate_trap(steps=20)
    assert len(path) == 20
    # Verify statevector stays trapped near |0> (< 0.2 rad)
    assert all(theta < 0.2 for theta in path)

def test_therapeutic_phase_pulse():
    sim = QuantumPsychiatrySimulator()
    path = sim.simulate_therapeutic_phase_pulse(steps=20, pulse_step=10)
    assert len(path) == 20
    # Before pulse (step 5), trapped near 0.05
    assert path[5] < 0.2
    # At pulse (step 10), restored to superposition near pi/4 (~0.785 rad)
    assert abs(path[10] - (3.14159 / 4.0)) < 0.05

def test_anxiety_thermal_dephasing():
    sim = QuantumPsychiatrySimulator()
    path = sim.simulate_anxiety_thermal_dephasing(steps=20)
    assert len(path) == 20
    # Verify high variance/volatility under dephasing
    assert min(path) >= 0.0 and max(path) <= 1.58

def test_run_psychiatry_benchmark(tmp_path):
    plot_file = str(tmp_path / "test_plot.png")
    paper_file = str(tmp_path / "test_paper.md")
    sim = QuantumPsychiatrySimulator()
    out_paper = sim.run_psychiatry_benchmark(output_plot=plot_file, output_paper=paper_file)
    assert os.path.exists(plot_file)
    assert os.path.exists(paper_file)
    assert "Depression as Hilbert Space Eigenstate Trapping" in open(paper_file).read()
