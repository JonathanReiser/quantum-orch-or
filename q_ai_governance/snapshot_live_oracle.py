"""
snapshot_live_oracle.py — Live Snapshot GraphQL API Q-AI Governance Oracle

Connects to the official Snapshot GraphQL API (https://hub.snapshot.org/graphql)
to pull live, active governance proposals from major Web3 DAOs (Uniswap, Arbitrum,
Optimism, Gitcoin, Aave), evaluating them with Q-AI Hilbert space statevector models.
"""

import json
import urllib.request
import argparse
import numpy as np

try:
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
except ImportError:
    from quantum_agent import QuantumOrchORAgent

SNAPSHOT_GRAPHQL_URL = "https://hub.snapshot.org/graphql"

DEFAULT_SPACES = [
    "uniswap.eth",
    "arbitrumfoundation.eth",
    "opgovernance.eth",
    "gitcoindao.eth",
    "aave.eth"
]

GRAPHQL_QUERY = """
query Proposals($spaces: [String]) {
  proposals(
    first: 10,
    skip: 0,
    where: {
      space_in: $spaces
    },
    orderBy: "created",
    orderDirection: desc
  ) {
    id
    title
    body
    choices
    start
    end
    state
    votes
    scores_total
    space {
      id
      name
    }
  }
}
"""

class SnapshotLiveOracle:
    def __init__(self, spaces=None):
        self.spaces = spaces or DEFAULT_SPACES

    def fetch_live_proposals(self):
        req_data = json.dumps({
            "query": GRAPHQL_QUERY,
            "variables": {"spaces": self.spaces}
        }).encode("utf-8")

        req = urllib.request.Request(
            SNAPSHOT_GRAPHQL_URL,
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "Q-AI-Governance-Oracle/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("data", {}).get("proposals", [])
        except Exception as e:
            print(f"⚠️ Live API warning: {e}. Falling back to sample proposals.")
            return self._fallback_proposals()

    def _fallback_proposals(self):
        return [
            {
                "id": "0x1111111111",
                "title": "Uniswap Grants Program v4 Treasury Proposal",
                "body": "Fund public goods and developer grants across 2026 Q3.",
                "choices": ["For", "Against", "Abstain"],
                "state": "active",
                "votes": 4200,
                "scores_total": 1250000.0,
                "space": {"id": "uniswap.eth", "name": "Uniswap"}
            },
            {
                "id": "0x2222222222",
                "title": "Arbitrum Gaming Catalyst Fund Allocation",
                "body": "Allocate 200M ARB to ecosystem gaming initiatives.",
                "choices": ["For", "Against"],
                "state": "active",
                "votes": 8900,
                "scores_total": 8500000.0,
                "space": {"id": "arbitrumfoundation.eth", "name": "Arbitrum"}
            }
        ]

    def predict_live_proposals(self, proposals=None):
        if proposals is None:
            proposals = self.fetch_live_proposals()

        print(f"\n==================================================")
        print(f"  FETCHING LIVE SNAPSHOT DAO GOVERNANCE PROPOSALS  ")
        print(f"==================================================")
        print(f"Active Spaces Monitored: {', '.join(self.spaces)}")
        print(f"Total Live Proposals Fetched: {len(proposals)}\n")

        results = []
        agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)

        for prop in proposals:
            title = prop.get("title", "Untitled Proposal")
            space_name = prop.get("space", {}).get("name", "Unknown DAO")
            space_id = prop.get("space", {}).get("id", "")
            state_str = prop.get("state", "active").upper()
            votes_cnt = prop.get("votes", 0)
            
            # Extract features from title/body
            title_len = len(title)
            is_grant_or_public_good = any(k in title.lower() for k in ["grant", "public", "fund", "catalyst", "treasury"])
            
            public_good_score = 9.0 if is_grant_or_public_good else 6.5
            roi_score = 8.5 if "treasury" in title.lower() or "fund" in title.lower() else 7.0
            
            obs = np.array([public_good_score, roi_score], dtype=np.float32)
            
            yes_count = 0
            for _ in range(50):
                idx, _, _, _, _ = agent.deliberate_and_act(obs)
                if idx % 2 == 0:
                    yes_count += 1

            predicted_yes_pct = round((yes_count / 50.0) * 100.0, 1)
            predicted_no_pct = round(100.0 - predicted_yes_pct, 1)
            
            consensus_risk = "LOW" if predicted_yes_pct >= 75.0 else ("MEDIUM" if predicted_yes_pct >= 55.0 else "HIGH")

            results.append({
                "space": space_name,
                "space_id": space_id,
                "proposal_id": prop.get("id", ""),
                "title": title,
                "state": state_str,
                "votes_count": votes_cnt,
                "predicted_yes_pct": predicted_yes_pct,
                "predicted_no_pct": predicted_no_pct,
                "consensus_risk": consensus_risk
            })

            risk_icon = "🟢" if consensus_risk == "LOW" else ("🟡" if consensus_risk == "MEDIUM" else "🔴")
            print(f"[{space_name}] {title[:50]}...")
            print(f"   State: {state_str} | Votes: {votes_cnt:,}")
            print(f"   Q-AI Vote Prediction: {predicted_yes_pct}% YES / {predicted_no_pct}% NO | Risk: {risk_icon} {consensus_risk}\n")

        summary = {
            "monitored_spaces": self.spaces,
            "total_proposals": len(proposals),
            "proposals": results
        }

        return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Live Snapshot API Q-AI Oracle")
    parser.add_argument("--json", type=str, default="live_snapshot_predictions.json", help="Output JSON path")
    args = parser.parse_args()

    oracle = SnapshotLiveOracle()
    summary = oracle.predict_live_proposals()

    with open(args.json, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Live Snapshot predictions saved to {args.json}")
