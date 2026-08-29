"""
cli.py — Main Command Line Interface executable via `q-ai-gov`
"""

import sys
import json
import argparse
import numpy as np

try:
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
    from q_ai_governance.dao_budget_allocator import DAOBudgetAllocator, sample_proposals
    from q_ai_governance.benchmark_real_dao_data import RealDAOBenchmarkRunner
    from q_ai_governance.snapshot_live_oracle import SnapshotLiveOracle
    from q_ai_governance.quantum_economics import run_quantum_econ_benchmark
    from q_ai_governance.quantum_crypto_engine import QuantumCryptoPredictor
    from q_ai_governance.crypto_recommendations import QuantumCryptoRecommendationOracle
    from q_ai_governance.uniswap_quantum_governance import UniswapQuantumGovernor
    from q_ai_governance.q_ai_bot import QAIGovernanceBot
    from q_ai_governance.q_ai_twitter_bot import QAITwitterBot
    from q_ai_governance.quantum_psychiatry_engine import QuantumPsychiatrySimulator
    from q_ai_governance.quantum_economics_engine import QuantumEconomicsSimulator
    from q_ai_governance.market_phase_collapse_bot import MarketPhaseCollapseBot
    from q_ai_governance.uniswap_v4_hook_oracle import UniswapV4HookOracle
except ImportError:
    from quantum_agent import QuantumOrchORAgent
    from dao_budget_allocator import DAOBudgetAllocator, sample_proposals
    from benchmark_real_dao_data import RealDAOBenchmarkRunner
    from snapshot_live_oracle import SnapshotLiveOracle
    from quantum_economics import run_quantum_econ_benchmark
    from quantum_crypto_engine import QuantumCryptoPredictor
    from crypto_recommendations import QuantumCryptoRecommendationOracle
    from uniswap_quantum_governance import UniswapQuantumGovernor
    from q_ai_bot import QAIGovernanceBot
    from q_ai_twitter_bot import QAITwitterBot
    from quantum_psychiatry_engine import QuantumPsychiatrySimulator
    from quantum_economics_engine import QuantumEconomicsSimulator
    from market_phase_collapse_bot import MarketPhaseCollapseBot
    from uniswap_v4_hook_oracle import UniswapV4HookOracle

def main():
    parser = argparse.ArgumentParser(
        prog="q-ai-gov",
        description="Q-AI Governance: Quantum-Cognitive AI Policy & DAO Decision Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: app
    app_parser = subparsers.add_parser("app", help="Launch Streamlit Quantum Market Phase Dashboard")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit DAO proposal and generate Quantum Security Certificate")
    audit_parser.add_argument("--proposal-id", type=str, default="PROP-101", help="Proposal ID")
    audit_parser.add_argument("--yes", type=int, default=550000, help="YES vote count")
    audit_parser.add_argument("--no", type=int, default=450000, help="NO vote count")
    audit_parser.add_argument("--category", type=str, default="Public Goods", help="Proposal Category")
    audit_parser.add_argument("--output", type=str, default="dao_security_certificate.json", help="Output JSON path")

    # Subcommand: serve
    serve_parser = subparsers.add_parser("serve", help="Fetch real-time Quantitative Trading API signal")
    serve_parser.add_argument("--asset", type=str, default="BTC", help="Crypto or Equity Ticker (e.g. BTC, ETH, SOL, NVDA)")

    # Subcommand: give
    give_parser = subparsers.add_parser("give", help="Audit Base L2 non-profit grant impact and issue Q-Giving proof")
    give_parser.add_argument("--nonprofit", type=str, default="Clean Water Initiative", help="Non-Profit Organization Name")
    give_parser.add_argument("--grant-usd", type=float, default=25000.0, help="Grant Amount in USD")

    # Subcommand: hook
    hook_parser = subparsers.add_parser("hook", help="Generate Uniswap v4 Q-AI Governance Hook deployment payload")
    hook_parser.add_argument("--output", type=str, default="uniswap_v4_hook_payload.json", help="Output JSON path")

    # Subcommand: market-bot
    mkt_parser = subparsers.add_parser("market-bot", help="Run Quantum Market Phase Collapse Signal Bot")
    mkt_parser.add_argument("--output", type=str, default="market_signals_report.json", help="Output JSON path")

    # Subcommand: econ-full
    econ_full_parser = subparsers.add_parser("econ-full", help="Run Quantum Economics simulation & paper generator")
    econ_full_parser.add_argument("--plot", type=str, default="quantum_economics_benchmark_plot.png", help="Output plot path")
    econ_full_parser.add_argument("--paper", type=str, default="quantum_economics_paper.md", help="Output paper path")

    # Subcommand: psychiatry
    psy_parser = subparsers.add_parser("psychiatry", help="Run Quantum Psychiatry simulation & paper generator")
    psy_parser.add_argument("--plot", type=str, default="psychiatry_benchmark_plot.png", help="Output plot path")
    psy_parser.add_argument("--paper", type=str, default="quantum_psychiatry_paper.md", help="Output paper path")

    # Subcommand: uniswap
    uni_parser = subparsers.add_parser("uniswap", help="Run Uniswap-specific governance simulation and proposal generator")
    uni_parser.add_argument("--output", type=str, default="UNISWAP_GOVERNANCE_PROPOSAL.md", help="Output proposal path")

    # Subcommand: recommend

    # Subcommand: recommend
    rec_parser = subparsers.add_parser("recommend", help="Generate live quantitative Q-AI crypto trade signals")
    rec_parser.add_argument("--output", type=str, default="crypto_recommendations_report.json", help="Output JSON report path")

    # Subcommand: crypto

    # Subcommand: crypto
    crypto_parser = subparsers.add_parser("crypto", help="Forecast crypto price direction and target levels")
    crypto_parser.add_argument("--asset", type=str, default="BTC", help="Asset Code (BTC, ETH, SOL, ARB, OP)")
    crypto_parser.add_argument("--output", type=str, default="crypto_benchmark_plot.png", help="Output plot path")

    # Subcommand: tweet

    # Subcommand: tweet
    tweet_parser = subparsers.add_parser("tweet", help="Generate Twitter/X 280-character Q-AI forecast cards")
    tweet_parser.add_argument("--simulate", action="store_true", help="Print live tweet cards in terminal")

    # Subcommand: bot

    # Subcommand: bot
    bot_parser = subparsers.add_parser("bot", help="Run Telegram & Discord Governance Alert Bot")
    bot_parser.add_argument("--simulate", action="store_true", help="Print live alerts in terminal")

    # Subcommand: econ

    # Subcommand: econ
    econ_parser = subparsers.add_parser("econ", help="Run Quantum Economics & Financial Market simulation")
    econ_parser.add_argument("--output", type=str, default="quantum_econ_results.png", help="Output plot path")

    # Subcommand: live
    live_parser = subparsers.add_parser("live", help="Pull and predict live active proposals from Snapshot API")
    live_parser.add_argument("--output", type=str, default="live_snapshot_predictions.json", help="Output JSON report path")

    # Subcommand: allocate
    alloc_parser = subparsers.add_parser("allocate", help="Allocate DAO budget across competing proposals")
    alloc_parser.add_argument("--budget", type=float, default=1000000.0, help="Total Treasury Budget ($)")
    alloc_parser.add_argument("--output", type=str, default="budget_allocation_report.json", help="Output JSON report path")

    # Subcommand: predict
    pred_parser = subparsers.add_parser("predict", help="Predict real Snapshot DAO proposal vote approval")
    pred_parser.add_argument("--public-good", type=float, required=True, help="Public Good Score (1.0 - 10.0)")
    pred_parser.add_argument("--roi", type=float, required=True, help="Ecosystem ROI Score (1.0 - 10.0)")

    # Subcommand: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run Snapshot DAO benchmark suite against real vote data")
    bench_parser.add_argument("--output", type=str, default="real_dao_benchmark_plot.png", help="Output plot path")

    args = parser.parse_args()

    if args.command == "app":
        import subprocess
        app_path = os.path.join(os.path.dirname(__file__), "app.py")
        subprocess.run(["streamlit", "run", app_path])

    elif args.command == "audit":
        from q_ai_governance.dao_security_oracle import DAOSecurityOracle
        oracle = DAOSecurityOracle()
        cert = oracle.audit_proposal(
            proposal_id=args.proposal_id,
            yes_votes=args.yes,
            no_votes=args.no,
            category=args.category
        )
        oracle.export_certificate(cert, output_file=args.output)
        print(f"🔒 B2B DAO Security Certificate exported to {args.output}")
        print(json.dumps(cert, indent=2))

    elif args.command == "serve":
        from q_ai_governance.market_signal_api import MarketSignalAPI
        api = MarketSignalAPI()
        res = api.get_signal(asset=args.asset)
        print(f"📈 Quantitative Trading API Signal [{args.asset}]")
        print(json.dumps(res, indent=2))

    elif args.command == "give":
        from q_ai_governance.q_ai_giving_portal import QGivingPortal
        portal = QGivingPortal()
        res = portal.audit_giving_grant(nonprofit_name=args.nonprofit, grant_amount_usd=args.grant_usd)
        print(f"🎁 Base L2 Q-Giving Philanthropy Impact Audit [{args.nonprofit}]")
        print(json.dumps(res, indent=2))

    elif args.command == "hook":
        oracle = UniswapV4HookOracle()
        oracle.generate_hook_deployment_summary(output_json=args.output)

    elif args.command == "market-bot":
        bot = MarketPhaseCollapseBot()
        bot.run_market_scan(output_json=args.output)

    elif args.command == "econ-full":
        sim = QuantumEconomicsSimulator()
        sim.run_economics_benchmark(output_plot=args.plot, output_paper=args.paper)

    elif args.command == "psychiatry":
        sim = QuantumPsychiatrySimulator()
        sim.run_psychiatry_benchmark(output_plot=args.plot, output_paper=args.paper)

    elif args.command == "uniswap":
        governor = UniswapQuantumGovernor()
        governor.run_uniswap_benchmark()
        governor.generate_uniswap_forum_proposal(output_md=args.output)

    elif args.command == "recommend":
        oracle = QuantumCryptoRecommendationOracle()
        summary = oracle.generate_recommendations()

    elif args.command == "crypto":
        predictor = QuantumCryptoPredictor(asset=args.asset)
        res = predictor.predict_market_direction()
        print(f"📈 Running Q-AI Crypto Market Forecast for {res['asset']}...")
        print(f"Current Price: ${res['current_price']:,.2f} | Q-AI Target: ${res['q_ai_target_price']:,.2f} ({res['prob_bullish_pct']}% Bullish)")
        predictor.generate_crypto_chart(res, output_plot=args.output)

    elif args.command == "tweet":
        bot = QAITwitterBot()
        tweets = bot.generate_tweet_cards()
        print(f"🔮 Generated {len(tweets)} Twitter/X Q-AI Forecast Cards:\n")
        for i, card in enumerate(tweets, 1):
            print(f"--- TWEET #{i} ({len(card)} chars) ---\n{card}\n")

    elif args.command == "bot":
        bot = QAIGovernanceBot()
        alerts = bot.generate_alerts()
        print(f"🤖 Generated {len(alerts)} Q-AI Governance Alerts:\n")
        for i, a in enumerate(alerts, 1):
            print(f"--- ALERT #{i} ---\n{a}")

    elif args.command == "econ":
        run_quantum_econ_benchmark(output_plot=args.output)

    elif args.command == "live":
        print(f"📡 Connecting to Snapshot GraphQL API...")
        oracle = SnapshotLiveOracle()
        summary = oracle.predict_live_proposals()
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Live Snapshot predictions saved to {args.output}")

    elif args.command == "allocate":
        print(f"⚡ Running Q-AI DAO Budget Allocator for ${args.budget:,.2f} Treasury...")
        allocator = DAOBudgetAllocator(total_budget=args.budget)
        props = sample_proposals()
        report = allocator.allocate_budget(props)
        allocator.generate_report_file(report, output_json=args.output)
        print(f"✅ Budget allocation complete. Total Allocated: ${report['total_allocated']:,.2f} ({report['consensus_score']:.1f}% Consensus)")

    elif args.command == "predict":
        print(f"🔮 Predicting Snapshot DAO Proposal Vote Approval...")
        obs = np.array([args.public_good, args.roi], dtype=np.float32)
        agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)
        
        yes_count = 0
        for _ in range(50):
            idx, _, _, _, _ = agent.deliberate_and_act(obs)
            if idx % 2 == 0:
                yes_count += 1
                
        pred_pct = (yes_count / 50.0) * 100.0
        print(f"\n==================================================")
        print(f"  Q-AI PREDICTIVE GOVERNANCE ORACLE RESULT         ")
        print(f"==================================================")
        print(f"Public Good Score: {args.public_good}/10.0")
        print(f"Ecosystem ROI Score: {args.roi}/10.0")
        print(f"Predicted Proposal Vote Approval: {pred_pct:.1f}% (YES)\n")

    elif args.command == "benchmark":
        print(f"📊 Running Real Snapshot DAO Benchmark Suite...")
        runner = RealDAOBenchmarkRunner()
        summary = runner.run_benchmark()
        runner.generate_benchmark_plot(summary, output_plot=args.output)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
