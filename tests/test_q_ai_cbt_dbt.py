"""
Unit tests for Quantum CBT/DBT Decision Engine (q_ai_cbt_dbt.py)
"""

import pytest
import numpy as np
from q_ai_governance.q_ai_cbt_dbt import (
    embed_to_hilbert_statevector,
    apply_destructive_phase_interference,
    generate_ghz_wise_mind_statevector,
    measure_cbt_dbt_statevector,
    QuantumCBTEngine,
)


def test_embed_to_hilbert_statevector():
    real_embed = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    psi = embed_to_hilbert_statevector(real_embed)

    assert len(psi) == 3
    assert np.isclose(np.linalg.norm(psi), 1.0)


def test_apply_destructive_phase_interference():
    psi = np.array([1.0 + 0j, 1.0 + 0j]) / np.sqrt(2)
    mask = np.array([1.0, 0.0])  # Shift first component by pi (180 deg)

    filtered = apply_destructive_phase_interference(psi, mask, phase_shift=np.pi)

    assert len(filtered) == 2
    assert np.isclose(np.linalg.norm(filtered), 1.0)
    # Check that phase shifted component is negated (e^{i*pi} = -1)
    assert np.isclose(filtered[0], -1.0 / np.sqrt(2))


def test_generate_ghz_wise_mind_statevector():
    ghz = generate_ghz_wise_mind_statevector()

    assert len(ghz) == 8
    assert np.isclose(np.linalg.norm(ghz), 1.0)
    assert np.isclose(np.abs(ghz[0]) ** 2, 0.5)
    assert np.isclose(np.abs(ghz[7]) ** 2, 0.5)


def test_measure_cbt_dbt_statevector():
    ghz = generate_ghz_wise_mind_statevector()
    metrics = measure_cbt_dbt_statevector(ghz, baseline_stability=50.0)

    assert metrics["wise_mind_coherence"] == 1.0
    assert metrics["dialectical_status"] == "WISE_MIND_HARMONY"
    assert metrics["consensus_threshold_met"] is True


def test_quantum_cbt_engine_pipeline():
    engine = QuantumCBTEngine(baseline_stability=55.0)
    embedding = np.random.randn(128)
    distortion_indices = np.array([0, 2, 4])

    result = engine.process_cognitive_cycle(embedding, distortion_indices=distortion_indices)

    assert result["processed_statevector_dim"] == 64
    assert np.isclose(result["statevector_norm"], 1.0)
    assert result["cbt_reframe_applied"] is True
    assert result["metrics"]["baseline_stability"] == 55.0
