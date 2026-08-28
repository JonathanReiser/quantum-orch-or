"""
ibm_quantum_backend.py — IBM Quantum Hardware Execution Connector

Connects QuantumOrchORAgent circuits to real 127-qubit IBM Quantum hardware QPUs
(ibm_brisbane, ibm_kyiv, ibm_osaka) via Qiskit Runtime API with seamless AerSimulator fallback.
"""

import os
import json
import argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class IBMQuantumBackendConnector:
    def __init__(self, api_token=None, backend_name="ibm_brisbane"):
        self.api_token = api_token or os.getenv("IBM_QUANTUM_TOKEN")
        self.backend_name = backend_name
        self.simulator = AerSimulator()
        self.using_real_hardware = False

        if self.api_token:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
                self.service = QiskitRuntimeService(channel="ibm_quantum", token=self.api_token)
                self.hardware_backend = self.service.backend(self.backend_name)
                self.using_real_hardware = True
                print(f"✅ Connected to Real IBM Quantum Hardware QPU: {self.backend_name}")
            except Exception as e:
                print(f"⚠️ IBM Quantum API Connection Warning: {e}. Falling back to AerSimulator.")
                self.hardware_backend = self.simulator
        else:
            self.hardware_backend = self.simulator

    def execute_quantum_deliberation(self, theta, phi, shots=1024):
        """
        Executes a 2-qubit quantum deliberation circuit on IBM Quantum hardware or simulator.
        """
        qc = QuantumCircuit(2, 2)
        qc.ry(theta, 0)
        qc.rx(phi, 1)
        qc.cz(0, 1)
        qc.measure([0, 1], [0, 1])

        if self.using_real_hardware:
            compiled_qc = transpile(qc, self.hardware_backend)
            job = self.hardware_backend.run(compiled_qc, shots=shots)
            result = job.result()
            counts = result.get_counts()
        else:
            compiled_qc = transpile(qc, self.simulator)
            result = self.simulator.run(compiled_qc, shots=shots).result()
            counts = result.get_counts()

        # Calculate state probabilities
        total_shots = sum(counts.values())
        prob_00 = counts.get("00", 0) / total_shots
        prob_01 = counts.get("01", 0) / total_shots
        prob_10 = counts.get("10", 0) / total_shots
        prob_11 = counts.get("11", 0) / total_shots

        return {
            "backend_used": self.backend_name if self.using_real_hardware else "AerSimulator (Local)",
            "using_real_hardware": self.using_real_hardware,
            "shots": shots,
            "counts": counts,
            "state_probabilities": {
                "00": round(prob_00, 4),
                "01": round(prob_01, 4),
                "10": round(prob_10, 4),
                "11": round(prob_11, 4)
            }
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test IBM Quantum Hardware Backend Connector")
    parser.add_argument("--token", type=str, help="IBM Quantum API Token")
    parser.add_argument("--backend", type=str, default="ibm_brisbane", help="IBM QPU Backend Name")
    args = parser.parse_args()

    connector = IBMQuantumBackendConnector(api_token=args.token, backend_name=args.backend)
    res = connector.execute_quantum_deliberation(theta=0.785, phi=1.047, shots=1024)

    print("\n==================================================")
    print("  IBM QUANTUM HARDWARE EXECUTION RESULTS         ")
    print("==================================================")
    print(f"Backend Used:         {res['backend_used']}")
    print(f"Real Hardware Active: {res['using_real_hardware']}")
    print(f"Shots Executed:       {res['shots']}")
    print(f"State Counts:         {res['counts']}")
    print(f"State Probabilities:  {json.dumps(res['state_probabilities'], indent=2)}\n")
