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

### 2. Running the Orch-OR Simulation

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

### Running on Real Quantum Hardware (IBM QPU)

You can run the game theory circuit directly on a physical quantum computer on the IBM Quantum cloud by providing the `--ibmq` flag and your API token:

```bash
python3 quantum_game.py --ibmq --token YOUR_IBM_QUANTUM_TOKEN --p1 Q --p2 Q
```

* `--p1`: Player 1 Strategy (`C`, `D`, or `Q`)
* `--p2`: Player 2 Strategy (`C`, `D`, or `Q`)
* `--token`: Your IBM Quantum API Token (from quantum.ibm.com). Optional if already configured locally.


### Payoff Matrix & Simulation Results

The simulation runs six scenario combinations and outputs the following expected payoffs:

| Scenario | Player 1 Strategy | Player 2 Strategy | Expected Payoff (P1, P2) | State Resolution |
| :--- | :---: | :---: | :---: | :---: |
| **Classical Cooperation** | Cooperate ($C$) | Cooperate ($C$) | (3.00, 3.00) | 100% $|CC\rangle$ |
| **Classical Defection** | Defect ($D$) | Defect ($D$) | **(1.00, 1.00)** | 100% $|DD\rangle$ (Old Nash Eq.) |
| **Classical Exploitation** | Defect ($D$) | Cooperate ($C$) | (5.00, 0.00) | 100% $|DC\rangle$ |
| **Quantum Exploiting Defector**| Quantum ($Q$) | Defect ($D$) | (5.00, 0.00) | 100% $|DC\rangle$ |
| **Quantum Mutual Cooperation** | Quantum ($Q$) | Quantum ($Q$) | **(3.00, 3.00)** | 100% $|CC\rangle$ (New Nash Eq.) |

**In the quantum game, if Player 2 attempts to cheat by playing $D$ while you play $Q$, the entanglement causes Player 2's payoff to drop to **0**, while you get **5**. Since defection is heavily penalized by the quantum strategy, **$(Q, Q)$ becomes the only stable Nash Equilibrium**, allowing self-interested players to achieve mutual cooperation.

### 🧠 Understanding the Web App Cognitive Agent

If you run the interactive web application, the **Cognitive Agent (Orch-OR)** tab visualizes the Penrose-Hameroff model of decision-making with three interactive panels:

1. **Cognitive State Vector Space (2D Circle Canvas):**
   * Represents the agent's mind-state as a vector: $|\psi\rangle = \cos(\theta)|Ethics\rangle + \sin(\theta)|Profit\rangle$.
   * **Vector Angle:** Points straight up ($90^\circ$) for pure Ethics, and straight right ($0^\circ$) for pure Profit. A $45^\circ$ angle represents an undecided, balanced superposition.
   * **Rotations:** Clicking "Preserve Ethics" or "Maximize Profit" applies rotation matrices that swing the vector on the canvas, demonstrating how arguments tilt the agent's beliefs.
2. **The Deliberation Loop & Drift:**
   * Clicking **"Toggle Deliberation"** starts active contemplation. The vector drifts slightly representing natural thought wandering.
   * **Entropy Integration:** The app integrates the Shannon entropy of the state over time to calculate the accumulated cognitive action. The closer the vector is to a balanced superposition, the higher the entropy and the faster the action meter rises.
   * **Spontaneous Collapse:** The moment the action line crosses the threshold, a spontaneous collapse is triggered. The screen flashes, the vector collapses onto either the $|Ethics\rangle$ or $|Profit\rangle$ axis, and the decision is resolved.

### 🎮 Understanding the Web App Game Simulator

If you run the interactive web application, the **Quantum Game Theory** tab visualizes the EWL model with three interactive panels:

1. **The Payoff Grid (2x2 Matrix):**
   * **Rows (P1)** and **Columns (P2)** represent the choices to Cooperate ($C$) or Defect ($D$).
   * Each cell displays the score: `(Player 1, Player 2)`.
     * **CC (3, 3):** Mutual cooperation (good outcome).
     * **DD (1, 1):** Mutual defection (classical trap).
     * **DC (5, 0) / CD (0, 5):** One player defects and exploits the other.
   * **Probability Badges & Glow Highlights:** Shows how likely the system is to resolve into each outcome. The grid dynamically highlights the active outcomes in glowing cyan.
2. **The Entanglement Slider ($\gamma$):**
   * Adjusts the quantum coupling between the players. 
   * **At 0% (Classical):** You are playing the standard, unentangled Prisoner's Dilemma. Playing $(D, D)$ always results in $100\%$ probability of DD.
   * **At 100% (Quantum):** Qubits are maximally entangled. Playing $(Q, Q)$ rotates the states back to $100\%$ probability of CC.
   * **At 50% (Superposition):** You will see multiple cells light up (e.g. $50\%$ CC and $50\%$ DD), representing a quantum superposition of different game outcomes before the measurement resolves it.
3. **The Outcome Distribution Chart:**
   * A bar chart showing the probability of resolving onto the eigenstates: $|CC\rangle$, $|DC\rangle$, $|CD\rangle$, and $|DD\rangle$. 
   * In Qiskit qubit ordering, index 1 ($|01\rangle$) represents Player 1 playing $D$ and Player 2 playing $C$ (DC), while index 2 ($|10\rangle$) represents CD.
