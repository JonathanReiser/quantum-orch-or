r"""
Unit tests for Quantum Truth Alignment Engine (q_ai_truth_alignment.py)
"""

import pytest
import numpy as np
from q_ai_governance.q_ai_truth_alignment import (
    EpistemicTruthAnchor,
    DialecticalTruthIntegrator,
    RepresentationCoherenceEngine,
    TruthAlignedSteeringPipeline,
)


def test_epistemic_truth_anchor():
    fact = np.array([1.0, 0.0, 0.0, 1.0])
    usr = np.array([1.0, 0.0, 0.0, 1.0])

    invariance = EpistemicTruthAnchor.calculate_invariance(fact, usr)
    assert np.isclose(invariance, 1.0)


def test_dialectical_truth_integrator():
    psi = DialecticalTruthIntegrator.build_truth_superposition(emotion_dim=64)
    assert len(psi) == 64
    assert np.isclose(np.linalg.norm(psi), 1.0)
    assert np.isclose(np.abs(psi[0]) ** 2, 0.5)
    assert np.isclose(np.abs(psi[1]) ** 2, 0.5)


def test_representation_coherence_engine():
    psi = DialecticalTruthIntegrator.build_truth_superposition(emotion_dim=4)
    mask = np.array([1.0, 0.0, 0.0, 0.0])

    filtered, coherence = RepresentationCoherenceEngine.cancel_hallucination_noise(psi, mask)

    assert len(filtered) == 4
    assert np.isclose(np.linalg.norm(filtered), 1.0)
    assert coherence == 0.75


def test_truth_aligned_steering_pipeline():
    pipeline = TruthAlignedSteeringPipeline(baseline_stability=38.0)
    usr_embed = np.random.randn(128)
    fact_embed = np.random.randn(128)
    noise_indices = np.array([0, 2, 4])

    res = pipeline.compute_truth_steering(usr_embed, fact_embed, noise_indices)

    assert 0.0 <= res["epistemic_invariance"] <= 1.0
    assert 0.0 <= res["representation_coherence"] <= 1.0
    assert res["steering_vector_norm"] > 0
    assert res["new_stability"] > 38.0
    assert res["truth_aligned_status"] == "EPISTEMICALLY_GROUNDED_AND_DIALECTICALLY_BALANCED"
