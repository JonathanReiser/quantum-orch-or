"""
q_ai_bot.py — Telegram & Discord Q-AI Governance Alert Bot

Monitors active Snapshot DAO proposals (Uniswap, Arbitrum, Optimism, Gitcoin, Aave),
running Q-AI Hilbert space predictions to format rich real-time alert notifications
for Telegram channels and Discord webhooks.
"""

import sys
import json
import urllib.request
import argparse

try:
    from q_ai_governance.snapshot_live_oracle import SnapshotLiveOracle
except ImportError:
    from snapshot_live_oracle import SnapshotLiveOracle

class QAIGovernanceBot:
    def __init__(self, spaces=None):
        self.oracle = SnapshotLiveOracle(spaces=spaces)

    def generate_alerts(self):
        summary = self.oracle.predict_live_proposals()
        alerts = []

        for prop in summary.get("proposals", []):
            space = prop.get("space", "DAO")
            title = prop.get("title", "Untitled Proposal")
            yes_pct = prop.get("predicted_yes_pct", 50.0)
            no_pct = prop.get("predicted_no_pct", 50.0)
            risk = prop.get("consensus_risk", "MEDIUM")
            votes = prop.get("votes_count", 0)

            risk_icon = "🟢" if risk == "LOW" else ("🟡" if risk == "MEDIUM" else "🔴")

            msg = (
                f"🚨 *Q-AI GOVERNANCE ALERT* 🚨\n"
                f"🏛️ *DAO:* {space}\n"
                f"📜 *Proposal:* {title[:60]}...\n"
                f"📊 *Current Turnout:* {votes:,} votes\n\n"
                f"🔮 *Q-AI Oracle Vote Forecast:*\n"
                f"   • YES Approval: *{yes_pct}%*\n"
                f"   • NO Rejection: *{no_pct}%*\n"
                f"⚡ *Consensus Risk:* {risk_icon} *{risk}*\n"
                f"🔗 *Live Dashboard:* https://jonathanreiser.github.io/quantum-orch-or/\n"
            )
            alerts.append(msg)

        return alerts

    def send_discord_webhook(self, webhook_url, alerts=None):
        if alerts is None:
            alerts = self.generate_alerts()

        sent_count = 0
        for alert in alerts[:3]: # Limit to top 3 for webhook payload
            payload = {"content": alert}
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status in [200, 204]:
                        sent_count += 1
            except Exception as e:
                print(f"⚠️ Discord webhook dispatch notice: {e}")
        return sent_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Q-AI Governance Alert Bot")
    parser.add_argument("--simulate", action="store_true", help="Print formatted live bot alerts in terminal")
    parser.add_argument("--webhook", type=str, help="Discord Webhook URL to dispatch alerts")

    args = parser.parse_args()
    bot = QAIGovernanceBot()
    alerts = bot.generate_alerts()

    print(f"\n==================================================")
    print(f"  Q-AI GOVERNANCE TELEGRAM & DISCORD BOT ALERTS    ")
    print(f"==================================================")
    print(f"Generated {len(alerts)} Real-Time Governance Alerts:\n")

    for i, alert_msg in enumerate(alerts, 1):
        print(f"--- ALERT #{i} ---")
        print(alert_msg)

    if args.webhook:
        count = bot.send_discord_webhook(args.webhook, alerts)
        print(f"✅ Dispatched {count} alerts to Discord webhook!")
