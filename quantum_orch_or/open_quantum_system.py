"""
Open Quantum System Physics Engine using Lindblad Master Equation

Models thermal dephasing (gamma_phi at T = 310 K) and energy relaxation (gamma_1)
on microtubule tubulin qubit density matrices under Penrose Objective Reduction (Orch-OR).
"""

import numpy as np
from scipy.linalg import expm
from .physics import (
    calculate_single_tubulin_eg,
    HBAR
)

class LindbladMasterEquationSolver:
    """
    Solves the Lindblad Master Equation for an N-qubit tubulin system:
    d(rho)/dt = -i [H, rho] + sum_k ( L_k rho L_k^dagger - 0.5 {L_k^dagger L_k, rho} )
    """
    def __init__(self, num_qubits=2, J_coupling=1.0e-3, g_field=5.0e-4, gamma_dephasing=0.01, gamma_relaxation=0.005, eg_scale=1.0e17):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.J = J_coupling
        self.g = g_field
        self.gamma_dephasing = gamma_dephasing
        self.gamma_relaxation = gamma_relaxation
        self.eg_scale = eg_scale
        
        self.single_eg = calculate_single_tubulin_eg() * self.eg_scale
        
        # Pauli operators
        self.sigma_x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
        self.sigma_y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        self.sigma_z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
        self.sigma_minus = np.array([[0, 1], [0, 0]], dtype=np.complex128)
        self.identity = np.eye(2, dtype=np.complex128)

        self.H = self._build_hamiltonian()
        self.collapse_operators = self._build_collapse_operators()

    def _get_single_qubit_op(self, op, qubit_idx):
        op_list = [self.identity] * self.num_qubits
        op_list[qubit_idx] = op
        res = op_list[0]
        for item in op_list[1:]:
            res = np.kron(res, item)
        return res

    def _build_hamiltonian(self):
        H = np.zeros((self.dim, self.dim), dtype=np.complex128)
        # Transverse Field (-g sum X_i)
        for i in range(self.num_qubits):
            H -= self.g * self._get_single_qubit_op(self.sigma_x, i)
            
        # Nearest-neighbor Ising interaction (-J sum Z_i Z_{i+1})
        for i in range(self.num_qubits - 1):
            Z_i = self._get_single_qubit_op(self.sigma_z, i)
            Z_next = self._get_single_qubit_op(self.sigma_z, i + 1)
            H -= self.J * (Z_i @ Z_next)
            
        return H

    def _build_collapse_operators(self):
        c_ops = []
        for i in range(self.num_qubits):
            # Dephasing operator L_z
            if self.gamma_dephasing > 0:
                L_z = np.sqrt(self.gamma_dephasing) * self._get_single_qubit_op(self.sigma_z, i)
                c_ops.append(L_z)
            # Relaxation operator L_-
            if self.gamma_relaxation > 0:
                L_m = np.sqrt(self.gamma_relaxation) * self._get_single_qubit_op(self.sigma_minus, i)
                c_ops.append(L_m)
        return c_ops

    def compute_drho_dt(self, rho):
        """
        Computes d(rho)/dt according to the Lindblad equation.
        """
        # Unitary component: -i [H, rho]
        drho = -1j * (self.H @ rho - rho @ self.H)
        
        # Dissipative component
        for L in self.collapse_operators:
            L_dagger = L.conj().T
            L_dag_L = L_dagger @ L
            dissipator = L @ rho @ L_dagger - 0.5 * (L_dag_L @ rho + rho @ L_dag_L)
            drho += dissipator
            
        return drho

    def step(self, rho, dt=0.01):
        """
        Evolves density matrix rho by dt using 4th-order Runge-Kutta.
        """
        k1 = self.compute_drho_dt(rho)
        k2 = self.compute_drho_dt(rho + 0.5 * dt * k1)
        k3 = self.compute_drho_dt(rho + 0.5 * dt * k2)
        k4 = self.compute_drho_dt(rho + dt * k3)
        
        rho_next = rho + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Enforce Hermiticity and unit trace
        rho_next = 0.5 * (rho_next + rho_next.conj().T)
        rho_next /= np.real(np.trace(rho_next))
        return rho_next

    def compute_coherence_weight(self, rho):
        """
        Calculates density matrix purity Tr(rho^2) as spatial coherence metric W_c.
        """
        return np.real(np.trace(rho @ rho))

    def run_simulation(self, total_steps=100, dt=0.01):
        """
        Runs density matrix evolution with Penrose OR collapse checks.
        """
        # Initialize pure state (|00...0> + |11...1>) / sqrt(2)
        psi0 = np.zeros(self.dim, dtype=np.complex128)
        psi0[0] = 1.0 / np.sqrt(2)
        psi0[-1] = 1.0 / np.sqrt(2)
        rho = np.outer(psi0, psi0.conj())

        time_axis = []
        purity_axis = []
        action_axis = []
        collapses = []
        
        accumulated_action = 0.0

        for step_idx in range(total_steps):
            t = step_idx * dt
            time_axis.append(t)
            
            w_c = self.compute_coherence_weight(rho)
            purity_axis.append(w_c)
            
            inst_eg = self.single_eg * w_c
            accumulated_action += inst_eg * dt
            action_axis.append(accumulated_action)

            # Check Penrose OR Collapse Threshold
            if accumulated_action >= HBAR:
                collapses.append(step_idx)
                # Sample basis state from diagonal elements
                probs = np.real(np.diag(rho))
                probs /= np.sum(probs)
                collapsed_idx = np.random.choice(self.dim, p=probs)
                
                # Reset density matrix to pure basis state
                rho = np.zeros((self.dim, self.dim), dtype=np.complex128)
                rho[collapsed_idx, collapsed_idx] = 1.0
                accumulated_action = 0.0
            else:
                rho = self.step(rho, dt)

        return {
            "time": time_axis,
            "purity": purity_axis,
            "action": action_axis,
            "collapses": collapses
        }
