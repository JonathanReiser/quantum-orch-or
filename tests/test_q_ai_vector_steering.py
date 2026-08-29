"""
Unit tests for Quantum Latent Vector Steering Engine (q_ai_vector_steering.py)
"""

import pytest
import numpy as np
from q_ai_governance.q_ai_vector_steering import (
    ComplexStatevectorMapper,
    ContinuousPhaseInterferenceOperator,
    BornRuleStatevectorSampler,
    LatentVectorSteeringEngine,
)


def test_complex_statevector_mapper():
    embed = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    psi = ComplexStatevectorMapper.project(embed)

    assert len(psi) == 3
    assert np.isclose(np.linalg.norm(psi), 1.0)


def test_continuous_phase_interference():
    psi = np.array([1.0 + 0j, 1.0 + 0j]) / np.sqrt(2)
    indices = np.array([0])

    filtered, factor = ContinuousPhaseInterferenceOperator.apply_phase_shift(psi, indices, delta_phi=np.pi)

    assert np.isclose(factor, -1.0)
    assert np.isclose(np.linalg.norm(filtered), 1.0)
    assert np.isclose(filtered[0], -1.0 / np.sqrt(2))


def test_born_rule_sampler():
    psi = np.array([1.0 + 0j, 0.0 + 0j])
    probs = BornRuleStatevectorSampler.sample_probabilities(psi)

    assert len(probs) == 2
    assert probs[0] == 1.0
    assert probs[1] == 0.0


def test_latent_vector_steering_engine():
    engine = LatentVectorSteeringEngine(baseline_stability=38.0)
    raw_embed = np.random.randn(64)
    distortion_indices = np.array([0, 2, 4])

    res = engine.compute_steering_activation(raw_embed, distortion_indices, phase_angle=np.pi)

    assert res["statevector_dim"] == 32
    assert res["interference_factor"] == -1.0
    assert res["representation_steering_ready"] is True
    assert res["steering_vector_norm"] > 0
