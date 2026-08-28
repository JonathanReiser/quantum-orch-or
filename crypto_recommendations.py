"""
crypto_recommendations.py — Live Crypto Q-AI Recommendation Oracle

Generates quantitative trade signals (BULLISH_BUY, BEARISH_SELL, NEUTRAL_HOLD), target price
forecasts, and stop-loss risk boundaries using Q-AI Hilbert space statevector deliberation.
"""

import json
import argparse
import numpy as np

try:
    from q_ai_governance.quantum_crypto_engine import QuantumCryptoPredictor
except ImportError:
    from quantum_crypto_engine import QuantumCryptoPredictor

SUPPORTED_ASSETS = ["BTC", "ETH", "SOL", "ARB", "OP"]

class QuantumCryptoRecommendationOracle:
    def __init__(self, assets=None):
        self.assets = assets or SUPPORTED_ASSETS

    def generate_recommendations(self):
        print(f"==================================================")
        print(f"  QUANTUM-COGNITIVE CRYPTO RECOMMENDATION ORACLE  ")
        print(f"==================================================")
        print(f"Assets Evaluated: {', '.join(self.assets)}\n")

        results = []

        for asset in self.assets:
            predictor = QuantumCryptoPredictor(asset=asset)
            res = predictor.predict_market_direction()

            current = res["current_price"]
            prob_bull = res["prob_bullish_pct"]
            target = res["q_ai_target_price"]

            # Signal Logic
            if prob_bull >= 70.0:
                signal = "BULLISH_BUY"
                stop_loss = round(current * 0.96, 2)
                signal_icon = "🟢"
            elif prob_bull <= 35.0:
                signal = "BEARISH_SELL"
                stop_loss = round(current * 1.04, 2)
                signal_icon = "🔴"
            else:
                signal = "NEUTRAL_HOLD"
                stop_loss = round(current * 0.98, 2)
                signal_icon = "🟡"

            confidence = round(max(prob_bull, 100.0 - prob_bull), 1)

            rec = {
                "asset": asset,
                "signal": signal,
                "signal_icon": signal_icon,
                "confidence_pct": confidence,
                "current_price": current,
                "target_price_24h": target,
                "stop_loss_price": stop_loss,
                "volatility_risk": res["risk_level"]
            }
            results.append(rec)

            print(f"[{asset}] Signal: {signal_icon} {signal} (Confidence: {confidence}%)")
            print(f"   Current: ${current:,.2f} | Target 24h: ${target:,.2f} | Stop-Loss: ${stop_loss:,.2f}")
            print(f"   Risk Level: {res['risk_level']}\n")

        summary = {
            "assets_evaluated": len(self.assets),
            "disclaimer": "Quantitative Q-AI statistical signals for informational research purposes.",
            "recommendations": results
        }

        return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Live Crypto Q-AI Recommendation Oracle")
    parser.add_argument("--json", type=str, default="crypto_recommendations_report.json", help="Output JSON path")
    args = parser.parse_args()

    oracle = QuantumCryptoRecommendationOracle()
    summary = oracle.generate_recommendations()

    with open(args.json, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Crypto Q-AI Recommendations saved to {args.json}")
