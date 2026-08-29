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
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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

# Plain-English Legend Callout Box
with st.expander("📖 **What do Dephasing Noise (γ_ϕ) and Risk Levels mean? (Click to Expand)**", expanded=True):
    st.markdown("""
    * 🌀 **Dephasing Noise ($\gamma_\phi$):** Measures **market panic, confusion, and order-book noise**. Low noise means high harmony; high noise means chaotic panic.
    * 🟢 **LOW RISK ($\gamma_\phi < 0.40$):** Calm, harmonized market. Clear trend momentum. Safe to trade.
    * 🟡 **MEDIUM RISK ($0.40 \le \gamma_\phi \le 0.70$):** Rising market noise and conflicting social rumors. Tighten stop-losses.
    * 🔴 **HIGH RISK ($\gamma_\phi > 0.70$):** Extreme market panic! Penrose action triggers a **Statevector Collapse**, warning of an impending sharp drop.
    """)

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
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{item['emoji']} {item['asset']}</h3>
            <p><strong>Phase:</strong> <span class="{status_color}">{item['phase']}</span></p>
            <p><strong>Signal:</strong> <code>{item['signal']}</code></p>
            <hr style="border: 0.5px solid #334155;">
            <p>📈 <strong>P(BULL):</strong> {item['p_bull']}%</p>
            <p>📉 <strong>P(BEAR):</strong> {item['p_bear']}%</p>
            <p>🌀 <strong>Dephasing γ_ϕ:</strong> {item['gamma_phi']}</p>
            <p>⚛️ <strong>Penrose Action S(t):</strong> {item['action_S']}</p>
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
        title="Decoherence Noise Levels (Threshold = 0.70)",
        labels={"gamma_phi": "Dephasing Noise γ_ϕ", "asset": "Asset"}
    )
    fig_bar.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    st.subheader("⚛️ Statevector Bullish Confidence P(BULL)")
    fig_pie = px.pie(
        df,
        names="asset",
        values="p_bull",
        title="Bullish Statevector Distribution",
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
    f"• P(BULL): {selected_item['p_bull']}%\n"
    f"• Dephasing Noise γ_ϕ: {selected_item['gamma_phi']}\n"
    f"• Penrose Action S(t): {selected_item['action_S']}\n"
    f"https://github.com/JonathanReiser/quantum-orch-or #QuantumAI #{selected_item['asset']}"
)

st.code(card_text, language="text")

if auto_refresh:
    time.sleep(5)
    st.rerun()
