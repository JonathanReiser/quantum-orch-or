"""
Live Demonstration: Quantum Truth Alignment Engine (demo_truth_alignment.py)
-----------------------------------------------------------------------------
Demonstrates Epistemic Invariance, Dialectical Truth Superposition, and Representation
Coherence Filtering for LLM Activation Steering.
"""

import numpy as np
from q_ai_governance.q_ai_truth_alignment import TruthAlignedSteeringPipeline

def main():
    print("=" * 80)
    print("🎯 QUANTUM TRUTH ALIGNMENT ENGINE — LIVE DEMO")
    print("=" * 80)

    pipeline = TruthAlignedSteeringPipeline(baseline_stability=38.0)
    np.random.seed(42)

    user_prompt = np.random.randn(128)
    objective_fact = np.random.randn(128)
    hallucination_noise_indices = np.array([1, 4, 7, 10, 15])

    print("\n1. INPUT PROCESSED:")
    print("   User Prompt Vector Dim:", len(user_prompt))
    print("   Objective Fact Grounding Vector Dim:", len(objective_fact))
    print("   Hallucination Noise Vector Indices:", hallucination_noise_indices)

    res = pipeline.compute_truth_steering(user_prompt, objective_fact, hallucination_noise_indices)

    print("\n2. QUANTUM TRUTH METRICS CALCULATED:")
    print(f"   Epistemic Fact Invariance Index (I_fact): {res['epistemic_invariance'] * 100:.1f}%")
    print(f"   Representation Coherence Score:            {res['representation_coherence'] * 100:.1f}%")
    print(f"   Steering Activation Vector Norm:          {res['steering_vector_norm']:.4f}")
    print(f"   Stability Delta (\\Delta S):                +{res['stability_delta']}")
    print(f"   New Grounded Stability Score:              {res['new_stability']:.1f} / 100")
    print(f"   Truth Status:                             {res['truth_aligned_status']}")

    print("\n" + "=" * 80)
    print("✓ SUCCESS: Epistemic & Dialectical Truth Alignment Steering Vector Synthesized!")
    print("=" * 80)

if __name__ == "__main__":
    main()
