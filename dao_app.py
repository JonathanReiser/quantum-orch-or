"""
dao_app.py — Interactive Streamlit Web Dashboard for DAO Treasury & Governance Security Audits.
"""

import time
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from dao_security_oracle import DAOSecurityOracle
except ImportError:
    from q_ai_governance.dao_security_oracle import DAOSecurityOracle

st.set_page_config(
    page_title="Q-AI B2B DAO Treasury Security Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #0284c7;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .info-banner {
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .status-pass {
        color: #10b981;
        font-weight: bold;
        font-size: 16pt;
    }
    .status-fail {
        color: #ef4444;
        font-weight: bold;
        font-size: 16pt;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.title("🏛️ Q-AI B2B DAO Treasury Security Audit Portal")
st.markdown("""
On-Chain Governance Proposal Risk Auditor enforcing **$80.00\%$ Quantum GHZ Entanglement Consensus** 
via [`Q_AIGovernanceHook.sol`](https://github.com/JonathanReiser/quantum-orch-or/blob/main/contracts/Q_AIGovernanceHook.sol).  
*CERN Zenodo DOI:* [`10.5281/zenodo.22151233`](https://zenodo.org/records/22151233) | *PyPI Package:* `pip install q-ai-governance`
""")

# Guide Banner
st.markdown("""
<div class="info-banner">
    <h3 style="margin-top:0; color:#38bdf8;">🎻 What is "Vote Vector Entanglement"? (The Orchestra Analogy)</h3>
    <ul style="line-height: 1.6; font-size: 10.5pt;">
        <li>🗣️ <strong>Classical Un-Entangled Voting (The Old Way):</strong> Votes are isolated numbers. A whale with 51% of tokens acts like a person shouting through a megaphone—he forces bad proposals through.</li>
        <li>🎻 <strong>Q-AI Entangled Voting (The New Way):</strong> Q-AI maps votes into an <i>N-qubit GHZ quantum entangled state</i>. Votes act like an <strong>Orchestra playing in harmony</strong>.</li>
        <li>🟢 <strong>Constructive Boost (Public-Good Alignment):</strong> Community members voting for public goods share phase harmony. Their waves entangle constructively, boosting consensus to <strong>≥ 80.00%</strong>!</li>
        <li>🔴 <strong>Destructive Cancellation (Whale Attack):</strong> A selfish whale voting to drain funds is out-of-phase. His wave entangles destructively and <strong>cancels itself out (1 - 1 = 0)</strong>!</li>
        <li>🔒 <strong>Tamper-Evident SHA-256 Proof:</strong> Every audit generates a cryptographic Qiskit proof hash executed on 127-qubit IBM Quantum hardware.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("⚙️ Audit Proposal Inputs")
selected_dao = st.sidebar.selectbox("Select Target DAO:", ["Uniswap DAO", "Arbitrum DAO", "Optimism Collective", "Gitcoin DAO", "Base Q-Giving"])
proposal_id = st.sidebar.text_input("Proposal ID:", "UNI-PROP-42")
category = st.sidebar.selectbox("Proposal Category:", ["Public Goods", "Security Audits", "Developer Infrastructure", "Selfish Extraction"])

yes_votes = st.sidebar.number_input("YES Votes Cast:", min_value=0, value=550000, step=10000)
no_votes = st.sidebar.number_input("NO Votes Cast:", min_value=0, value=450000, step=10000)
abstain_votes = st.sidebar.number_input("ABSTAIN Votes Cast:", min_value=0, value=0, step=5000)

# Run Audit
oracle = DAOSecurityOracle(dao_name=selected_dao)
cert = oracle.audit_proposal(
    proposal_id=proposal_id,
    yes_votes=yes_votes,
    no_votes=no_votes,
    abstain_votes=abstain_votes,
    category=category
)

score = cert["quantum_audit_metrics"]["quantum_consensus_score"]
passed = cert["smart_contract_execution"]

st.subheader("📊 Audit Results & Smart Contract Execution Status")

col1, col2 = st.columns([1, 1])

with col1:
    status_class = "status-pass" if passed else "status-fail"
    status_text = "🟢 APPROVED FOR PAYOUT" if passed else "🔴 BLOCKED & REJECTED"
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>🏛️ {selected_dao} — {proposal_id}</h3>
        <p><strong>Category:</strong> <code>{category}</code></p>
        <p><strong>Audit Decision:</strong> <span class="{status_class}">{status_text}</span></p>
        <hr style="border: 0.5px solid #334155;">
        <p>⚛️ <strong>Quantum Consensus Score:</strong> <span style="font-weight:bold; font-size:14pt; color:#38bdf8;">{cert['quantum_audit_metrics']['quantum_consensus_percentage']}</span></p>
        <p>🎯 <strong>Required Threshold:</strong> 80.00%</p>
        <p>📊 <strong>Raw YES Vote Ratio:</strong> {float(cert['raw_vote_tallies']['raw_yes_ratio']) * 100:.2f}%</p>
        <p>🌀 <strong>Lindblad Dephasing Rate (γ_ϕ):</strong> {cert['quantum_audit_metrics']['lindblad_dephasing_gamma_phi']}</p>
        <p>🔒 <strong>Enforced Hook:</strong> <code>{cert['enforced_hook']}</code></p>
        <p>🔑 <strong>SHA-256 Qiskit Proof:</strong> <code style="font-size:7pt;">{cert['qiskit_proof_hash']}</code></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("🎯 Consensus Score vs 80% Threshold Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Quantum Consensus Score (%)"},
        delta = {'reference': 80.0, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#38bdf8"},
            'steps': [
                {'range': [0, 80], 'color': "rgba(239, 68, 68, 0.2)"},
                {'range': [80, 100], 'color': "rgba(16, 185, 129, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80.0
            }
        }
    ))
    fig_gauge.update_layout(template="plotly_dark", height=320)
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# Security Certificate Download Section
st.subheader("📄 Download Official Quantum DAO Security Certificate")
cert_json = json.dumps(cert, indent=2)
st.download_button(
    label="📥 Download SHA-256 Quantum Security Certificate (JSON)",
    data=cert_json,
    file_name=f"{proposal_id}_security_certificate.json",
    mime="application/json"
)

st.code(cert_json, language="json")
