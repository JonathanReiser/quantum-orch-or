"""
Full Multi-Turn Conversational Q-AI LLM Web App (chat_q_ai_llm.py)
------------------------------------------------------------------
Interactive multi-turn chat interface with live quantum statevector trajectory tracking,
continuous phase interference filtering, and neural dialectical text generation.
"""

import streamlit as st
import numpy as np
from q_ai_governance.q_ai_cbt_dbt import QuantumCBTEngine
from q_ai_governance.q_ai_vector_steering import LatentVectorSteeringEngine
from q_ai_governance.q_ai_truth_alignment import TruthAlignedSteeringPipeline
from q_ai_governance.q_ai_neural_generator import NeuralDialecticalGenerator

st.set_page_config(
    page_title="Multi-Turn Q-AI Conversational Companion",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Multi-Turn Q-AI Conversational Companion")
st.markdown("""
*Have a continuous dialogue with the Q-AI LLM. The engine tracks your cognitive statevector trajectory across turns, applying continuous phase interference ($\cos\Delta\phi = -1$) and Wise Mind entanglement ($|\text{GHZ}_3\\rangle$).*
""")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stability_history" not in st.session_state:
    st.session_state.stability_history = [38.0]

if "cbt_engine" not in st.session_state:
    st.session_state.cbt_engine = QuantumCBTEngine(baseline_stability=38.0)

# Sidebar Trajectory & Metrics
st.sidebar.header("📊 Live Quantum Trajectory")
st.sidebar.write(f"**Current Emotional Stability:** {st.session_state.stability_history[-1]:.1f} / 100")
st.sidebar.line_chart(st.session_state.stability_history)

if st.sidebar.button("🔄 Reset Conversation"):
    st.session_state.messages = []
    st.session_state.stability_history = [38.0]
    st.session_state.cbt_engine = QuantumCBTEngine(baseline_stability=38.0)
    st.rerun()

# Display Conversation History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "metrics" in msg:
            m = msg["metrics"]
            st.caption(f"⚛️ Statevector Metrics: Stability = {m['new_stability']:.1f} (ΔS: +{m['stability_delta']}) | Wise Mind Coherence = {m['wise_mind_coherence'] * 100:.0f}%")

# Chat Input
if prompt := st.chat_input("Type your message to the Q-AI Assistant..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process Quantum Statevector Calculation
    current_stability = st.session_state.stability_history[-1]
    np.random.seed(abs(hash(prompt)) % (2**32))
    raw_embedding = np.random.randn(128)
    distortion_indices = np.array([0, 2, 4, 8, 12])

    cbt_engine = QuantumCBTEngine(baseline_stability=current_stability)
    res = cbt_engine.process_cognitive_cycle(raw_embedding, distortion_indices=distortion_indices, user_thought_text=prompt)
    m = res["metrics"]

    # Generate Neural Dialectical Response
    assistant_response = NeuralDialecticalGenerator.generate_reframe(prompt)

    # Update Trajectory History
    new_stability = m["new_stability"]
    st.session_state.stability_history.append(new_stability)

    # Add Assistant Message
    assistant_entry = {
        "role": "assistant",
        "content": assistant_response,
        "metrics": m
    }
    st.session_state.messages.append(assistant_entry)

    with st.chat_message("assistant"):
        st.write(assistant_response)
        st.caption(f"⚛️ Statevector Metrics: Stability = {m['new_stability']:.1f} (ΔS: +{m['stability_delta']}) | Wise Mind Coherence = {m['wise_mind_coherence'] * 100:.0f}%")

    st.rerun()
