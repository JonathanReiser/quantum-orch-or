"""
Tests for quantum_orch_or/circuit.py — the state-preparation and
Trotter-step circuit builders. Uses qiskit.quantum_info.Statevector for
exact (noiseless) circuit simulation rather than AerSimulator, since
these circuits contain no measurement/reset and Statevector is faster
and simpler for that case.
"""
import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from quantum_orch_or.circuit import (
    create_initial_state_circuit,
    append_trotter_step,
    build_full_evolution_circuit,
    build_mid_circuit_collapse_circuit,
)


@pytest.mark.parametrize("num_qubits", [2, 3, 4])
def test_ground_state_is_all_zero_basis_state(num_qubits):
    qc = create_initial_state_circuit(num_qubits, "ground")
    probs = Statevector(qc).probabilities()
    assert probs[0] == pytest.approx(1.0)
    assert np.sum(probs[1:]) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("num_qubits", [2, 3, 4])
def test_excited_state_is_all_one_basis_state(num_qubits):
    qc = create_initial_state_circuit(num_qubits, "excited")
    probs = Statevector(qc).probabilities()
    assert probs[-1] == pytest.approx(1.0)
    assert np.sum(probs[:-1]) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("num_qubits", [2, 3, 4])
def test_superposition_state_is_uniform(num_qubits):
    qc = create_initial_state_circuit(num_qubits, "superposition")
    probs = Statevector(qc).probabilities()
    expected = 1.0 / (2 ** num_qubits)
    assert probs == pytest.approx(np.full(2 ** num_qubits, expected))


@pytest.mark.parametrize("num_qubits", [2, 3, 4])
def test_ghz_state_is_split_between_all_zero_and_all_one(num_qubits):
    qc = create_initial_state_circuit(num_qubits, "ghz")
    probs = Statevector(qc).probabilities()
    assert probs[0] == pytest.approx(0.5)
    assert probs[-1] == pytest.approx(0.5)
    assert np.sum(probs[1:-1]) == pytest.approx(0.0, abs=1e-9)


def test_unknown_state_type_raises():
    with pytest.raises(ValueError):
        create_initial_state_circuit(3, "not-a-real-state")


def test_trotter_step_appends_expected_gate_counts():
    num_qubits = 3
    qc = create_initial_state_circuit(num_qubits, "ground")
    append_trotter_step(qc, num_qubits, J_coupling=1e-3, g_tunneling=5e-4, dt=1e-3)

    names = [instr.operation.name for instr in qc.data]
    # num_qubits - 1 nearest-neighbor ZZ interactions, num_qubits transverse-field rotations
    assert names.count("rzz") == num_qubits - 1
    assert names.count("rx") == num_qubits


def test_trotter_step_with_zero_parameters_is_identity():
    # rzz(0)/rx(0) are identity rotations, so a full evolution circuit with
    # J=g=0 should leave the initial state completely unchanged.
    num_qubits = 3
    qc = build_full_evolution_circuit(
        num_qubits, J_coupling=0.0, g_tunneling=0.0, dt=1e-3, steps=10, initial_state="superposition"
    )
    initial = Statevector(create_initial_state_circuit(num_qubits, "superposition"))
    evolved = Statevector(qc)
    assert np.allclose(np.asarray(evolved), np.asarray(initial), atol=1e-9)


def test_build_full_evolution_circuit_qubit_count_and_zero_steps():
    num_qubits = 4
    qc = build_full_evolution_circuit(num_qubits, 1e-3, 5e-4, 1e-3, steps=0, initial_state="ground")
    assert qc.num_qubits == num_qubits
    assert len(qc.data) == 0  # ground state prep is a no-op, zero Trotter steps appended


def test_build_mid_circuit_collapse_circuit_structure():
    num_qubits = 3
    qc = build_mid_circuit_collapse_circuit(
        num_qubits, J_coupling=1e-3, g_tunneling=5e-4, dt=1e-3, steps_before_collapse=5, initial_state="ground"
    )
    assert qc.num_qubits == num_qubits
    assert qc.num_clbits == num_qubits
    names = [instr.operation.name for instr in qc.data]
    assert "measure" in names
    assert "reset" in names
    assert names.count("reset") == num_qubits
