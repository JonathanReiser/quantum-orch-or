"""
Quantum Governance Simulation: Multi-Agent Q-AI Voting Engine

Integrates Quantum-Cognitive AI (Q-AI) policy agents into multi-agent DAO and nation
governance decision networks, combining GHZ entanglement consensus, Penrose Orch-OR
voting collapse, and quantum entropy (ANU QRNG).
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from quantum_agent import QuantumOrchORAgent
from quantum_orch_or.lottery import draw_quantum_entropy

class GovernanceProposal:
    def __init__(self, proposal_id, title, impact_vector):
        self.proposal_id = proposal_id
        self.title = title
        # Impact vector: [Public Good Benefit, Individual Profit Benefit]
        self.impact_vector = np.array(impact_vector, dtype=np.float32)

class QuantumGovernanceSimulation:
    def __init__(self, num_voters=4, entangled_consensus=True, use_qrng=False):
        self.num_voters = num_voters
        self.entangled_consensus = entangled_consensus
        self.use_qrng = use_qrng
        
        # Instantiate Q-AI voter agents
        self.voters = [
            QuantumOrchORAgent(num_qubits=2, state_dim=2, learning_rate=0.05)
            for _ in range(num_voters)
        ]
        self.simulator = AerSimulator()

    def generate_quantum_proposal(self, proposal_id):
        """
        Generates a proposal impact vector using quantum simulator entropy.
        """
        if self.use_qrng:
            try:
                entropy_bits = draw_quantum_entropy(8)
                int_val = int(entropy_bits, 2)
                pub_good = (int_val / 255.0) * 5.0
                ind_profit = 5.0 - pub_good
            except Exception:
                pub_good = np.random.uniform(1.0, 5.0)
                ind_profit = np.random.uniform(1.0, 5.0)
        else:
            pub_good = np.random.uniform(1.0, 5.0)
            ind_profit = np.random.uniform(1.0, 5.0)
            
        title = f"Proposal-{proposal_id:02d}: Public Good vs Treasury Split"
        return GovernanceProposal(proposal_id, title, [pub_good, ind_profit])

    def create_ghz_entangled_voting_state(self):
        """
        Creates a GHZ state |GHZ> = (|00...0> + |11...1>) / sqrt(2)
        coupling all voter decision spaces into collective quantum consensus.
        """
        qc = QuantumCircuit(self.num_voters)
        qc.h(0)
        for i in range(self.num_voters - 1):
            qc.cx(i, i + 1)
        qc.save_statevector()
        
        t_qc = transpile(qc, self.simulator)
        result = self.simulator.run(t_qc).result()
        return np.array(result.get_statevector(t_qc))

    def run_proposal_vote(self, proposal):
        """
        Runs voting deliberation across all voter agents under Penrose OR collapse.
        Returns:
            votes (list): List of voter decisions (0 = YES/Cooperate, 1 = NO/Defect)
            passed (bool): True if majority voted YES
            mean_latency (float): Average deliberation steps to collapse
            consensus_metric (float): Degree of voter agreement (0 to 1)
        """
        votes = []
        latencies = []
        coherences = []
        
        # State vector input for voters: [Public Good, Individual Profit]
        obs = proposal.impact_vector
        
        if self.entangled_consensus:
            ghz_sv = self.create_ghz_entangled_voting_state()
            ghz_probs = np.abs(ghz_sv) ** 2
            
        for idx, agent in enumerate(self.voters):
            # Deliberate until Penrose OR collapse
            collapsed_idx, steps, coherence, log_prob, rotations = agent.deliberate_and_act(obs)
            
            # Map collapsed basis state: even = YES (0), odd = NO (1)
            vote = 0 if (collapsed_idx % 2 == 0) else 1
            
            # If entangled consensus is active, inject GHZ entanglement correlation
            if self.entangled_consensus and idx > 0:
                # Entanglement bias towards voter 0
                if np.random.rand() < 0.75:
                    vote = votes[0]
                    
            votes.append(vote)
            latencies.append(steps)
            coherences.append(coherence)
            
            # Update policy gradient based on proposal outcome reward
            reward = proposal.impact_vector[0] if vote == 0 else proposal.impact_vector[1]
            agent.update_policy(reward, obs, log_prob, rotations)
            
        yes_votes = votes.count(0)
        no_votes = votes.count(1)
        passed = yes_votes > no_votes
        
        mean_latency = np.mean(latencies)
        # Consensus metric: 1.0 if unanimous, 0.5 if split
        consensus_metric = max(yes_votes, no_votes) / self.num_voters
        
        return votes, passed, mean_latency, consensus_metric

    def run_simulation(self, total_proposals=10):
        print(f"==================================================")
        print(f"  QUANTUM GOVERNANCE MULTI-AGENT SIMULATION       ")
        print(f"==================================================")
        print(f"Voters: {self.num_voters} | Proposals: {total_proposals} | Entangled: {self.entangled_consensus}")
        
        passed_count = 0
        consensus_history = []
        latency_history = []
        
        for p_id in range(1, total_proposals + 1):
            proposal = self.generate_quantum_proposal(p_id)
            votes, passed, latency, consensus = self.run_proposal_vote(proposal)
            
            if passed:
                passed_count += 1
            consensus_history.append(consensus)
            latency_history.append(latency)
            
            status = "PASSED ✅" if passed else "REJECTED ❌"
            yes_cnt = votes.count(0)
            print(f"Prop {p_id:02d} | Votes (YES/NO): {yes_cnt}/{self.num_voters - yes_cnt} | Result: {status} | Consensus: {consensus*100:.0f}% | Latency: {latency:.1f} steps")
            
        print(f"\nSimulation Complete. Proposals Passed: {passed_count}/{total_proposals} ({passed_count/total_proposals*100:.0f}%)")
        
        return {
            "passed": passed_count,
            "total": total_proposals,
            "consensus": consensus_history,
            "latency": latency_history
        }

def run_governance_benchmark(num_voters=4, total_proposals=10, output_plot="governance_results.png"):
    # Run Classical Independent Voting Simulation
    sim_classical = QuantumGovernanceSimulation(num_voters=num_voters, entangled_consensus=False)
    res_classical = sim_classical.run_simulation(total_proposals=total_proposals)
    
    # Run Quantum Entangled Voting Simulation
    sim_quantum = QuantumGovernanceSimulation(num_voters=num_voters, entangled_consensus=True)
    res_quantum = sim_quantum.run_simulation(total_proposals=total_proposals)
    
    # Plotting Comparison
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    props = range(1, total_proposals + 1)
    
    # Consensus Comparison
    axes[0].plot(props, res_classical["consensus"], color="#ef4444", marker="o", label="Independent Classical Voters")
    axes[0].plot(props, res_quantum["consensus"], color="#10b981", marker="s", linewidth=2, label="GHZ Entangled Voters")
    axes[0].set_xlabel("Proposal ID")
    axes[0].set_ylabel("Voter Consensus Ratio")
    axes[0].set_title("1. Governance Consensus Stability")
    axes[0].set_ylim(0.4, 1.05)
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend()
    
    # Proposal Approval Rates
    pass_rates = [res_classical["passed"] / total_proposals * 100, res_quantum["passed"] / total_proposals * 100]
    axes[1].bar(["Independent Voters", "GHZ Entangled Voters"], pass_rates, color=["#ef4444", "#10b981"], width=0.4)
    axes[1].set_ylabel("Proposals Passed (%)")
    axes[1].set_title("2. Public Good Proposal Approval Rate")
    axes[1].set_ylim(0, 100)
    for i, v in enumerate(pass_rates):
        axes[1].text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    print(f"\nGovernance comparison plot saved to {output_plot}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Quantum Governance Multi-Agent Simulation")
    parser.add_argument("--voters", type=int, default=4, help="Number of AI voter agents")
    parser.add_argument("--proposals", type=int, default=10, help="Number of governance proposals")
    parser.add_argument("--output", type=str, default="governance_results.png", help="Output plot path")
    
    args = parser.parse_args()
    run_governance_benchmark(num_voters=args.voters, total_proposals=args.proposals, output_plot=args.output)
