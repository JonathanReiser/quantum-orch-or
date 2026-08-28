import pytest
import numpy as np
from quantum_orch_or.open_quantum_system import LindbladMasterEquationSolver

def test_lindblad_solver_initialization():
    solver = LindbladMasterEquationSolver(num_qubits=2, gamma_dephasing=0.01, gamma_relaxation=0.005)
    assert solver.dim == 4
    assert solver.H.shape == (4, 4)
    assert len(solver.collapse_operators) == 4

def test_lindblad_density_matrix_step():
    solver = LindbladMasterEquationSolver(num_qubits=2, gamma_dephasing=0.05)
    psi0 = np.array([1.0, 0.0, 0.0, 1.0]) / np.sqrt(2)
    rho = np.outer(psi0, psi0.conj())
    
    # Verify unit trace initially
    assert np.isclose(np.real(np.trace(rho)), 1.0)
    
    # Step forward in time
    rho_next = solver.step(rho, dt=0.01)
    
    # Trace preservation check
    assert np.isclose(np.real(np.trace(rho_next)), 1.0)
    
    # Hermiticity check
    assert np.allclose(rho_next, rho_next.conj().T)
    
    # Dephasing should decrease off-diagonal elements (purity)
    purity_initial = solver.compute_coherence_weight(rho)
    purity_next = solver.compute_coherence_weight(rho_next)
    assert purity_next <= purity_initial + 1e-6

def test_lindblad_simulation_loop():
    solver = LindbladMasterEquationSolver(num_qubits=2, eg_scale=1.0e17)
    results = solver.run_simulation(total_steps=20, dt=0.01)
    
    assert len(results["time"]) == 20
    assert len(results["purity"]) == 20
    assert len(results["action"]) == 20
    assert isinstance(results["collapses"], list)
