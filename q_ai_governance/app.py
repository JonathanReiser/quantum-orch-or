"""
app.py — Interactive Streamlit Dashboard for Quantum Market Phase Collapse Signals.
"""

import time
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from market_phase_collapse_bot import MarketPhaseCollapseBot
except ImportError:
    from q_ai_governance.market_phase_collapse_bot import MarketPhaseCollapseBot

st.set_page_config(
    page_title="Q-AI Quantum Market Phase Dashboard",
    page_icon="⚡",
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
        border: 1px solid #475569;
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
    .status-green {
        color: #10b981;
        font-weight: bold;
    }
    .status-yellow {
        color: #f59e0b;
        font-weight: bold;
    }
    .status-red {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.title("⚡ Quantum-Cognitive AI Market Phase Dashboard")
st.markdown("""
Real-time Quantum Statevector Phase Scanner powered by **Lindblad Thermal Decoherence ($\gamma_\phi$)** 
and **Penrose Orchestrated Objective Reduction (Orch-OR)**.  
*Published Paper DOI:* [`10.5281/zenodo.22151233`](https://zenodo.org/records/22151233) | *PyPI SDK:* `pip install q-ai-governance`
""")

# ALWAYS-VISIBLE Legend Callout Banner (No Hovering or Clicking Needed!)
st.markdown("""
<div class="info-banner">
    <h3 style="margin-top:0; color:#38bdf8;">📖 Dashboard Guide: Key Metrics & Risk Thresholds</h3>
    <ul style="line-height: 1.6; font-size: 10.5pt;">
        <li>📈 <strong>P(BULL) & 📉 P(BEAR):</strong> The <strong>Probability (%)</strong> of the asset moving UP (Bullish) vs DOWN (Bearish), calculated via quantum statevector projection (|⟨BULL|ψ⟩|²).</li>
        <li>🌀 <strong>Dephasing Noise (γ_ϕ):</strong> Measures <strong>market panic & order-book confusion</strong> (0.00 = Perfectly Calm, >0.70 = Extreme Panic).</li>
        <li>⚛️ <strong>Penrose Threshold (S_crit = 1.00):</strong> Measures spacetime quantum collapse action. 
            When <strong>Penrose Action S(t) ≥ 1.00</strong>, a <strong>Statevector Collapse</strong> triggers an immediate market crash warning!</li>
        <li>🟢 <strong>LOW RISK (γ_ϕ < 0.40):</strong> Calm market harmony. Safe trend momentum.</li>
        <li>🟡 <strong>MEDIUM RISK (0.40 ≤ γ_ϕ ≤ 0.70):</strong> Rising social noise. Tighten stop-losses.</li>
        <li>🔴 <strong>HIGH RISK (γ_ϕ > 0.70 or S(t) ≥ 1.00):</strong> Panic collapse imminent! Impending crash warning.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("⚙️ Scanner Controls")
selected_assets = st.sidebar.multiselect(
    "Select Assets to Monitor:",
    ["BTC", "ETH", "SOL", "SPY", "QQQ", "NVDA", "TSLA"],
    default=["BTC", "ETH", "SOL", "SPY", "NVDA"]
)

sensitivity = st.sidebar.slider("Lindblad Dephasing Noise Sensitivity (γ_ϕ)", 0.1, 0.9, 0.6, 0.05)
auto_refresh = st.sidebar.checkbox("Auto Refresh Signals", value=False)

# Run Scanner
bot = MarketPhaseCollapseBot(assets=selected_assets)
bot.dephasing_rate = sensitivity
report = bot.run_market_scan()
asset_data = report["assets"]

st.subheader("📊 Live Market Risk Signals")

# Display Grid Cards
cols = st.columns(min(len(asset_data), 4))

for idx, item in enumerate(asset_data):
    col = cols[idx % len(cols)]
    with col:
        status_color = "status-green" if item['risk'] == "LOW" else ("status-yellow" if item['risk'] == "MEDIUM" else "status-red")
        penrose_status = "⚠️ COLLAPSE IMMINENT" if float(item['action_S']) >= 1.00 else "NORMAL"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{item['emoji']} {item['asset']}</h3>
            <p><strong>Phase State:</strong> <span class="{status_color}">{item['phase']}</span></p>
            <p><strong>Action Signal:</strong> <code>{item['signal']}</code></p>
            <hr style="border: 0.5px solid #475569;">
            <p>📈 <strong>P(BULL) Probability:</strong> <span style="font-weight:bold; color:#10b981;">{item['p_bull']}%</span></p>
            <p>📉 <strong>P(BEAR) Probability:</strong> <span style="font-weight:bold; color:#ef4444;">{item['p_bear']}%</span></p>
            <p>🌀 <strong>Dephasing Noise (γ_ϕ):</strong> {item['gamma_phi']} <em>(Threshold: 0.70)</em></p>
            <p>⚛️ <strong>Penrose Action S(t):</strong> {item['action_S']} <em>(Collapse Threshold = 1.00)</em></p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

st.markdown("---")

# Visualizations Layout
col_chart1, col_chart2 = st.columns(2)

df = pd.DataFrame(asset_data)

with col_chart1:
    st.subheader("🌀 Lindblad Dephasing Noise (γ_ϕ) by Asset")
    fig_bar = px.bar(
        df,
        x="asset",
        y="gamma_phi",
        color="risk",
        color_discrete_map={"LOW": "#10b981", "MEDIUM": "#f59e0b", "HIGH": "#ef4444"},
        title="Decoherence Noise Levels (Warning Threshold = 0.70)",
        labels={"gamma_phi": "Dephasing Noise γ_ϕ", "asset": "Asset"}
    )
    fig_bar.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    st.subheader("📈 Bullish Probability P(BULL) Comparison (%)")
    fig_pie = px.pie(
        df,
        names="asset",
        values="p_bull",
        title="Relative Bullish Confidence Probabilities (%)",
        hole=0.4
    )
    fig_pie.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_pie, use_container_width=True)

# Forecast Broadcast Card Section
st.subheader("📱 Social Media Broadcast Card Generator")
selected_card_asset = st.selectbox("Select Asset for 280-Char Broadcast Card:", selected_assets)
selected_item = next((x for x in asset_data if x["asset"] == selected_card_asset), asset_data[0])

card_text = (
    f"🔮 Q-AI Market Phase Signal [{selected_item['asset']}]\n"
    f"Phase: {selected_item['emoji']} {selected_item['phase']}\n"
    f"Signal: {selected_item['signal']} (Risk: {selected_item['risk']})\n"
    f"• Bullish Probability P(BULL): {selected_item['p_bull']}%\n"
    f"• Bearish Probability P(BEAR): {selected_item['p_bear']}%\n"
    f"• Dephasing Noise γ_ϕ: {selected_item['gamma_phi']} (Threshold 0.70)\n"
    f"• Penrose Action S(t): {selected_item['action_S']} (Collapse Threshold 1.00)\n"
    f"https://github.com/JonathanReiser/quantum-orch-or #QuantumAI #{selected_item['asset']}"
)

st.code(card_text, language="text")

if auto_refresh:
    time.sleep(5)
    st.rerun()
