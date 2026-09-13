"""One-qubit open-system analogy driven by a somatic gamma parameter."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector
from qiskit_dynamics.models import LindbladModel
from qiskit_dynamics.solvers import solve_lmde


@dataclass(frozen=True)
class Trajectory:
    time_s: np.ndarray
    p_choice_1: np.ndarray
    coherence_l1: np.ndarray
    purity: np.ndarray
    density_matrices: np.ndarray


def initial_choice_circuit(theta: float = np.pi / 2, phase: float = 0.0) -> QuantumCircuit:
    circuit = QuantumCircuit(1, name="localized_choice_node")
    circuit.ry(theta, 0)
    circuit.rz(phase, 0)
    return circuit


def mindfulness_rotation(rho: np.ndarray, angle: float) -> np.ndarray:
    """Apply RY; this redirects state but cannot recover dissipated purity."""
    c, s = np.cos(angle / 2), np.sin(angle / 2)
    rotation = np.array([[c, -s], [s, c]], dtype=complex)
    return rotation @ rho @ rotation.conj().T


def simulate(
    gamma_per_s: float,
    duration_s: float = 10.0,
    samples: int = 301,
    thermal_excited_fraction: float = 0.10,
    mindfulness_at_s: float | None = 4.0,
    mindfulness_angle: float = -np.pi / 5,
) -> Trajectory:
    """Solve thermal relaxation with an optional instantaneous intervention."""
    if not (0.0 <= gamma_per_s <= 10.0):
        raise ValueError("gamma_per_s must be in [0, 10]")
    if not (0.0 <= thermal_excited_fraction <= 1.0):
        raise ValueError("thermal_excited_fraction must be in [0, 1]")
    if duration_s <= 0 or samples < 2:
        raise ValueError("duration_s must be positive and samples >= 2")

    sigma_minus = np.array([[0, 1], [0, 0]], dtype=complex)
    sigma_plus = sigma_minus.conj().T
    down = gamma_per_s * (1.0 - thermal_excited_fraction)
    up = gamma_per_s * thermal_excited_fraction
    model = LindbladModel(
        static_hamiltonian=np.zeros((2, 2)),
        static_dissipators=[np.sqrt(down) * sigma_minus, np.sqrt(up) * sigma_plus],
    )
    rho0 = np.asarray(DensityMatrix(Statevector(initial_choice_circuit())).data)
    times = np.linspace(0.0, duration_s, samples)

    def solve_segment(t_eval: np.ndarray, state: np.ndarray) -> np.ndarray:
        if len(t_eval) == 1:
            return state[None, :, :]
        result = solve_lmde(
            model, [float(t_eval[0]), float(t_eval[-1])], state,
            t_eval=t_eval, atol=1e-10, rtol=1e-9,
        )
        return np.asarray(result.y)

    if mindfulness_at_s is None or not (0.0 < mindfulness_at_s < duration_s):
        states = solve_segment(times, rho0)
    else:
        split = int(np.searchsorted(times, mindfulness_at_s))
        left = solve_segment(np.append(times[:split], mindfulness_at_s), rho0)
        rotated = mindfulness_rotation(left[-1], mindfulness_angle)
        right_samples = times[split:]
        exact = bool(np.isclose(right_samples[0], mindfulness_at_s))
        right_t = right_samples if exact else np.insert(right_samples, 0, mindfulness_at_s)
        right = solve_segment(right_t, rotated)
        states = np.concatenate((left[:-1], right if exact else right[1:]), axis=0)

    return Trajectory(
        times,
        np.real(states[:, 1, 1]),
        2.0 * np.abs(states[:, 0, 1]),
        np.real(np.einsum("tij,tji->t", states, states)),
        states,
    )

