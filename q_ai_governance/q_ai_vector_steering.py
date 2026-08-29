r"""
Quantum Latent Vector Steering Engine (q_ai_vector_steering.py)
----------------------------------------------------------------
Implements continuous phase interference cos(\Delta\phi), density matrix
Born probability sampling P(k) = |<k|\psi>|^2, and activation steering
tensors for LLM representation engineering.
"""

import numpy as np
from typing import Dict, Any, Tuple


class ComplexStatevectorMapper:
    r"""
    Maps real-valued embedding vectors (e.g. 1024-d, 4096-d) into
    Complex Hilbert Space (\mathcal{H} = \mathbb{C}^{d/2}) with phase angles.
    """

    @staticmethod
    def project(real_embedding: np.ndarray) -> np.ndarray:
        arr = np.asarray(real_embedding, dtype=np.float64)
        if arr.ndim != 1 or len(arr) < 2:
            raise ValueError("Embedding must be 1D array with len >= 2.")
        if len(arr) % 2 != 0:
            arr = arr[:-1]

        even = arr[0::2]
        odd = arr[1::2]
        complex_vec = even + 1j * odd

        norm = np.linalg.norm(complex_vec)
        if norm == 0:
            return complex_vec
        return complex_vec / norm


class ContinuousPhaseInterferenceOperator:
    """
    Applies continuous unitary phase rotation U(\Delta\phi) = e^{i * \Delta\phi}.
    Interference term is given by cos(\Delta\phi).
    """

    @staticmethod
    def apply_phase_shift(
        statevector: np.ndarray,
        target_indices: np.ndarray,
        delta_phi: float = np.pi
    ) -> Tuple[np.ndarray, float]:
        vec = np.asarray(statevector, dtype=np.complex128).copy()
        mask = np.zeros(len(vec), dtype=np.float64)
        for idx in target_indices:
            if 0 <= idx < len(mask):
                mask[idx] = 1.0

        phase_factor = np.exp(1j * delta_phi * mask)
        filtered = vec * phase_factor

        norm = np.linalg.norm(filtered)
        if norm > 0:
            filtered = filtered / norm

        # Continuous interference factor = cos(\Delta\phi)
        interference_factor = float(np.cos(delta_phi))

        return filtered, interference_factor


class BornRuleStatevectorSampler:
    """
    Calculates density matrix \rho = |\psi><\psi| and measures Born rule probabilities:
    P(k) = |<k|\psi>|^2
    """

    @staticmethod
    def sample_probabilities(statevector: np.ndarray) -> np.ndarray:
        vec = np.asarray(statevector, dtype=np.complex128)
        probs = np.abs(vec) ** 2
        p_sum = np.sum(probs)
        if p_sum > 0:
            probs = probs / p_sum
        return probs


class LatentVectorSteeringEngine:
    """
    Synthesizes activation steering tensors v_steer for LLM representation engineering.
    """

    def __init__(self, baseline_stability: float = 50.0):
        self.baseline_stability = baseline_stability

    def compute_steering_activation(
        self,
        raw_embedding: np.ndarray,
        distortion_indices: np.ndarray,
        phase_angle: float = np.pi
    ) -> Dict[str, Any]:
        # 1. Project to Complex Hilbert Space
        psi = ComplexStatevectorMapper.project(raw_embedding)

        # 2. Continuous Phase Interference
        psi_filtered, interference_factor = ContinuousPhaseInterferenceOperator.apply_phase_shift(
            psi, distortion_indices, delta_phi=phase_angle
        )

        # 3. Born Probability Sampling
        probs = BornRuleStatevectorSampler.sample_probabilities(psi_filtered)

        # 4. Synthesize Real-Valued Activation Steering Vector (for LLM Latent Injection)
        # Reconstruct real embedding shape: [Re(psi_0), Im(psi_0), Re(psi_1), Im(psi_1)...]
        reconstructed = np.empty(len(psi_filtered) * 2, dtype=np.float64)
        reconstructed[0::2] = np.real(psi_filtered)
        reconstructed[1::2] = np.imag(psi_filtered)

        # Steering direction = (reconstructed - raw_embedding)
        raw_truncated = raw_embedding[: len(reconstructed)]
        steering_vector = reconstructed - raw_truncated

        # 5. Measure Stability Delta
        p_deescalate = float(np.mean(probs[: len(probs) // 2])) if len(probs) > 0 else 0.5
        p_escalate = float(np.mean(probs[len(probs) // 2 :])) if len(probs) > 0 else 0.5

        exp_val = p_deescalate - p_escalate
        stability_delta = int(np.round(exp_val * 15.0))
        new_stability = max(0.0, min(100.0, self.baseline_stability + stability_delta))

        return {
            "statevector_dim": len(psi_filtered),
            "interference_factor": interference_factor,
            "steering_vector_norm": float(np.linalg.norm(steering_vector)),
            "steering_vector_sample": steering_vector[:4].tolist(),
            "p_deescalate": p_deescalate,
            "p_escalate": p_escalate,
            "stability_delta": stability_delta,
            "new_stability": new_stability,
            "representation_steering_ready": True,
        }
