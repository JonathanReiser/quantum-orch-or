"""
cli.py — Main Command Line Interface executable via `q-ai-gov`
"""

import sys
import os
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
        description="Q-AI Governance: exploratory quantum-cognition simulations and reproducible DAO analysis"
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

    # Subcommand: swarm
    swarm_parser = subparsers.add_parser("swarm", help="Evaluate Enterprise Multi-Agent AI Swarm Consensus")
    swarm_parser.add_argument("--task", type=str, default="Autonomous Fleet Path Optimization", help="Multi-Agent AI Task Description")
    swarm_parser.add_argument("--agents", type=int, default=5, help="Number of AI agents in swarm")

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
    live_parser = subparsers.add_parser(
        "live",
        help="Pull active Snapshot proposals and generate exploratory heuristic estimates",
    )
    live_parser.add_argument("--output", type=str, default="live_snapshot_estimates.json", help="Output JSON report path")

    # Subcommand: allocate
    alloc_parser = subparsers.add_parser("allocate", help="Allocate DAO budget across competing proposals")
    alloc_parser.add_argument("--budget", type=float, default=1000000.0, help="Total Treasury Budget ($)")
    alloc_parser.add_argument("--output", type=str, default="budget_allocation_report.json", help="Output JSON report path")

    # Subcommand: predict
    pred_parser = subparsers.add_parser(
        "predict",
        help="Run an exploratory statevector simulation from manual scores; not a vote forecast",
    )
    pred_parser.add_argument("--public-good", type=float, required=True, help="Manual synthetic input (1.0 - 10.0)")
    pred_parser.add_argument("--roi", type=float, required=True, help="Manual synthetic input (1.0 - 10.0)")
    pred_parser.add_argument("--shots", type=int, default=16, help="Toy-model measurement repetitions (default: 16)")

    # Subcommand: experiments
    experiment_parser = subparsers.add_parser(
        "experiments",
        help="List or run transparent decision-making experiments",
    )
    experiment_parser.add_argument("--list", action="store_true", help="List the experiment catalogue")
    experiment_parser.add_argument("--run", type=str, help="ID of a runnable local experiment")
    experiment_parser.add_argument("--data", type=str, help="Input dataset for the selected experiment")
    experiment_parser.add_argument("--test-frac", type=float, default=0.30, help="Held-out temporal fraction")
    experiment_parser.add_argument("--output", type=str, default="experiment_result.json", help="Destination JSON report")

    # Subcommand: ewl-tournament
    ewl_parser = subparsers.add_parser(
        "ewl-tournament",
        help="Run the EWL mechanism-blind control ladder (simulator + matched classical sampler)",
    )
    ewl_parser.add_argument("--p1", choices=["C", "D", "Q"], default="C", help="Player 1 strategy")
    ewl_parser.add_argument("--p2", choices=["C", "D", "Q"], default="D", help="Player 2 strategy")
    ewl_parser.add_argument("--entanglement", type=float, default=float(np.pi / 2), help="EWL gamma in [0, pi/2]")
    ewl_parser.add_argument("--rounds", type=int, default=100, help="Number of replayable sampled rounds")
    ewl_parser.add_argument("--seed", type=int, default=0, help="Pseudorandom seed recorded in the manifest")
    ewl_parser.add_argument("--output", type=str, default="ewl_tournament_report.json", help="Destination JSON report")

    # Subcommand: fetch-snapshot-data
    fetch_parser = subparsers.add_parser(
        "fetch-snapshot-data",
        help="Download closed, cleanly-binary Snapshot proposals for reproducible analysis",
    )
    fetch_parser.add_argument(
        "--output",
        type=str,
        default="snapshot_dao_dataset.json",
        help="Destination JSON path",
    )

    # Subcommand: benchmark
    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Run the temporal, hindsight-free Snapshot benchmark",
    )
    bench_parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Snapshot dataset JSON, produced by fetch-snapshot-data or supplied from a source checkout",
    )
    bench_parser.add_argument(
        "--test-frac",
        type=float,
        default=0.30,
        help="Fraction of the newest proposals reserved for testing (default: 0.30)",
    )
    bench_parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.json",
        help="Destination JSON report path",
    )

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

    elif args.command == "swarm":
        from q_ai_governance.q_ai_agent_swarm import QAIAgentSwarm
        swarm = QAIAgentSwarm()
        res = swarm.evaluate_swarm_consensus(task_name=args.task, num_agents=args.agents)
        print(f"🤖 Enterprise Multi-Agent AI Swarm Consensus [{args.task}]")
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
        bench_results = governor.run_uniswap_benchmark()
        governor.generate_uniswap_forum_proposal(results=bench_results, output_md=args.output)

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
        print("📡 Connecting to Snapshot GraphQL API...")
        print("⚠️ Results are exploratory heuristic estimates, not validated vote forecasts.")
        oracle = SnapshotLiveOracle()
        summary = oracle.predict_live_proposals()
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Live Snapshot estimates saved to {args.output}")

    elif args.command == "allocate":
        print(f"⚡ Running Q-AI DAO Budget Allocator for ${args.budget:,.2f} Treasury...")
        allocator = DAOBudgetAllocator(total_budget=args.budget)
        props = sample_proposals()
        report = allocator.allocate_budget(props)
        allocator.generate_report_file(report, output_json=args.output)
        print(f"✅ Budget allocation complete. Total Allocated: ${report['total_allocated']:,.2f} ({report['consensus_score']:.1f}% Consensus)")

    elif args.command == "predict":
        if args.shots < 1:
            parser.error("predict --shots must be at least 1")
        print("⚠️ This is an exploratory statevector simulation, not a validated vote forecast.")
        obs = np.array([args.public_good, args.roi], dtype=np.float32)
        agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)
        
        yes_count = 0
        for _ in range(args.shots):
            idx, _, _, _, _ = agent.deliberate_and_act(obs)
            if idx % 2 == 0:
                yes_count += 1
                
        pred_pct = (yes_count / args.shots) * 100.0
        print(f"\n==================================================")
        print(f"  EXPLORATORY STATEVECTOR SIMULATION               ")
        print(f"==================================================")
        print(f"Manual public-good input: {args.public_good}/10.0")
        print(f"Manual ROI input: {args.roi}/10.0")
        print(f"Measured toy-model YES share: {pred_pct:.1f}%\n")

    elif args.command == "experiments":
        from q_ai_governance.experiment_lab import list_experiments, run_experiment

        if args.list or not args.run:
            for experiment in list_experiments():
                print(f"{experiment['experiment_id']}: {experiment['title']}")
                print(f"  {experiment['kind']} | {experiment['status']}")
                print(f"  Hypothesis: {experiment['hypothesis']}")
                print(f"  Baseline: {experiment['baseline']}\n")
        else:
            if args.run == "snapshot-temporal-baseline" and not args.data:
                parser.error("experiments --run snapshot-temporal-baseline requires --data")
            try:
                if args.run == "snapshot-temporal-baseline":
                    report = run_experiment(args.run, data_path=args.data, test_frac=args.test_frac)
                else:
                    report = run_experiment(args.run)
            except ValueError as exc:
                parser.error(str(exc))
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, "w") as fh:
                json.dump(report, fh, indent=2)
            print(f"Experiment report written to {args.output}")

    elif args.command == "ewl-tournament":
        from q_ai_governance.ewl_tournament import run_tournament

        try:
            report = run_tournament(
                player_1=args.p1,
                player_2=args.p2,
                entanglement=args.entanglement,
                rounds=args.rounds,
                seed=args.seed,
            )
        except ValueError as exc:
            parser.error(str(exc))

        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as fh:
            json.dump(report, fh, indent=2)
        checks = report["control_checks"]
        print("EWL mechanism-blind tournament report written to " + args.output)
        print("Matched EWL/classical-control probabilities: " + str(checks["matched_probability_distribution"]))
        print("Matched EWL/classical-control replay sequence: " + str(checks["matched_sampled_event_sequence"]))
        print("Hardware adapter status: not executed (no QPU claim).")

    elif args.command == "fetch-snapshot-data":
        from q_ai_governance.fetch_snapshot_dataset import build, SPACES

        print("Fetching closed proposals from the Snapshot hub...")
        proposals, dropped, seen = build()
        payload = {
            "source": "https://hub.snapshot.org/graphql",
            "spaces": SPACES,
            "closed_proposals_seen": seen,
            "proposals_kept": len(proposals),
            "dropped": dropped,
            "proposals": proposals,
        }
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved {len(proposals)} cleanly-binary proposals to {args.output}")

    elif args.command == "benchmark":
        from q_ai_governance.benchmark_snapshot_real import run

        summary = run(args.data, test_frac=args.test_frac)
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as fh:
            json.dump(summary, fh, indent=2)

        split = summary["split"]
        print("=" * 66)
        print("  SNAPSHOT BENCHMARK — temporal split, no hindsight")
        print("=" * 66)
        print(f"n = {split['n_total']}  (train {split['n_train']} / test {split['n_test']})")
        print(f"{'model':<28}{'MAE (pp)':>10}{'RMSE (pp)':>11}{'R^2':>9}")
        print("-" * 66)
        for name, result in summary["results"].items():
            print(f"{name:<28}{result['mae_pp']:>10.2f}{result['rmse_pp']:>11.2f}{result['r2']:>9.3f}")
        print(f"\nWritten to {args.output}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
