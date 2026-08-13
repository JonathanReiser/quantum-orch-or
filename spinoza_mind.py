#!/usr/bin/env python3
import argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def run_local_simulation(theta):
    """
    Simulates the Spinozist dual-mind circuit locally using AerSimulator.
    """
    qc = QuantumCircuit(2)
    
    # 1. Entangle Mind A (qubit 0) and Mind B (qubit 1) into a Bell State.
    # This represents the two minds sharing a single underlying Spinozist substance.
    qc.h(0)
    qc.cx(0, 1)
    
    # 2. Apply a deliberation rotation on Mind A (qubit 0) only.
    # We rotate the statevector representing arguments shifting the belief.
    qc.ry(theta, 0)
    
    # 3. Spontaneous resolution (measurement)
    qc.measure_all()
    
    simulator = AerSimulator()
    t_qc = transpile(qc, simulator)
    result = simulator.run(t_qc, shots=1024).result()
    return result.get_counts()

def run_on_ibm(theta, token=None):
    """
    Submits the Spinozist dual-mind circuit to a real physical IBM Quantum computer.
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
    
    # Build circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(theta, 0)
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
        return counts, backend.name

def main():
    parser = argparse.ArgumentParser(description="Spinoza's Entangled Intellect Qiskit Simulator")
    parser.add_argument("--theta", type=float, default=np.pi/4, help="Deliberation rotation angle in radians (default: pi/4)")
    parser.add_argument("--ibmq", action="store_true", help="Run the circuit on a real physical IBM Quantum computer")
    parser.add_argument("--token", type=str, help="IBM Quantum API Token")
    
    args = parser.parse_args()
    
    print("==================================================")
    print("     SPINOZA'S ENTANGLED INTELLECT SIMULATOR      ")
    print("==================================================")
    print(f"Metaphysical Premise: Mind A and Mind B are modes of a")
    print(f"single substance. Deliberating on Mind A will physically")
    print(f"rotate and collapse the decision state of Mind B.")
    print(f"Deliberation Angle (theta) = {args.theta:.4f} radians ({np.degrees(args.theta):.1f}°)")
    print("==================================================")
    
    if args.ibmq:
        res = run_on_ibm(args.theta, args.token)
        if res:
            counts, qpu_name = res
            print("\n=== EXECUTION RESULTS ===")
            print(f"QPU Backend: {qpu_name}")
        else:
            return
    else:
        print("Running local Aer simulator run...")
        counts = run_local_simulation(args.theta)
        print("\n=== SIMULATION RESULTS ===")
        print("Backend: AerSimulator")
        
    total_shots = sum(counts.values())
    
    # Qiskit maps qubit 0 to rightmost bit, qubit 1 to leftmost bit
    # counts keys are 'q1q0' -> 'MindB MindA'
    p_00 = counts.get('00', 0) / total_shots # Both Ethics
    p_01 = counts.get('01', 0) / total_shots # Mind A Profit, Mind B Ethics
    p_10 = counts.get('10', 0) / total_shots # Mind A Ethics, Mind B Profit
    p_11 = counts.get('11', 0) / total_shots # Both Profit
    
    agreement = p_00 + p_11
    disagreement = p_01 + p_10
    
    print(f"Total Shots: {total_shots}")
    print(f"  P(Both Choose Ethics |00>): {p_00*100:.1f}%")
    print(f"  P(Both Choose Profit |11>): {p_11*100:.1f}%")
    print(f"  P(Mind A Profit, Mind B Ethics |01>): {p_01*100:.1f}%")
    print(f"  P(Mind A Ethics, Mind B Profit |10>): {p_10*100:.1f}%")
    print("--------------------------------------------------")
    print(f"Unified Decision Agreement (00 or 11): {agreement*100:.1f}%")
    print(f"Cognitive Disagreement (01 or 10): {disagreement*100:.1f}%")
    print("==================================================")
    
    print("\nSpinozist Interpretation:")
    print("Observe that even though Mind B received NO direct rotation,")
    print(f"its final state was rotated by Mind A's deliberation.")
    if agreement > 0.7:
        print("Because they share a unified substance (entanglement), their")
        print("decisions remain highly correlated and unified in harmony.")
    else:
        print("With a larger deliberation angle, the two modes split into")
        print("higher cognitive disagreement, yet they remain locked in correlation.")
    print("==================================================")

if __name__ == "__main__":
    main()
