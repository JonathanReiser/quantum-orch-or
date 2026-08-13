# Quantum Orch-OR Simulation on Qiskit

This repository contains a Python package that models Sir Roger Penrose and Dr. Stuart Hameroff’s **Orchestrated Objective Reduction (Orch-OR)** hypothesis of consciousness using **Qiskit** quantum computing frameworks.

The simulation maps physical properties of microtubules to qubits and models how quantum coherence and electrostatic interactions evolve until they trigger spontaneous gravitational wave-function collapses.

---

## 🌌 Core Concepts of Orch-OR

* **Microtubule Qubits:** The brain's microtubules are composed of tubulin protein dimers. Orch-OR posits that these dimers act as qubits, existing in superpositions of conformational states $|0\rangle$ (Alpha conformation) and $|1\rangle$ (Beta conformation).
* **Quantum Evolution:** Dimers interact with neighboring tubulins through electrostatic dipole-dipole interactions, which are modeled here using a transverse-field Ising Hamiltonian.
* **Objective Reduction (OR):** According to Penrose, superpositions represent a split in spacetime geometry. When the difference in gravitational self-energy ($E_G$) of this split reaches a threshold, the state spontaneously collapses (reduces) to a classical basis state:
  $$\int_{0}^{t} E_G(t') dt' \ge \hbar$$
* **Orchestration:** The surrounding classical neuronal state structures and shields this quantum coherence, preventing early environmental decoherence.

---

## 🛠️ How the Code Works

1. **Physical Calculations (`physics.py`):** Calculates the gravitational self-energy $E_G$ of superposed tubulins using Penrose's spherical mass displacement approximation. It also computes a spatial correlation coherence weight $W_c$ from the density matrix/statevector to scale the collective gravity of entangled states:
   $$E_G = E_{G,1} \cdot W_c$$
2. **Quantum Circuits (`circuit.py`):** Builds Trotterized quantum circuits to approximate the time-evolution operator $U(t) = e^{-iHt}$ under the Hamiltonian:
   $$H = -J \sum \sigma_z^{(i)} \sigma_z^{(i+1)} - g \sum \sigma_x^{(i)}$$
3. **Simulation Loop (`simulation.py`):** Evolves the quantum statevector step-by-step. It tracks the accumulated action and, upon reaching $\hbar$, collapses the statevector to a classical basis state (simulating OR) and resets the action to zero.
4. **Visualization (`visualize.py`):** Plts the tubulin conformation probabilities, the spatial coherence, and the accumulated action over time, highlighting the exact moment of Objective Reduction.

---

## 🚀 Getting Started

### 1. Installation

Set up a virtual environment and install Qiskit and the other dependencies:

```bash
# Initialize and activate the virtual environment
bash setup_env.sh
source venv/bin/activate
```

### 2. Running the Simulation

Run the CLI tool to execute a simulation. We apply a scaling factor to $E_G$ (e.g. `--scale-eg 1e17`) to make the collapse visible with a small toy system of 4 qubits:

```bash
python3 main.py --qubits 4 --steps 200 --scale-eg 1e17 --output simulation_results.png
```

### 3. Running on Real Quantum Hardware

To print the transpiled Qiskit circuit containing mid-circuit measurements and resets (which is fully compatible with IBM's real Quantum Processing Units (QPUs)):

```bash
python3 main.py --qubits 4 --hw-circuit
```

To run on actual hardware, you can authenticate Qiskit with your IBM Quantum API Token and swap the backend:
```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_IBM_QUANTUM_TOKEN")
backend = service.least_busy(simulator=False, operational=True)
```

---

## 📊 Output Visualization Explained

![Orch-OR Simulation Plot](simulation_results.png)

The simulation output plot displays three sections:
1. **Tubulin Dimers Conformation Evolution:** Tracks $P(|1\rangle)$ for each tubulin dimer. Oscillates smoothly until the vertical red line (the OR event), where it collapses to a discrete binary state (e.g., $|0110\rangle$).
2. **Quantum Coherence Weight:** Tracks the degree of entanglement. Falls instantly back to base levels when the superposition collapses.
3. **Penrose Threshold Evolution:** Shows the accumulated action rising until it hits the $\hbar$ threshold line, prompting the collapse.

---

## 🎮 Quantum Game Theory: Prisoner's Dilemma

This repository also contains `quantum_game.py`, which implements the **Eisert-Wilkens-Lewenstein (EWL)** model of Quantum Game Theory to resolve the classical Prisoner's Dilemma.

By entangling the decision space of two self-interested players, a new purely quantum strategy $Q$ is introduced that changes the Nash Equilibrium of the game from mutual defection (1,1) to mutual cooperation (3,3).

### How to Run the Game Theory Simulation

To run the EWL simulation and compute the expected payoffs for different classical vs. quantum strategies:

```bash
python3 quantum_game.py
```

### Payoff Matrix & Simulation Results

The simulation runs six scenario combinations and outputs the following expected payoffs:

| Scenario | Player 1 Strategy | Player 2 Strategy | Expected Payoff (P1, P2) | State Resolution |
| :--- | :---: | :---: | :---: | :---: |
| **Classical Cooperation** | Cooperate ($C$) | Cooperate ($C$) | (3.00, 3.00) | 100% $|CC\rangle$ |
| **Classical Defection** | Defect ($D$) | Defect ($D$) | **(1.00, 1.00)** | 100% $|DD\rangle$ (Old Nash Eq.) |
| **Classical Exploitation** | Defect ($D$) | Cooperate ($C$) | (5.00, 0.00) | 100% $|DC\rangle$ |
| **Quantum Exploiting Defector**| Quantum ($Q$) | Defect ($D$) | (5.00, 0.00) | 100% $|DC\rangle$ |
| **Quantum Mutual Cooperation** | Quantum ($Q$) | Quantum ($Q$) | **(3.00, 3.00)** | 100% $|CC\rangle$ (New Nash Eq.) |

**Why this resolves the dilemma:**
In a classical game, if you expect the other player to cooperate, you should defect (getting 5 instead of 3). If you expect them to defect, you should defect (getting 1 instead of 0). Thus, both defect.

In the quantum game, if Player 2 attempts to cheat by playing $D$ while you play $Q$, the entanglement causes Player 2's payoff to drop to **0**, while you get **5**. Since defection is heavily penalized by the quantum strategy, **$(Q, Q)$ becomes the only stable Nash Equilibrium**, allowing self-interested players to achieve mutual cooperation.

