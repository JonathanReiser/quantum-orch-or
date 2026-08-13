#!/usr/bin/env python3
import argparse
import os
import sys
from quantum_orch_or.simulation import QuantumOrchORSimulation
from quantum_orch_or.visualize import plot_simulation_results

def main():
    parser = argparse.ArgumentParser(description="Quantum Orch-OR Simulation on Qiskit")
    parser.add_argument("--qubits", type=int, default=4, help="Number of qubits (tubulins) in the chain")
    parser.add_argument("--coupling", type=float, default=1.0e-3, help="Dipole-dipole coupling constant J")
    parser.add_argument("--tunneling", type=float, default=5.0e-4, help="Quantum tunneling rate g")
    parser.add_argument("--dt", type=float, default=1.0e-3, help="Time step size in seconds")
    parser.add_argument("--steps", type=int, default=150, help="Total simulation steps")
    parser.add_argument("--state", type=str, default="superposition", 
                        choices=["ground", "excited", "superposition", "ghz"],
                        help="Initial state of the tubulin qubits")
    parser.add_argument("--output", type=str, default="simulation_results.png", 
                        help="Path to save the output visualization plot")
    parser.add_argument("--hw-circuit", action="store_true", 
                        help="Generate the Qiskit hardware-compatible circuit description file instead of running simulation")
    parser.add_argument("--scale-eg", type=float, default=1.0, 
                        help="Scaling factor for E_G (e.g. 1e16 to force collapse events in toy models)")

    args = parser.parse_args()

    # If active virtual env is not running this script, notify
    if not os.environ.get('VIRTUAL_ENV'):
        print("Warning: You are not running inside the virtual environment 'venv'. Results may fail.")

    sim = QuantumOrchORSimulation(
        num_qubits=args.qubits,
        J_coupling=args.coupling,
        g_tunneling=args.tunneling,
        dt=args.dt,
        total_steps=args.steps,
        initial_state=args.state,
        eg_scaling=args.scale_eg
    )

    if args.hw_circuit:
        print("Generating Qiskit circuit with mid-circuit collapse gates...")
        qc = sim.generate_qiskit_hardware_circuit()
        print("\n=== GENERATED QISKIT CIRCUIT ===")
        print(qc.draw(output='text'))
        print("================================")
        print("Circuit is ready to run on real hardware.")
        return

    # Run statevector simulation
    results = sim.run_statevector_simulation()
    
    # Save the output plot
    plot_simulation_results(results, args.qubits, save_path=args.output)
    print(f"Simulation completed successfully! Output plot saved to: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
