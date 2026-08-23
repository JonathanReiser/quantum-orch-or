"""
Tests for quantum_orch_or/simulation.py — the full statevector simulation
loop, including the Penrose objective-reduction (collapse) mechanism.

The evolution between collapses is fully deterministic (unitary Trotter
steps); the only randomness is which basis state a collapse resolves to
(np.random.choice), never *whether/when* one triggers given the inputs.
So we can assert on collapse timing/count exactly, and only need to be
loose about which basis state gets picked.
"""
import numpy as np
import pytest

from quantum_orch_or.simulation import QuantumOrchORSimulation
from quantum_orch_or.physics import HBAR


def test_result_dict_shape():
    steps = 12
    sim = QuantumOrchORSimulation(num_qubits=3, total_steps=steps, eg_scaling=1.0)
    results = sim.run_statevector_simulation()

    assert set(results.keys()) == {"time", "coherence", "energy", "action", "collapses", "probabilities"}
    for key in ("time", "coherence", "energy", "action", "probabilities"):
        assert len(results[key]) == steps
    assert all(len(p) == 3 for p in results["probabilities"])
    assert all(0.0 <= p <= 1.0 for step_probs in results["probabilities"] for p in step_probs)


def test_zero_eg_scaling_never_collapses():
    # single_eg == 0 -> step_action is always 0 -> accumulated action can
    # never reach HBAR -> no collapse should ever be triggered.
    sim = QuantumOrchORSimulation(num_qubits=3, total_steps=30, eg_scaling=0.0)
    results = sim.run_statevector_simulation()
    assert results["collapses"] == []
    assert all(a == 0.0 for a in results["action"])


def test_large_eg_scaling_forces_a_collapse_and_resets_action():
    # A huge eg_scaling should blow past the HBAR threshold almost
    # immediately, guaranteeing at least one collapse well within a modest
    # step budget. (eg_scaling=1e20 with these defaults comfortably clears
    # HBAR on the very first step: single_eg * initial coherence(=num_qubits
    # for a product "superposition" start) * dt ≈ 10x HBAR — verified
    # empirically, not just by order-of-magnitude estimate.)
    sim = QuantumOrchORSimulation(num_qubits=3, total_steps=20, eg_scaling=1e20)
    results = sim.run_statevector_simulation()

    assert len(results["collapses"]) >= 1
    first_collapse_step = results["collapses"][0]

    # The action value recorded AT the collapse step is what crossed HBAR...
    assert results["action"][first_collapse_step] >= HBAR
    # ...and accumulation restarts from zero on the very next step, so it
    # should read far below HBAR again (unless another collapse happens
    # immediately, in which case it would itself appear in `collapses`).
    if first_collapse_step + 1 < len(results["action"]) and (first_collapse_step + 1) not in results["collapses"]:
        assert results["action"][first_collapse_step + 1] < HBAR


def test_collapse_resets_state_to_a_classical_basis_state():
    # After a forced collapse, each qubit's P(|1>) for that step's snapshot
    # is whatever it was going into the collapse (probabilities are
    # recorded before the collapse check runs) — but the step immediately
    # AFTER a collapse should read a clean classical (0 or 1) probability
    # for every qubit, since the statevector was reset to a single basis
    # state.
    sim = QuantumOrchORSimulation(num_qubits=3, total_steps=20, eg_scaling=1e20)
    results = sim.run_statevector_simulation()
    assert len(results["collapses"]) >= 1

    step_after = results["collapses"][0] + 1
    if step_after < len(results["probabilities"]):
        probs_after = results["probabilities"][step_after]
        for p in probs_after:
            assert p == pytest.approx(0.0, abs=1e-9) or p == pytest.approx(1.0, abs=1e-9)


def test_generate_qiskit_hardware_circuit_structure():
    sim = QuantumOrchORSimulation(num_qubits=3, total_steps=15, eg_scaling=1e20)
    qc = sim.generate_qiskit_hardware_circuit()

    assert qc.num_qubits == 3
    # One classical register per collapse event, plus a final one.
    assert len(qc.cregs) == len(sim.collapse_events) + 1
    assert len(sim.collapse_events) >= 1  # sanity: this eg_scaling should have forced at least one

    names = [instr.operation.name for instr in qc.data]
    assert "measure" in names
    assert "reset" in names
