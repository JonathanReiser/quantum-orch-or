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
    from q_ai_governance.q_ai_bot import QAIGovernanceBot
except ImportError:
    from quantum_agent import QuantumOrchORAgent
    from dao_budget_allocator import DAOBudgetAllocator, sample_proposals
    from benchmark_real_dao_data import RealDAOBenchmarkRunner
    from snapshot_live_oracle import SnapshotLiveOracle
    from quantum_economics import run_quantum_econ_benchmark
    from q_ai_bot import QAIGovernanceBot

def main():
    parser = argparse.ArgumentParser(
        prog="q-ai-gov",
        description="Q-AI Governance: Quantum-Cognitive AI Policy & DAO Decision Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

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

    if args.command == "bot":
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
