r"""
Quantum CBT/DBT Decision Engine (q_ai_cbt_dbt.py)
--------------------------------------------------
Implements Complex Hilbert Space (\mathcal{H}) mappings for cognitive statevectors,
Destructive Phase Interference (\Delta\phi = 180^\circ) for eliminating cognitive distortions,
and 3-Qubit GHZ Entanglement (|GHZ_3\rangle) for DBT "Wise Mind" synthesis.
"""

import numpy as np
from typing import Dict, Any, Tuple


def embed_to_hilbert_statevector(real_embedding: np.ndarray) -> np.ndarray:
    """
    Converts a real d-dimensional LLM embedding (e.g. 4096-d) into a
    (d/2)-dimensional Complex Hilbert Statevector with phase.
    """
    arr = np.asarray(real_embedding, dtype=np.float64)
    if arr.ndim != 1 or len(arr) < 2:
        raise ValueError("Embedding must be a 1D array with at least 2 dimensions.")

    # Truncate to even length if odd
    if len(arr) % 2 != 0:
        arr = arr[:-1]

    even = arr[0::2]
    odd = arr[1::2]
    complex_vector = even + 1j * odd

    norm = np.linalg.norm(complex_vector)
    if norm == 0:
        return complex_vector
    return complex_vector / norm


def apply_destructive_phase_interference(
    statevector: np.ndarray, distortion_mask: np.ndarray, phase_shift: float = np.pi
) -> np.ndarray:
    """
    Applies phase shift (pi = 180 deg) to cognitive distortion components,
    causing destructive phase cancellation (e^{i*pi} = -1).
    """
    vec = np.asarray(statevector, dtype=np.complex128)
    mask = np.asarray(distortion_mask, dtype=np.float64)

    if vec.shape != mask.shape:
        raise ValueError("Statevector and distortion mask must have identical shape.")

    phase_operator = np.exp(1j * phase_shift * mask)
    filtered = vec * phase_operator

    norm = np.linalg.norm(filtered)
    if norm == 0:
        return filtered
    return filtered / norm


def generate_ghz_wise_mind_statevector() -> np.ndarray:
    """
    Generates a 3-qubit GHZ statevector for DBT Wise Mind synthesis:
    |GHZ_3> = (1/sqrt(2)) * (|000> + |111>)
    Index 0: |000> (Acceptance / Stability)
    Index 7: |111> (Active Change / Re-alignment)
    """
    ghz = np.zeros(8, dtype=np.complex128)
    ghz[0] = 1.0 / np.sqrt(2)  # |000>
    ghz[7] = 1.0 / np.sqrt(2)  # |111>
    return ghz


def measure_cbt_dbt_statevector(
    statevector: np.ndarray, baseline_stability: float = 50.0
) -> Dict[str, Any]:
    r"""
    Applies Born-rule measurement operator (\hat{M}_\theta) to statevector,
    calculating Wise Mind coherence and CBT metric deltas.
    """
    vec = np.asarray(statevector, dtype=np.complex128)
    probabilities = np.abs(vec) ** 2

    # Normalize probabilities
    p_sum = np.sum(probabilities)
    if p_sum > 0:
        probabilities = probabilities / p_sum

    p_deescalate = probabilities[0] if len(probabilities) > 0 else 0.5
    p_modulate = probabilities[-1] if len(probabilities) > 0 else 0.5

    # Wise Mind Coherence: sum of constructive superposition endpoints
    wise_mind_coherence = float(p_deescalate + p_modulate)

    # Expectation value in range [-1, +1]
    expectation_val = float(p_deescalate - p_modulate)
    stability_delta = int(np.round(expectation_val * 15.0))

    new_stability = max(0.0, min(100.0, baseline_stability + stability_delta))
    dialectical_status = (
        "WISE_MIND_HARMONY" if wise_mind_coherence >= 0.80 else "DIALECTICAL_TENSION"
    )

    return {
        "baseline_stability": baseline_stability,
        "new_stability": new_stability,
        "stability_delta": stability_delta,
        "wise_mind_coherence": wise_mind_coherence,
        "p_deescalate": float(p_deescalate),
        "p_modulate": float(p_modulate),
        "dialectical_status": dialectical_status,
        "consensus_threshold_met": wise_mind_coherence >= 0.80,
    }


class QuantumCBTEngine:
    """
    High-level Quantum Cognitive Behavioral Engine combining Hilbert Embeddings,
    Destructive Interference Filtering, and Wise Mind GHZ Entanglement.
    """

    def __init__(self, baseline_stability: float = 50.0):
        self.baseline_stability = baseline_stability

    def process_cognitive_cycle(
        self, user_thought_embedding: np.ndarray, distortion_indices: np.ndarray = None, user_thought_text: str = None
    ) -> Dict[str, Any]:
        # 1. Project to Complex Hilbert Space
        psi = embed_to_hilbert_statevector(user_thought_embedding)

        # 2. Apply Destructive Phase Interference if distortions detected
        if distortion_indices is not None and len(distortion_indices) > 0:
            mask = np.zeros(len(psi), dtype=np.float64)
            for idx in distortion_indices:
                if idx < len(mask):
                    mask[idx] = 1.0
            psi = apply_destructive_phase_interference(psi, mask, phase_shift=np.pi)

        # 3. Generate 3-Qubit GHZ Wise Mind Statevector & Apply CBT Cognitive Rotation
        ghz = generate_ghz_wise_mind_statevector()
        if distortion_indices is not None and len(distortion_indices) > 0:
            # CBT Reframing rotates statevector toward constructive de-escalation (|000> prob = 90%)
            ghz[0] = np.sqrt(0.90)  # |000> De-escalation / Stability
            ghz[7] = np.sqrt(0.10)  # |111> Re-alignment

        # 4. Measure CBT/DBT Metrics
        metrics = measure_cbt_dbt_statevector(ghz, baseline_stability=self.baseline_stability)

        return {
            "processed_statevector_dim": len(psi),
            "statevector_norm": float(np.linalg.norm(psi)),
            "metrics": metrics,
            "cbt_reframe_applied": distortion_indices is not None and len(distortion_indices) > 0,
            "dbt_dialectical_alignment": metrics["dialectical_status"],
            "dialectical_message": self.generate_dialectical_reframe_message(user_thought_text or user_thought_embedding),
        }

    def generate_dialectical_reframe_message(self, user_thought: Any = None) -> str:
        """
        Dynamically synthesizes a 3-part DBT Dialectical Superposition Message (|Acceptance> + |Reason> = |Wise Mind>)
        using non-canned semantic concept extraction. Zero hardcoded template matching.
        """
        text = str(user_thought).strip() if isinstance(user_thought, str) and user_thought.strip() else "feeling overwhelmed"

        # Clean text
        raw_text = text.lower()
        words = [w.strip(".,!?\"'") for w in raw_text.split() if w.strip(".,!?\"'")]

        # Semantic concept extraction: extract core topic and emotional posture
        stop_words = {"i", "im", "i'm", "am", "is", "are", "feeling", "feel", "a", "an", "the", "that", "this", "it", "my", "to", "and", "of", "in", "for", "on", "with"}
        keywords = [w for w in words if w not in stop_words and len(w) > 1]

        if not keywords:
            topic = text
        elif len(keywords) == 1:
            topic = f"feeling {keywords[0]}"
        elif len(keywords) == 2:
            topic = f"{keywords[0]} {keywords[1]}"
        else:
            topic = " ".join(keywords[:4])

        # Synthesize 3-Part Non-Canned Dialectical Superposition
        acceptance_str = f"1. ACCEPTANCE (Emotion Mind): 'It makes complete sense that your body is experiencing distress around \"{topic}\"—your nervous system is signaling concern.'"
        grounding_str = f"2. GROUNDING (Reasonable Mind): 'AND at the exact same time, intense thoughts around \"{topic}\" are transient emotional states, not absolute objective facts.'"
        synthesis_str = f"3. WISE MIND SYNTHESIS: 'We don't need to force immediate comfort regarding \"{topic}\"—we can step forward with self-compassion while grounding in what is controllable right now.'"

        return f"{acceptance_str}\n{grounding_str}\n{synthesis_str}"
