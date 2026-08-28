"""
quantum_economics.py — Quantum Economics & Financial Market Engine

Applies quantum statevectors, Hilbert space non-orthogonal projections, financial news
order effects, and Bell state liquidity contagion to model asset pricing, market panics,
and systemic economic stability.
"""

import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class QuantumMarketSentimentModel:
    def __init__(self, num_assets=2, initial_sentiment="superposition"):
        self.num_assets = num_assets
        self.simulator = AerSimulator()
        self.theta = np.pi / 4 if initial_sentiment == "superposition" else (0.1 if initial_sentiment == "bullish" else 1.4)

    def evolve_sentiment(self, market_shock=0.0, steps=20):
        """
        Evolves market asset sentiment statevector under financial shocks.
        """
        history_p_bull = []
        history_p_bear = []
        history_action = []

        accumulated_action = 0.0
        dt = 0.02
        hbar = 1.0545718e-34

        for s in range(steps):
            # Apply shock drift and thermal market noise
            noise = np.random.normal(0, 0.03)
            self.theta = np.clip(self.theta + market_shock * 0.05 + noise, 0.0, np.pi / 2)

            p_bull = float(np.cos(self.theta) ** 2)
            p_bear = float(np.sin(self.theta) ** 2)

            # Calculate Shannon Market Entropy
            entropy = -(p_bull * np.log2(p_bull + 1e-9) + p_bear * np.log2(p_bear + 1e-9))
            accumulated_action += 0.035 * (1.0 + entropy) * dt

            history_p_bull.append(p_bull)
            history_p_bear.append(p_bear)
            history_action.append(accumulated_action)

        return {
            "p_bullish": history_p_bull,
            "p_bearish": history_p_bear,
            "accumulated_action": history_action
        }

class QuantumFinancialOrderEffect:
    """
    Models financial news disclosure order effects (AB != BA).
    E.g. Inflation Report (A) followed by Fed Rate Decision (B) vs vice-versa.
    """
    def __init__(self):
        self.simulator = AerSimulator()

    def simulate_news_sequence(self, angle_A=0.5, angle_B=0.8):
        # Path AB: News A then News B
        qc_ab = QuantumCircuit(1)
        qc_ab.ry(angle_A, 0)
        qc_ab.rx(angle_B, 0)
        qc_ab.save_statevector()
        
        t_ab = transpile(qc_ab, self.simulator)
        res_ab = self.simulator.run(t_ab).result()
        sv_ab = np.array(res_ab.get_statevector(t_qc if 't_qc' in locals() else t_ab))
        p_bull_ab = float(np.abs(sv_ab[0]) ** 2)

        # Path BA: News B then News A
        qc_ba = QuantumCircuit(1)
        qc_ba.rx(angle_B, 0)
        qc_ba.ry(angle_A, 0)
        qc_ba.save_statevector()

        t_ba = transpile(qc_ba, self.simulator)
        res_ba = self.simulator.run(t_ba).result()
        sv_ba = np.array(res_ba.get_statevector(t_ba))
        p_bull_ba = float(np.abs(sv_ba[0]) ** 2)

        return {
            "path_AB_bullish_pct": round(p_bull_ab * 100, 1),
            "path_BA_bullish_pct": round(p_bull_ba * 100, 1),
            "order_effect_delta": round(abs(p_bull_ab - p_bull_ba) * 100, 1)
        }

class QuantumLiquidityContagion:
    """
    Models systemic bank runs / crypto liquidity crunches as Bell state entanglement collapse (|Phi+>).
    """
    def __init__(self, num_institutions=2):
        self.num_institutions = num_institutions
        self.simulator = AerSimulator()

    def simulate_contagion(self, shock_severity=0.8):
        qc = QuantumCircuit(self.num_institutions)
        qc.h(0)
        for i in range(self.num_institutions - 1):
            qc.cx(i, i + 1)
            
        qc.rx(shock_severity, 0)
        qc.save_statevector()

        t_qc = transpile(qc, self.simulator)
        res = self.simulator.run(t_qc).result()
        sv = np.array(res.get_statevector(t_qc))
        probs = np.abs(sv) ** 2

        # 00 = Both Solvent, 11 = Both Default (Cascading Liquidity Run)
        return {
            "p_both_solvent": float(probs[0]),
            "p_both_default": float(probs[-1]),
            "contagion_correlation": float(probs[0] + probs[-1])
        }

def run_quantum_econ_benchmark(output_plot="quantum_econ_results.png"):
    print(f"==================================================")
    print(f"   QUANTUM ECONOMICS & FINANCIAL MARKET ENGINE   ")
    print(f"==================================================")

    # 1. Market Sentiment Simulation
    sentiment_model = QuantumMarketSentimentModel(initial_sentiment="superposition")
    sent_res = sentiment_model.evolve_sentiment(market_shock=0.2, steps=30)
    print(f"1. Market Sentiment Evolution (30 Steps):")
    print(f"   Final Bullish Prob: {sent_res['p_bullish'][-1]*100:.1f}% | Final Bearish Prob: {sent_res['p_bearish'][-1]*100:.1f}%\n")

    # 2. Financial News Order Effects
    order_engine = QuantumFinancialOrderEffect()
    order_res = order_engine.simulate_news_sequence(angle_A=0.6, angle_B=0.9)
    print(f"2. Financial News Order Effects (Non-Commutativity):")
    print(f"   Path A -> B (Inflation then Fed Rate): {order_res['path_AB_bullish_pct']}% Bullish")
    print(f"   Path B -> A (Fed Rate then Inflation): {order_res['path_BA_bullish_pct']}% Bullish")
    print(f"   Order Shift Delta:                     {order_res['order_effect_delta']}%\n")

    # 3. Systemic Liquidity Contagion
    contagion_engine = QuantumLiquidityContagion()
    contagion_res = contagion_engine.simulate_contagion(shock_severity=0.85)
    print(f"3. Systemic Liquidity Contagion (Bell State Entanglement):")
    print(f"   Probability Both Solvent: {contagion_res['p_both_solvent']*100:.1f}%")
    print(f"   Probability Both Default: {contagion_res['p_both_default']*100:.1f}%")
    print(f"   Systemic Correlation:     {contagion_res['contagion_correlation']*100:.1f}%\n")

    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    steps = range(1, 31)
    axes[0].plot(steps, [p * 100 for p in sent_res['p_bullish']], color="#00f2fe", label="Bullish Sentiment (%)", linewidth=2)
    axes[0].plot(steps, [p * 100 for p in sent_res['p_bearish']], color="#ef4444", label="Bearish Sentiment (%)", linewidth=2)
    axes[0].set_xlabel("Time Step (t)")
    axes[0].set_ylabel("Probability (%)")
    axes[0].set_title("1. Market Sentiment Superposition Drift")
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend()

    categories = ["Path A->B (Inflation first)", "Path B->A (Fed Rate first)"]
    vals = [order_res['path_AB_bullish_pct'], order_res['path_BA_bullish_pct']]
    axes[1].bar(categories, vals, color=["#00f2fe", "#a855f7"], width=0.4)
    axes[1].set_ylabel("Bullish Sentiment (%)")
    axes[1].set_title(f"2. Financial News Order Effect (Delta = {order_res['order_effect_delta']}%)")
    axes[1].set_ylim(0, 100)
    for i, v in enumerate(vals):
        axes[1].text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    print(f"📊 Quantum Economics plot saved to {output_plot}")

    return {
        "sentiment": sent_res,
        "order_effect": order_res,
        "contagion": contagion_res
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Quantum Economics Engine")
    parser.add_argument("--output", type=str, default="quantum_econ_results.png", help="Output plot path")
    args = parser.parse_args()

    run_quantum_econ_benchmark(output_plot=args.output)
