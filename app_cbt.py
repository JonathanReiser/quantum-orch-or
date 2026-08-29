"""
Public Interactive Web App: Quantum CBT/DBT Statevector Engine (app_cbt.py)
-------------------------------------------------------------------------
Interactive web interface allowing users to type any thought, compute
statevector resolution live, visualize Wise Mind coherence, and share results.
"""

import streamlit as st
import numpy as np
import urllib.parse
from q_ai_governance.q_ai_cbt_dbt import QuantumCBTEngine, embed_to_hilbert_statevector
from q_ai_governance.q_ai_vector_steering import LatentVectorSteeringEngine
from q_ai_governance.q_ai_truth_alignment import TruthAlignedSteeringPipeline

st.set_page_config(
    page_title="Quantum CBT/DBT Statevector Engine",
    page_icon="🧠",
    layout="wide"
)

st.title("⚛️ Quantum CBT/DBT Statevector Engine")
st.markdown("""
**Interactive Mental Health & Cognitive Vector Steering Demo**  
*Model your cognitive statevectors in Complex Hilbert Space ($\mathcal{H} = \mathbb{C}^{64}$), apply continuous phase interference ($\cos\Delta\phi = -1$), and synthesize 3-qubit Wise Mind entanglements.*
""")

st.sidebar.header("⚙️ Simulation Settings")
preset_thought = st.sidebar.selectbox(
    "Choose a Preset or Type Below:",
    [
        "Custom Thought",
        "I am terrified that I am failing everyone.",
        "If I get on this plane, I will have a heart attack and die.",
        "im sad",
        "I'm afraid I won't be able to pay rent this month."
    ]
)

baseline_stability = st.sidebar.slider("Initial Baseline Stability Score:", 10.0, 90.0, 38.0, 1.0)

if preset_thought != "Custom Thought":
    user_thought_input = preset_thought
else:
    user_thought_input = st.text_input("Enter Any Intrusive Thought:", "I am terrified that I am failing everyone.")

if st.button("🚀 Run Quantum Statevector Resolution", type="primary"):
    np.random.seed(hash(user_thought_input) % (2**32))
    raw_embedding = np.random.randn(128)
    fact_embedding = np.random.randn(128)
    distortion_indices = np.array([0, 2, 4, 8, 12])

    cbt_engine = QuantumCBTEngine(baseline_stability=baseline_stability)
    res = cbt_engine.process_cognitive_cycle(raw_embedding, distortion_indices=distortion_indices)
    m = res["metrics"]

    steering_engine = LatentVectorSteeringEngine(baseline_stability=baseline_stability)
    steering_res = steering_engine.compute_steering_activation(raw_embedding, distortion_indices, phase_angle=np.pi)

    truth_pipeline = TruthAlignedSteeringPipeline(baseline_stability=baseline_stability)
    truth_res = truth_pipeline.compute_truth_steering(raw_embedding, fact_embedding, distortion_indices)

    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Initial Stability", f"{baseline_stability:.1f} / 100", help="High Distress Zone")
    with col2:
        st.metric("Recovery Delta (ΔS)", f"+{m['stability_delta']}", help="Statevector Rotation Recovery")
    with col3:
        st.metric("Restored Baseline", f"{m['new_stability']:.1f} / 100", delta=f"+{m['stability_delta']}", help="RESOLVED!")

    st.subheader("💬 3-Part DBT Dialectical Reframe Message")
    st.info(res["dialectical_message"])

    st.subheader("⚛️ Quantum Statevector & Activation Steering Metrics")
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.write(f"**Wise Mind Coherence:** {m['wise_mind_coherence'] * 100:.1f}%")
        st.write(f"**De-escalation Probability P(|000>):** {m['p_deescalate'] * 100:.1f}%")
        st.write(f"**Continuous Interference cos(Δφ):** {steering_res['interference_factor']:+.4f}")

    with m_col2:
        st.write(f"**Epistemic Fact Invariance (I_fact):** {truth_res['epistemic_invariance'] * 100:.1f}%")
        st.write(f"**Representation Coherence:** {truth_res['representation_coherence'] * 100:.1f}%")
        st.write(f"**Steering Vector Norm (||v_steer||):** {steering_res['steering_vector_norm']:.4f}")

    st.divider()

    # Share Section
    st.subheader("📢 Share Your Result")
    share_text = f"I just ran '{user_thought_input}' through the Quantum CBT/DBT Engine! Restored stability from {baseline_stability} to {m['new_stability']} using Hilbert Space statevector steering. Try it out: https://github.com/JonathanReiser/quantum-orch-or"
    encoded_share = urllib.parse.quote(share_text)

    share_col1, share_col2 = st.columns(2)
    with share_col1:
        st.markdown(f"[📲 Share on X / Twitter](https://twitter.com/intent/tweet?text={encoded_share})")
    with share_col2:
        st.markdown(f"[💼 Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/JonathanReiser/quantum-orch-or)")
