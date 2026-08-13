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

def run_on_ibm(strategy1, strategy2, token=None):
    """
    Submits the quantum game circuit to a real physical IBM Quantum computer.
    """
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2
    except ImportError:
        print("Error: 'qiskit-ibm-runtime' package is not installed.")
        print("Please run: pip install qiskit-ibm-runtime")
        return None
        
    print("Connecting to IBM Quantum Service...")
    try:
        if token:
            service = QiskitRuntimeService(channel="ibm_quantum", token=token)
        else:
            service = QiskitRuntimeService()
    except Exception as e:
        print(f"Failed to authenticate with IBM Quantum: {e}")
        print("Make sure you provide a valid token using --token <YOUR_TOKEN>.")
        return None

    print("Finding the least busy physical backend...")
    backend = service.least_busy(simulator=False, operational=True)
    print(f"Selected physical system: {backend.name}")
    
    # Build circuit with measurements
    qc = QuantumCircuit(2)
    qc.append(J_gate, [0, 1])
    qc.append(Operator(strategy1), [0])
    qc.append(Operator(strategy2), [1])
    qc.append(J_dagger_gate, [0, 1])
    qc.measure_all()
    
    print("Transpiling circuit for backend layout...")
    t_qc = transpile(qc, backend)
    
    print("Submitting job to QPU...")
    with Session(service=service, backend=backend) as session:
        sampler = SamplerV2(session=session)
        job = sampler.run([t_qc])
        print(f"Job submitted! Job ID: {job.job_id()}")
        print("Waiting for results (this may take a while depending on queue)...")
        
        result = job.result()
        pub_result = result[0]
        counts = pub_result.data.meas.get_counts()
        
        total_shots = sum(counts.values())
        p_CC = counts.get('00', 0) / total_shots
        p_DC = counts.get('01', 0) / total_shots
        p_CD = counts.get('10', 0) / total_shots
        p_DD = counts.get('11', 0) / total_shots
        
        payoff1 = 3 * p_CC + 0 * p_CD + 5 * p_DC + 1 * p_DD
        payoff2 = 3 * p_CC + 5 * p_CD + 0 * p_DC + 1 * p_DD
        
        return (payoff1, payoff2), (p_CC, p_CD, p_DC, p_DD), backend.name

def main():
    import argparse
    parser = argparse.ArgumentParser(description="EWL Quantum Prisoner's Dilemma Simulator")
    parser.add_argument("--ibmq", action="store_true", help="Run the game on a real IBM Quantum computer")
    parser.add_argument("--token", type=str, help="IBM Quantum API Token")
    parser.add_argument("--p1", type=str, default="Q", choices=["C", "D", "Q"], help="Player 1 Strategy")
    parser.add_argument("--p2", type=str, default="Q", choices=["C", "D", "Q"], help="Player 2 Strategy")
    
    args = parser.parse_args()
    
    strategy_map = {"C": U_C, "D": U_D, "Q": U_Q}
    
    if args.ibmq:
        print("==================================================")
        print("      RUNNING GAME ON PHYSICAL IBM QPU            ")
        print("==================================================")
        print(f"Strategy: Player 1 = {args.p1}, Player 2 = {args.p2}")
        
        res = run_on_ibm(strategy_map[args.p1], strategy_map[args.p2], args.token)
        if res:
            (pay1, pay2), probs, qpu_name = res
            print("\n=== EXECUTION RESULTS ===")
            print(f"QPU Backend: {qpu_name}")
            print(f"Payoffs: Player 1 = {pay1:.2f}, Player 2 = {pay2:.2f}")
            print(f"Probabilities: CC={probs[0]:.2f}, CD={probs[1]:.2f}, DC={probs[2]:.2f}, DD={probs[3]:.2f}")
        print("==================================================")
        return

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
