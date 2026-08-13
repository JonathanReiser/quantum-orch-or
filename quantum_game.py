#!/usr/bin/env python3
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit_aer import AerSimulator

# Payoff constants
PAYOFF_CC = (3, 3)
PAYOFF_CD = (0, 5) # Player 1 gets 0, Player 2 gets 5
PAYOFF_DC = (5, 0) # Player 1 gets 5, Player 2 gets 0
PAYOFF_DD = (1, 1)

# EWL Entangling Operator J
# J = 1/sqrt(2) * (I⊗I + i * X⊗X)
I_2d = np.eye(2)
X_2d = np.array([[0, 1], [1, 0]])
I_4d = np.eye(4)
X_4d = np.kron(X_2d, X_2d)
J_matrix = (1 / np.sqrt(2)) * (I_4d + 1j * X_4d)
J_gate = Operator(J_matrix)
J_dagger_gate = Operator(J_matrix.conj().T)

# Strategy Unitary Matrices
U_C = np.eye(2) # Cooperate (Identity)
U_D = X_2d      # Defect (Bit-flip X)
U_Q = np.array([[1j, 0], [0, -1j]]) # Quantum strategy Q

def simulate_game(strategy1, strategy2):
    """
    Simulates the EWL Quantum Prisoner's Dilemma game for given Player 1 and Player 2 strategies.
    Returns the expected payoffs (Payoff1, Payoff2) and final state probabilities.
    """
    qc = QuantumCircuit(2)
    
    # 1. Apply Entangling Operator J
    qc.append(J_gate, [0, 1])
    
    # 2. Apply Strategies
    qc.append(Operator(strategy1), [0])
    qc.append(Operator(strategy2), [1])
    
    # 3. Apply De-entangling Operator J†
    qc.append(J_dagger_gate, [0, 1])
    
    # 4. Save statevector to get exact probabilities
    qc.save_statevector()
    
    # Run simulation
    simulator = AerSimulator()
    t_qc = transpile(qc, simulator)
    result = simulator.run(t_qc).result()
    statevector = np.array(result.get_statevector(t_qc))
    
    # Calculate probabilities of the basis states: |00> (CC), |01> (CD), |10> (DC), |11> (DD)
    # Note: Qiskit ordering is q1 q0, so state index 1 is |01> (Player 1 defect, Player 2 cooperate)
    probs = np.abs(statevector) ** 2
    
    p_CC = probs[0] # |00>
    p_DC = probs[1] # |01> (Player 1 defect, Player 2 cooperate)
    p_CD = probs[2] # |10> (Player 1 cooperate, Player 2 defect)
    p_DD = probs[3] # |11>
    
    # Calculate expected payoffs
    payoff1 = 3 * p_CC + 0 * p_CD + 5 * p_DC + 1 * p_DD
    payoff2 = 3 * p_CC + 5 * p_CD + 0 * p_DC + 1 * p_DD
    
    return (payoff1, payoff2), (p_CC, p_CD, p_DC, p_DD)

def main():
    scenarios = {
        "Classical Mutual Cooperation (C vs C)": (U_C, U_C),
        "Classical Mutual Defection (D vs D)": (U_D, U_D),
        "Classical Unilateral Defection (D vs C)": (U_D, U_C),
        "Quantum vs Classical Defection (Q vs D)": (U_Q, U_D),
        "Classical Defection vs Quantum (D vs Q)": (U_D, U_Q),
        "Quantum Mutual Cooperation (Q vs Q)": (U_Q, U_Q)
    }
    
    print("==================================================")
    print("      EWL QUANTUM PRISONER'S DILEMMA RUN          ")
    print("==================================================")
    
    for name, (strat1, strat2) in scenarios.items():
        (pay1, pay2), probs = simulate_game(strat1, strat2)
        print(f"\nScenario: {name}")
        print(f"  Payoffs: Player 1 = {pay1:.2f}, Player 2 = {pay2:.2f}")
        print(f"  Probabilities: CC={probs[0]:.2f}, CD={probs[1]:.2f}, DC={probs[2]:.2f}, DD={probs[3]:.2f}")
    
    print("\n==================================================")

if __name__ == "__main__":
    main()
