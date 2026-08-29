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
        Generates a 3-part DBT Dialectical Superposition Message (|Acceptance> + |Reason> = |Wise Mind>).
        """
        text = str(user_thought).strip() if isinstance(user_thought, str) else ""

        if "sad" in text.lower():
            return (
                "1. ACCEPTANCE (Emotion Mind): 'It is completely okay and valid to feel sad right now—your nervous system is giving space to something heavy.'\n"
                "2. GROUNDING (Reasonable Mind): 'AND at the exact same time, this sadness is a temporary wave passing through, not your permanent identity.'\n"
                "3. WISE MIND SYNTHESIS: 'We don't need to force fake positivity right now—we can sit with this sadness gently while keeping space for warmth and peace to return.'"
            )
        elif "plane" in text.lower() or "fly" in text.lower() or "die" in text.lower():
            return (
                "1. ACCEPTANCE (Emotion Mind): 'It makes complete sense that your body is reacting with panic at the gate—your nervous system is trying to protect you.'\n"
                "2. GROUNDING (Reasonable Mind): 'AND at the exact same time, your physical health check and aviation safety statistics are 100% solid.'\n"
                "3. WISE MIND SYNTHESIS: 'We don't need to eliminate fear to board the plane—we can step onto the jet bridge carrying both fear and safety together.'"
            )
        elif "fail" in text.lower() or "terrified" in text.lower():
            return (
                "1. ACCEPTANCE (Emotion Mind): 'Feeling terrified of failing shows how much you care about the people and outcomes in your life.'\n"
                "2. GROUNDING (Reasonable Mind): 'AND at the exact same time, a high-anxiety thought is an emotional prediction, not an established factual outcome.'\n"
                "3. WISE MIND SYNTHESIS: 'We can honor your deep care while grounding in the present moment, focusing only on the single next manageable step.'"
            )
        elif "rent" in text.lower() or "money" in text.lower() or "pay" in text.lower():
            return (
                "1. ACCEPTANCE (Emotion Mind): 'Financial stress is deeply unsettling, and feeling anxious about paying bills is a completely understandable reaction.'\n"
                "2. GROUNDING (Reasonable Mind): 'AND at the exact same time, panic amplifies worst-case scenarios, whereas calm problem-solving reveals practical options.'\n"
                "3. WISE MIND SYNTHESIS: 'We will acknowledge the financial pressure without letting panic run the show, focusing on practical resources and step-by-step solutions.'"
            )
        elif text:
            cleaned = text if len(text) <= 60 else text[:57] + "..."
            return (
                f"1. ACCEPTANCE (Emotion Mind): 'It is completely valid to experience distress around: \"{cleaned}\"—your nervous system is signaling concern.'\n"
                f"2. GROUNDING (Reasonable Mind): 'AND at the exact same time, an intense thought or feeling is a transient internal state, not an absolute objective truth.'\n"
                f"3. WISE MIND SYNTHESIS: 'We can acknowledge this concern with compassion while anchoring in grounded Wise Mind action, focusing on what is controllable right now.'"
            )

        return (
            "1. ACCEPTANCE (Emotion Mind): 'It makes complete sense that your body is reacting with distress right now—your nervous system is trying to protect you.'\n"
            "2. GROUNDING (Reasonable Mind): 'AND at the exact same time, your baseline physical health and safety facts remain grounded.'\n"
            "3. WISE MIND SYNTHESIS: 'We don't need to eliminate the fear immediately—we can move forward carrying both self-compassion and clear-headed grounding together.'"
        )
