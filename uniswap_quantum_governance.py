"""
uniswap_quantum_governance.py — Uniswap-Specific Q-AI Governance Oracle & Forum Proposal Engine

Evaluates Uniswap v3/v4 governance proposals, v4 Hooks fee parameters, and delegate voting
dynamics using Hilbert space statevectors, generating a formal Uniswap Forum Proposal.
"""

import json
import os
import argparse
import numpy as np

try:
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
except ImportError:
    from quantum_agent import QuantumOrchORAgent

# Weights fit to real historical DAO outcomes by train_uniswap_governance_agent.py.
# If this file doesn't exist yet, QuantumOrchORAgent falls back to (documented,
# printed) random init rather than silently pretending to be trained.
TRAINED_WEIGHTS_PATH = os.path.join(
    os.path.dirname(__file__), "q_ai_governance", "trained_uniswap_agent_weights.npz"
)

UNISWAP_PROPOSALS = [
    {
        "id": "UNI-PROP-12",
        "title": "Uniswap v3 Deployment on Arbitrum One",
        "real_yes_pct": 98.4,
        "public_good_score": 9.5,
        "roi_score": 9.8
    },
    {
        "id": "UNI-PROP-18",
        "title": "v4 Hooks Security Audit & Developer Grant Fund",
        "real_yes_pct": 96.2,
        "public_good_score": 9.2,
        "roi_score": 9.4
    },
    {
        "id": "UNI-PROP-24",
        "title": "Protocol Fee Switch Activation & Dynamic Pool Tier Adjustment",
        "real_yes_pct": 58.4,
        "public_good_score": 6.1,
        "roi_score": 7.5
    }
]

class UniswapQuantumGovernor:
    def __init__(self):
        self.proposals = UNISWAP_PROPOSALS

    def run_uniswap_benchmark(self):
        results = []

        print("==================================================")
        print("  UNISWAP Q-AI GOVERNANCE ORACLE BENCHMARK       ")
        print("==================================================")

        for prop in self.proposals:
            public_good = prop["public_good_score"]
            roi = prop["roi_score"]
            real_vote = prop["real_yes_pct"]

            obs = np.array([public_good, roi], dtype=np.float32)

            agent = QuantumOrchORAgent(num_qubits=2, state_dim=2, weights_path=TRAINED_WEIGHTS_PATH)
            yes_count = 0
            for _ in range(50):
                idx, _, _, _, _ = agent.deliberate_and_act(obs)
                if idx % 2 == 0:
                    yes_count += 1

            q_ai_pred = round((yes_count / 50.0) * 100.0, 1)
            error = round(abs(q_ai_pred - real_vote), 1)

            res = {
                "id": prop["id"],
                "title": prop["title"],
                "real_vote_yes_pct": real_vote,
                "q_ai_predicted_yes_pct": q_ai_pred,
                "prediction_error_pct": error,
                "consensus_risk": "LOW" if q_ai_pred >= 80.0 else "MEDIUM"
            }
            results.append(res)

            print(f"[{prop['id']}] {prop['title']}")
            print(f"   Real Vote: {real_vote}% YES | Q-AI Forecast: {q_ai_pred}% YES | Error: {error}%\n")

        return results

    def generate_uniswap_forum_proposal(self, results=None, output_md="UNISWAP_GOVERNANCE_PROPOSAL.md"):
        """Renders the forum proposal from ACTUAL benchmark results — no hardcoded
        performance numbers. If results isn't passed, runs the benchmark itself."""
        if results is None:
            results = self.run_uniswap_benchmark()

        rows = "\n".join(
            f"| **{r['id']}** ({r['title']}) | **{r['real_vote_yes_pct']}%** | "
            f"**{r['q_ai_predicted_yes_pct']}%** | **{r['prediction_error_pct']}% Error** |"
            for r in results
        )
        mae = round(float(np.mean([r["prediction_error_pct"] for r in results])), 1)

        proposal_text = (
            "# [Proposal] Q-AI Governance Oracle: Quantum-Cognitive Vote Prediction & Fee Parameter Simulation for Uniswap v4\n\n"
            "**Author:** Jonathan Reiser (Quantum-Cognitive AI Systems)\n"
            "\n---\n\n"
            "> ## \u26a0\ufe0f Numbers below come from an n=3 sample fit by a procedure with a known defect\n"
            ">\n"
            "> See [CORRECTIONS.md](CORRECTIONS.md). This project's previously published\n"
            "> governance figures (\"835,000 Snapshot DAO votes\", \"86.7% error reduction\",\n"
            "> \"R\u00b2 = 0.98\") are retracted \u2014 they were not produced by the code that cited\n"
            "> them. The agent behind the table below was fit by a (1+1) hill climb that\n"
            "> never re-measures its incumbent, so it can accept nothing and still report a\n"
            "> flat, converged-looking loss. Do not cite these numbers as validated accuracy.\n"
            "> On the real 905-proposal Snapshot record, no model in this repository beats\n"
            "> predicting the historical median YES share.\n\n"
            "**Target Category:** Governance & Tooling / Grants\n"
            "**Live Visualizer:** https://jonathanreiser.github.io/quantum-orch-or/\n"
            "**GitHub Repository:** https://github.com/JonathanReiser/quantum-orch-or\n\n"
            "---\n\n"
            "## Executive Summary\n\n"
            "Uniswap governance represents one of the largest decentralized decision-making bodies in Web3. "
            "Classical voting models fail to capture non-commutative delegate preference shifts and framing order effects. "
            "Here we propose deploying the **Q-AI Governance Oracle**—a quantum-cognitive reinforcement learning engine "
            "governed by Penrose Orchestrated Objective Reduction (Orch-OR) statevector collapse.\n\n"
            "## Benchmarks on Real Uniswap Proposals\n\n"
            "We evaluated our Q-AI model, fit via leave-one-out cross-validation on a small set of historical "
            "Uniswap Snapshot governance votes (see `train_uniswap_governance_agent.py` in the repository for "
            "the fitting methodology). **This is a small sample (n=3 shown here) — treat these numbers as an "
            "early signal, not a statistically validated accuracy claim.**\n\n"
            "| Proposal ID & Title | Real Vote YES (%) | Q-AI Forecast YES (%) | Prediction Error |\n"
            "| :--- | :--- | :--- | :--- |\n"
            f"{rows}\n\n"
            f"**Mean Absolute Error on this sample:** {mae}pp.\n\n"
            "## Proposed Deliverables for Uniswap v4\n\n"
            "1. **Uniswap v4 Hooks Parameter Simulator:** Live simulation tool allowing delegates to model pool fee tier shifts and hook liquidity risks.\n"
            "2. **Delegate Alert Bot:** Real-time Telegram/Discord & X forecasting bot querying Snapshot GraphQL API.\n"
            "3. **Open-Source PyPI Library:** `pip install q-ai-governance` (`q-ai-gov`).\n\n"
            "## Grant Funding Request\n\n"
            "We request **$50,000 UNI** to fund full integration with Uniswap v4 Hooks telemetry, delegate dashboard UI, and smart contract simulation contracts.\n"
        )

        with open(output_md, "w") as f:
            f.write(proposal_text)

        print(f"📄 Formal Uniswap Forum Proposal saved to {output_md}")
        return output_md

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Uniswap Q-AI Governance Oracle")
    parser.add_argument("--output", type=str, default="UNISWAP_GOVERNANCE_PROPOSAL.md", help="Output Markdown proposal path")
    args = parser.parse_args()

    governor = UniswapQuantumGovernor()
    bench_results = governor.run_uniswap_benchmark()
    governor.generate_uniswap_forum_proposal(results=bench_results, output_md=args.output)
