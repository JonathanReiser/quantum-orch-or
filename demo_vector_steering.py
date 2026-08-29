"""
Live Demonstration: Latent Vector Steering Engine (demo_vector_steering.py)
-----------------------------------------------------------------------------
Demonstrates continuous phase interference cos(\Delta\phi) across arbitrary phase angles,
Born probability density matrix sampling, and real-valued activation steering vector synthesis.
"""

import numpy as np
from q_ai_governance.q_ai_vector_steering import LatentVectorSteeringEngine

def main():
    print("=" * 80)
    print("⚡ QUANTUM LATENT VECTOR STEERING ENGINE — LIVE DEMO")
    print("=" * 80)

    engine = LatentVectorSteeringEngine(baseline_stability=38.0)
    np.random.seed(42)
    raw_embedding = np.random.randn(128)
    distortion_indices = np.array([0, 2, 4, 8, 12, 16])

    print("\n1. USER THOUGHT INPUT PROCESSED:")
    print("   Input Dimension:", len(raw_embedding), "(e.g., LLM Latent Activation Layer)")
    print("   Detected Cognitive Distortion Indices:", distortion_indices)

    print("\n2. CONTINUOUS PHASE INTERFERENCE SWEEP (\\cos(\\Delta\\phi)):")
    phase_angles = [
        (0.0, "0° (Zero Shift / Constructive Boost)"),
        (np.pi / 4, "45° (Partial Phase Modulation)"),
        (np.pi / 2, "90° (Orthogonal Quadrature Shift)"),
        (np.pi, "180° (Full Destructive Phase Cancellation)"),
    ]

    for angle, label in phase_angles:
        res = engine.compute_steering_activation(raw_embedding, distortion_indices, phase_angle=angle)
        print(f"\n   --- Angle: {label} ---")
        print(f"     Continuous Interference Term cos(\\Delta\\phi): {res['interference_factor']:+.4f}")
        print(f"     Steering Vector Norm (||v_steer||):           {res['steering_vector_norm']:.4f}")
        print(f"     Resulting Stability Delta (\\Delta S):         {res['stability_delta']:+d}")
        print(f"     New Emotional Stability Score:               {res['new_stability']:.1f}")

    print("\n" + "=" * 80)
    print("✓ SUCCESS: Quantum Steering Tensors Ready for LLM Latent Injection!")
    print("=" * 80)

if __name__ == "__main__":
    main()
