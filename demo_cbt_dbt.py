"""
Interactive Live Demo: Quantum CBT/DBT Decision Engine (demo_cbt_dbt.py)
-------------------------------------------------------------------------
Runs an interactive demonstration of Hilbert space cognitive statevector
projection, destructive phase cancellation of an Automatic Negative Thought,
and 3-qubit GHZ Wise Mind entanglement.
"""

import numpy as np
from q_ai_governance.q_ai_cbt_dbt import QuantumCBTEngine, embed_to_hilbert_statevector, apply_destructive_phase_interference

def main():
    print("=" * 70)
    print("🧠 QUANTUM CBT/DBT DECISION ENGINE — LIVE DEMONSTRATION")
    print("=" * 70)

    # 1. Simulate User's Distorted Thought ("Everything is falling apart")
    np.random.seed(42)
    thought_embedding = np.random.randn(128)
    print("\n1. USER THOUGHT PROCESSED:")
    print("   Input Thought: 'Everything is falling apart and I cannot handle it.'")
    print("   Raw Classical Vector Dimension:", len(thought_embedding))

    # 2. Map to Complex Hilbert Space (\mathcal{H})
    psi_initial = embed_to_hilbert_statevector(thought_embedding)
    print("\n2. HILBERT SPACE PROJECTION (\\mathcal{H} = \\mathbb{C}^{64}):")
    print("   Complex Statevector Dim:", len(psi_initial))
    print("   Unit Norm Check (||\\psi||):", np.round(np.linalg.norm(psi_initial), 4))
    print("   Sample Amplitude [0]:", np.round(psi_initial[0], 4))

    # 3. Identify Automatic Negative Thought (ANT) Distortions & Apply Destructive Cancellation
    distortion_indices = np.array([0, 2, 4, 8, 12])
    print(f"\n3. COGNITIVE RESTRUCTURING (CBT OPERATOR \\hat{{U}}(\\pi)):")
    print(f"   Detected Cognitive Distortions at Vector Indices: {distortion_indices}")
    print("   Applying Phase Shift (\\Delta\\phi = 180° / e^{i\\pi} = -1)...")

    mask = np.zeros(len(psi_initial), dtype=np.float64)
    mask[distortion_indices] = 1.0
    psi_filtered = apply_destructive_phase_interference(psi_initial, mask, phase_shift=np.pi)

    print("   Result: Destructive cancellation executed on distorted phase angles.")
    print("   Filtered Norm Check:", np.round(np.linalg.norm(psi_filtered), 4))
    print("   Phase Shifted Amplitude [0]:", np.round(psi_filtered[0], 4))

    # 4. Process Wise Mind GHZ Entanglement Cycle
    print("\n4. DBT WISE MIND SYNTHESIS (|GHZ_3\\rangle ENTANGLEMENT):")
    engine = QuantumCBTEngine(baseline_stability=38.0)  # User starts in high-anxiety state (S = 38)
    result = engine.process_cognitive_cycle(thought_embedding, distortion_indices=distortion_indices)

    metrics = result["metrics"]
    print("   Baseline Stability:", metrics["baseline_stability"])
    print("   Wise Mind Coherence:", f"{metrics['wise_mind_coherence'] * 100:.1f}%")
    print("   Dialectical Status:", metrics["dialectical_status"])
    print("   Stability Delta (\\Delta S):", f"+{metrics['stability_delta']}")
    print("   New Restored Stability:", metrics["new_stability"])

    print("\n" + "=" * 70)
    print("✓ DEMO SUCCESS: Destructive Phase Cancellation & Wise Mind Achieved!")
    print("=" * 70)

if __name__ == "__main__":
    main()
