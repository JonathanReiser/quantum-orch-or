"""
Sanity checks for quantum_orch_or/physics.py — the classical/GR-adjacent
math (E_G, coherence weight, collapse time) that the rest of the
simulation is built on. These are pure functions with known closed-form
or hand-derivable answers, so we pin exact expected values rather than
just "it runs".
"""
import numpy as np
import pytest

from quantum_orch_or.physics import (
    calculate_single_tubulin_eg,
    calculate_collapse_time,
    calculate_coherence_metric,
    scale_gravitational_energy,
    G_CONSTANT,
    HBAR,
    TUBULIN_MASS,
    DISPLACEMENT_DISTANCE,
    TUBULIN_RADIUS,
)


def test_single_tubulin_eg_penrose_matches_formula():
    expected = G_CONSTANT * (TUBULIN_MASS ** 2) * (DISPLACEMENT_DISTANCE ** 2) / (TUBULIN_RADIUS ** 3)
    assert calculate_single_tubulin_eg() == pytest.approx(expected)
    assert calculate_single_tubulin_eg(method="penrose") > 0


def test_single_tubulin_eg_simple_matches_formula():
    expected = G_CONSTANT * (TUBULIN_MASS ** 2) / DISPLACEMENT_DISTANCE
    assert calculate_single_tubulin_eg(method="simple") == pytest.approx(expected)


def test_single_tubulin_eg_unknown_method_raises():
    with pytest.raises(ValueError):
        calculate_single_tubulin_eg(method="not-a-real-method")


def test_collapse_time_is_hbar_over_eg():
    eg = 2.0e-30
    assert calculate_collapse_time(eg) == pytest.approx(HBAR / eg)


def test_collapse_time_nonpositive_eg_is_infinite():
    assert calculate_collapse_time(0.0) == float("inf")
    assert calculate_collapse_time(-1.0) == float("inf")


def test_coherence_definite_basis_state_is_zero():
    # |000...0>: every qubit is in a definite classical bit (zero variance),
    # so C_ii = <Z_i^2> - <Z_i>^2 = 1 - 1 = 0, and the qubits are trivially
    # uncorrelated (C_ij = 0 for i != j too) — no coherence at all, matching
    # the "classical basis state" limit this metric is meant to detect.
    for n in (2, 3, 4):
        state = np.zeros(2 ** n, dtype=complex)
        state[0] = 1.0
        weight, c_matrix = calculate_coherence_metric(state, n)
        assert weight == pytest.approx(0.0, abs=1e-9)
        assert np.allclose(c_matrix, 0.0, atol=1e-9)


def test_coherence_uniform_product_superposition_equals_n():
    # H^{⊗n}|0...0>: each qubit individually in |+> (local superposition,
    # so C_ii = 1 - 0^2 = 1), but qubits are independent of each other
    # (C_ij = 0 for i != j) — this is the "product state (classical/
    # uncorrelated)" case the module's own docstring says sums to N.
    for n in (2, 3, 4):
        state = np.full(2 ** n, 1 / np.sqrt(2 ** n), dtype=complex)
        weight, c_matrix = calculate_coherence_metric(state, n)
        assert weight == pytest.approx(n)
        assert np.allclose(c_matrix, np.eye(n), atol=1e-9)


def test_coherence_ghz_state_equals_n_squared():
    # (|00...0> + |11...1>) / sqrt(2): a maximally-coherent GHZ state.
    # Per the module's own docstring, this should give coherence_weight == N^2.
    for n in (2, 3, 4):
        state = np.zeros(2 ** n, dtype=complex)
        state[0] = 1 / np.sqrt(2)
        state[-1] = 1 / np.sqrt(2)
        weight, c_matrix = calculate_coherence_metric(state, n)
        assert weight == pytest.approx(n * n)
        assert np.allclose(c_matrix, 1.0, atol=1e-9)


def test_coherence_weight_ghz_exceeds_product_superposition():
    # The core Orch-OR claim this metric encodes: genuine entanglement
    # (GHZ, weight N^2) should register as MORE coherent than the same
    # qubits merely each in their own local superposition with no
    # inter-qubit correlation (product state, weight N).
    n = 4
    product = np.full(2 ** n, 1 / np.sqrt(2 ** n), dtype=complex)
    ghz = np.zeros(2 ** n, dtype=complex)
    ghz[0] = ghz[-1] = 1 / np.sqrt(2)

    product_weight, _ = calculate_coherence_metric(product, n)
    ghz_weight, _ = calculate_coherence_metric(ghz, n)
    assert ghz_weight > product_weight


def test_scale_gravitational_energy_is_linear():
    assert scale_gravitational_energy(2.0, 3.0) == pytest.approx(6.0)
    assert scale_gravitational_energy(5.0, 0.0) == 0.0
