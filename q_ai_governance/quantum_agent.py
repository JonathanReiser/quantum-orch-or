"""
Quantum-Cognitive AI (Q-AI) Reinforcement Learning Agent

This module implements an AI policy agent whose deliberation occurs in Hilbert space
superposition and whose action selection is triggered by spontaneous Penrose
Orchestrated Objective Reduction (Orch-OR) statevector collapse events.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from quantum_orch_or.physics import (
    calculate_single_tubulin_eg,
    calculate_coherence_metric,
    scale_gravitational_energy,
    HBAR
)
from quantum_orch_or.circuit import append_trotter_step

class QuantumPrisonerDilemmaEnv:
    """
    A 2-player Quantum Prisoner's Dilemma environment for testing Q-AI policy agents.
    Actions: 0 = Cooperate, 1 = Defect
    Payoff matrix (Player 1, Opponent):
      (C, C) -> (3, 3)
      (C, D) -> (0, 5)
      (D, C) -> (5, 0)
      (D, D) -> (1, 1)
    """
    def __init__(self, opponent_strategy="tit_for_tat"):
        self.opponent_strategy = opponent_strategy
        self.last_agent_action = 0
        self.last_opponent_action = 0

    def reset(self):
        self.last_agent_action = 0
        self.last_opponent_action = 0
        # State vector: [last_agent_action, last_opponent_action]
        return np.array([self.last_agent_action, self.last_opponent_action], dtype=np.float32)

    def step(self, agent_action):
        # Map agent action (even basis state = Cooperate 0, odd = Defect 1)
        a_act = 0 if (agent_action % 2 == 0) else 1
        
        # Opponent action selection
        if self.opponent_strategy == "random":
            o_act = np.random.choice([0, 1])
        elif self.opponent_strategy == "always_defect":
            o_act = 1
        elif self.opponent_strategy == "always_cooperate":
            o_act = 0
        elif self.opponent_strategy == "tit_for_tat":
            o_act = self.last_agent_action
        else:
            o_act = 0

        # Payoffs
        if a_act == 0 and o_act == 0:
            r_agent, r_opp = 3.0, 3.0
        elif a_act == 0 and o_act == 1:
            r_agent, r_opp = 0.0, 5.0
        elif a_act == 1 and o_act == 0:
            r_agent, r_opp = 5.0, 0.0
        else:
            r_agent, r_opp = 1.0, 1.0

        self.last_agent_action = a_act
        self.last_opponent_action = o_act
        next_state = np.array([a_act, o_act], dtype=np.float32)
        done = True  # Single step game round
        
        return next_state, r_agent, done, {"agent_action": a_act, "opponent_action": o_act}

class QuantumOrchORAgent:
    """
    Hybrid Quantum Policy Agent using parameterized Qiskit quantum circuits
    and Penrose Objective Reduction for non-deterministic action collapse.
    """
    def __init__(self, num_qubits=4, state_dim=2, learning_rate=0.05, hbar_scale=1.0e17, weights_path=None):
        self.num_qubits = num_qubits
        self.state_dim = state_dim
        self.lr = learning_rate
        self.hbar_scale = hbar_scale

        # Policy parameters mapping state input to circuit rotation angles (Rx, Ry) and coupling (J, g)
        # Weights shape: (num_params, state_dim)
        self.num_rotations = num_qubits * 2
        self.weights = np.random.randn(self.num_rotations + 2, state_dim) * 0.1
        self.bias = np.zeros(self.num_rotations + 2)

        # Optionally load weights fit to real data (see train_uniswap_governance_agent.py)
        # instead of the random init above. Default is unchanged random init — this only
        # activates for callers that explicitly ask for fitted weights.
        if weights_path is not None:
            import os
            if os.path.exists(weights_path):
                fitted = np.load(weights_path)
                if fitted["weights"].shape == self.weights.shape and fitted["bias"].shape == self.bias.shape:
                    self.weights = fitted["weights"]
                    self.bias = fitted["bias"]
                else:
                    print(f"⚠️ weights_path={weights_path} shape mismatch for "
                          f"num_qubits={num_qubits}/state_dim={state_dim} — using random init.")
            else:
                print(f"⚠️ weights_path={weights_path} not found — using random init "
                      f"(run train_uniswap_governance_agent.py to produce it).")

        self.single_eg = calculate_single_tubulin_eg() * self.hbar_scale
        self.simulator = AerSimulator()
        # AerSimulator.target rebuilds its full Target object from scratch on every
        # access; deliberate_and_act() calls transpile() many times per rollout, so
        # cache it once here instead of paying that cost on every Trotter step.
        self._target = self.simulator.target
        
    def _compute_circuit_params(self, state_obs):
        # Linear layer output
        linear_out = self.weights @ state_obs + self.bias
        # Rotations between -pi and pi
        rotations = np.pi * np.tanh(linear_out[:self.num_rotations])
        # Coupling J and tunneling g (positive values)
        J_coupling = 1.0e-3 * (1.0 + np.tanh(linear_out[-2]))
        g_tunneling = 5.0e-4 * (1.0 + np.tanh(linear_out[-1]))
        return rotations, J_coupling, g_tunneling

    def _build_initial_circuit(self, rotations):
        qc = QuantumCircuit(self.num_qubits)
        for q in range(self.num_qubits):
            qc.rx(rotations[q], q)
            qc.ry(rotations[q + self.num_qubits], q)
        return qc

    def deliberate_and_act(self, state_obs, dt=0.005, max_steps=200):
        """
        Runs the quantum deliberation loop until Penrose Objective Reduction triggers collapse.
        Returns:
            chosen_basis_state (int): Collapsed basis state index
            deliberation_steps (int): Number of steps taken to reach threshold
            coherence_at_collapse (float): System coherence metric at moment of collapse
            log_prob (float): Proxy log probability for policy gradient update
        """
        rotations, J_coupling, g_tunneling = self._compute_circuit_params(state_obs)
        
        init_qc = self._build_initial_circuit(rotations)
        init_qc.save_statevector()
        
        t_qc = transpile(init_qc, target=self._target, optimization_level=0)
        result = self.simulator.run(t_qc).result()
        current_statevector = np.array(result.get_statevector(t_qc))
        
        accumulated_action = 0.0
        coherence_at_collapse = 1.0
        
        for step in range(1, max_steps + 1):
            coherence_weight, _ = calculate_coherence_metric(current_statevector, self.num_qubits)
            inst_eg = scale_gravitational_energy(self.single_eg, coherence_weight)
            
            step_action = inst_eg * dt
            accumulated_action += step_action
            
            # Check for Penrose Objective Reduction Threshold
            if accumulated_action >= HBAR:
                coherence_at_collapse = coherence_weight
                probs = np.abs(current_statevector) ** 2
                probs /= np.sum(probs) # Normalize
                
                collapsed_idx = np.random.choice(len(current_statevector), p=probs)
                log_prob = np.log(probs[collapsed_idx] + 1e-10)
                
                return collapsed_idx, step, coherence_at_collapse, log_prob, rotations
                
            # Evolve statevector by one Trotter step
            qc_step = QuantumCircuit(self.num_qubits)
            qc_step.initialize(current_statevector, range(self.num_qubits))
            append_trotter_step(qc_step, self.num_qubits, J_coupling, g_tunneling, dt)
            qc_step.save_statevector()
            
            t_qc = transpile(qc_step, target=self._target, optimization_level=0)
            result = self.simulator.run(t_qc).result()
            current_statevector = np.array(result.get_statevector(t_qc))

        # Fallback if threshold is not reached within max_steps
        probs = np.abs(current_statevector) ** 2
        probs /= np.sum(probs)
        collapsed_idx = np.random.choice(len(current_statevector), p=probs)
        log_prob = np.log(probs[collapsed_idx] + 1e-10)
        
        return collapsed_idx, max_steps, coherence_at_collapse, log_prob, rotations

    def update_policy(self, reward, state_obs, log_prob, rotations):
        """
        Updates weights using REINFORCE policy gradient.
        """
        # Feature gradient approximation
        grad_bias = reward * log_prob * np.ones_like(self.bias) * 0.01
        grad_weights = np.outer(grad_bias, state_obs)
        
        self.weights += self.lr * grad_weights
        self.bias += self.lr * grad_bias

def train_agent(episodes=20, num_qubits=4, opponent="tit_for_tat", output_plot="agent_results.png"):
    print(f"==================================================")
    print(f"   TRAINING HYBRID QUANTUM-ORCH-OR POLICY AGENT   ")
    print(f"==================================================")
    print(f"Qubits: {num_qubits} | Episodes: {episodes} | Opponent: {opponent}")
    
    env = QuantumPrisonerDilemmaEnv(opponent_strategy=opponent)
    agent = QuantumOrchORAgent(num_qubits=num_qubits, state_dim=2, learning_rate=0.05)
    
    rewards_history = []
    deliberation_history = []
    coherence_history = []
    cooperation_rates = []
    
    state = env.reset()
    
    for ep in range(1, episodes + 1):
        action, steps, coherence, log_prob, rotations = agent.deliberate_and_act(state)
        next_state, reward, done, info = env.step(action)
        
        agent.update_policy(reward, state, log_prob, rotations)
        state = next_state
        
        rewards_history.append(reward)
        deliberation_history.append(steps)
        coherence_history.append(coherence)
        cooperation_rates.append(1 if info["agent_action"] == 0 else 0)
        
        if ep % 5 == 0 or ep == 1:
            avg_r = np.mean(rewards_history[-5:])
            coop_pct = np.mean(cooperation_rates[-5:]) * 100
            print(f"Episode {ep:02d}/{episodes} | Reward: {reward:.1f} (Avg: {avg_r:.2f}) | "
                  f"Deliberation Steps: {steps:02d} | Coherence: {coherence:.2f} | Cooperation: {coop_pct:.0f}%")
            
    print("Training Complete. Plotting Results...")
    
    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    
    # Episode Rewards
    axes[0].plot(range(1, episodes + 1), rewards_history, color="#8b5cf6", marker="o", label="Episode Payoff")
    if len(rewards_history) >= 5:
        running_avg = np.convolve(rewards_history, np.ones(5)/5, mode='valid')
        axes[0].plot(range(5, episodes + 1), running_avg, color="#06b6d4", linewidth=2, label="5-Ep Moving Avg")
    axes[0].set_ylabel("Payoff Reward")
    axes[0].set_title("Hybrid Quantum AI Agent Training Performance")
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend()
    
    # Deliberation Latency (Steps to Penrose Collapse)
    axes[1].plot(range(1, episodes + 1), deliberation_history, color="#f59e0b", marker="s", label="Deliberation Steps")
    axes[1].axhline(y=np.mean(deliberation_history), color="#ef4444", linestyle=":", label=f"Mean Latency ({np.mean(deliberation_history):.1f} steps)")
    axes[1].set_ylabel("Steps to OR Collapse")
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend()
    
    # Quantum Coherence Weight at Collapse
    axes[2].plot(range(1, episodes + 1), coherence_history, color="#10b981", marker="^", label="Coherence Weight (W_c)")
    axes[2].set_xlabel("Episode")
    axes[2].set_ylabel("Coherence (W_c)")
    axes[2].grid(True, linestyle="--", alpha=0.5)
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    print(f"Results plot saved to {output_plot}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Hybrid Quantum Orch-OR AI Agent")
    parser.add_argument("--episodes", type=int, default=20, help="Number of training episodes")
    parser.add_argument("--qubits", type=int, default=4, help="Number of qubits in agent quantum circuit")
    parser.add_argument("--opponent", type=str, default="tit_for_tat", choices=["tit_for_tat", "random", "always_defect", "always_cooperate"], help="Opponent strategy in Prisoner's Dilemma")
    parser.add_argument("--output", type=str, default="agent_results.png", help="Path to save output plot")
    
    args = parser.parse_args()
    train_agent(episodes=args.episodes, num_qubits=args.qubits, opponent=args.opponent, output_plot=args.output)
