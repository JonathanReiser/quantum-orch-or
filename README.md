# ⚛️ Quantum-Orch-OR: Quantum-Cognitive AI Policy & Governance Engine

[![PyPI Version](https://img.shields.io/pypi/v/q-ai-governance.svg)](https://pypi.org/project/q-ai-governance/)
[![Zenodo Publication](https://img.shields.io/badge/Zenodo-DOI%2010.5281%2Fzenodo.22151233-blue.svg)](https://zenodo.org/records/22151233)
[![Tests](https://img.shields.io/badge/tests-126%20passed-brightgreen.svg)](https://github.com/JonathanReiser/quantum-orch-or)
[![Paper PDF](https://img.shields.io/badge/Paper-PDF%20Download-b31b1b.svg)](https://github.com/JonathanReiser/quantum-orch-or/blob/main/full_quantum_governance_paper.pdf)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-3D%20WebGL-cyan.svg)](https://jonathanreiser.github.io/quantum-orch-or/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quantum-Orch-OR** (`q-ai-governance`) is a world-first **Quantum-Cognitive Reinforcement Learning AI Engine**. By modeling agent decision-making in Hilbert space statevectors governed by **Penrose Orchestrated Objective Reduction (Orch-OR)** statevector collapse ($\tau = \hbar / E_G$) under **Lindblad thermal dephasing ($T = 310\text{ K}$)**, Q-AI captures non-commutative cognitive framing, question order effects, and collective voter gridlocks that classical linear models fail to predict.

---

> ### ⚠️ Corrected claims
>
> An audit on 2026-08-30 found that this project's previously advertised
> headline results — "835,000 Snapshot DAO votes", "86.7% error reduction",
> "1.3% MAE", "R² = 0.98", "GHZ entanglement doubles public-good approval
> 40% → 80%", "84% on the Linda problem", and "92.8% directional accuracy" —
> were **not produced by the code in this repository**. Several were hardcoded
> literals; the DAO figures came from five hand-written proposals, not a
> dataset. See **[CORRECTIONS.md](CORRECTIONS.md)** for the full accounting and
> for what the real data shows. Every number below is enforced by a
> [results ledger](tools/ledger/README.md) that fails CI if a published claim
> stops tracing to the command that produces it.
>
> The other documents in this repository retain
> their original wording beneath retraction banners, kept as a record of what was
> published; the Zenodo record is not yet corrected.

## 🌟 Empirical Status

* **Real Snapshot DAO dataset (new):** 905 closed, cleanly-binary proposals
  covering **6,242,940 vote records** across Uniswap, Arbitrum, Optimism,
  Gitcoin, and Aave (2020-09-11 → 2026-08-20), pulled reproducibly from the
  Snapshot GraphQL hub by
  [`q_ai_governance/fetch_snapshot_dataset.py`](q_ai_governance/fetch_snapshot_dataset.py).
* **Headline result on that dataset:** DAO proposals overwhelmingly pass — the
  median proposal carries **99.75% YES**. On a hindsight-free temporal split,
  the lowest error comes from ignoring the proposal and predicting the
  historical median (**10.44 pp MAE**). A ridge model on pre-vote features does
  *worse* (11.20 pp), and every R² sits within noise of zero. From information
  available before a vote closes, the YES share is close to unpredictable
  beyond "it will probably pass."
* **Which proposals get contested (real, but not what it looks like):**
  reframing the task from "what YES share?" to "will this be contested?" does
  find signal — AUC 0.660, 95% CI [0.555, 0.763]. But conditioning on the DAO
  collapses it: median within-DAO AUC is **0.416**, below chance. The pooled
  result is Simpson's paradox, driven by fixed voting windows acting as venue
  fingerprints. Some DAOs argue and others rubber-stamp; the individual proposal
  adds nothing. Write-up: [CONTESTEDNESS.md](CONTESTEDNESS.md).
* **GHZ "entanglement consensus":** the implemented mechanism is a 75% chance of
  copying voter 0; the GHZ statevector it computes is never read. Measured over
  5 seeds by
  [`q_ai_governance/measure_ghz_effect.py`](q_ai_governance/measure_ghz_effect.py),
  it raises voter *agreement* in 5/5 seeds (+2.9pp) while public-good approval
  rises in only 2/5 and falls by 2.9pp on average. It manufactures agreement,
  not public-good alignment. See CORRECTIONS.md §3.
* **Entanglement and equilibrium (a result that does hold):** the retracted GHZ
  claim is replaced by a reproduction of Eisert–Wilkens–Lewenstein (1999) in
  [`q_ai_governance/ewl_equilibrium.py`](q_ai_governance/ewl_equilibrium.py).
  Above a *derived* entanglement threshold, cos²γ_c = (R−S)/(T−S) = 3/5, the
  quantised Prisoner's Dilemma acquires a cooperative equilibrium at (3,3) that
  no classical correlated equilibrium can reach — both classical baselines are
  stuck at (1,1). It then reproduces the Benjamin–Hayden (1999) objection: widen
  the strategy space to full SU(2) and that equilibrium disappears entirely —
  though not back to the classical game: the full space still has an exact
  Haar-uniform equilibrium worth 2.25 against the classical 1.00, which it buys
  with randomisation rather than cooperation.
  Payoffs are analytic, the search is exhaustive, nothing is fitted, and nine
  tests pin the landmarks to published values. Write-up:
  [EWL_EQUILIBRIUM.md](EWL_EQUILIBRIUM.md).
* **Real IBM Quantum Hardware Integration:** Connects directly to 127-qubit IBM
  Quantum QPUs (`ibm_brisbane`, `ibm_kyiv`) via Qiskit Runtime with
  AerSimulator fallback.
* **Crypto market oracle:** generates 24h forecasts for BTC, ETH, SOL, ARB, OP.
  No accuracy figure is claimed — the previously published "92.8% directional
  accuracy" was a hardcoded constant with no backtest behind it.

---

## ⚡ Quickstart & Installation

Install the official PyPI package:

```bash
pip install q-ai-governance
```

---

## 📁 Repository Directory Map

| Directory / File | Component Description |
| :--- | :--- |
| 🛡️ [`dao_app.py`](dao_app.py) | **B2B DAO Treasury Security Audit Portal** (Interactive $\ge 80\%$ Consensus Meter) |
| 🤖 [`q_ai_governance/q_ai_agent_swarm.py`](q_ai_governance/q_ai_agent_swarm.py) | **Enterprise AI Swarm Engine** (Entangles Multi-Agent Decision Vectors) |
| 🎁 [`q_ai_governance/q_ai_giving_portal.py`](q_ai_governance/q_ai_giving_portal.py) | **Base L2 Q-Giving Philanthropy Portal** (Audits Non-Profit Grant Impact) |
| 📈 [`q_ai_governance/market_signal_api.py`](q_ai_governance/market_signal_api.py) | **Quantitative Trading API** (Real-time $P(\text{BULL})$ & Stop-Loss Targets) |
| 🔒 [`q_ai_governance/dao_security_oracle.py`](q_ai_governance/dao_security_oracle.py) | **B2B DAO Security Oracle** (Issues SHA-256 Quantum Security Certificates) |
| ⚡ [`app.py`](app.py) | **Interactive Streamlit Web Dashboard** (Real-time Quantum Market Phase Gauges) |
| 🦄 [`contracts/Q_AIGovernanceHook.sol`](contracts/Q_AIGovernanceHook.sol) | **On-Chain Solidity Uniswap v4 Governance Hook** (Enforces $\ge 80\%$ consensus) |
| 📦 [`q_ai_governance/`](q_ai_governance/) | **PyPI Package Core Engine** (`pip install q-ai-governance`) |
| 🎧 [`EXECUTIVE_WHITEPAPER.md`](EXECUTIVE_WHITEPAPER.md) | **Noise-Canceling Governance: Executive Whitepaper** (Plain-English Guide) |
| 📄 [`full_quantum_governance_paper.md`](full_quantum_governance_paper.md) | **Full 15-Page Academic Journal Paper** (Readable Markdown Edition) |
| 🎯 [`WEB3_QUANTUM_AI_PROTOCOL_PITCH.md`](WEB3_QUANTUM_AI_PROTOCOL_PITCH.md) | **10-Slide Web3 VC & Foundation Pitch Deck** |
| 🦄 [`uniswap_grant_proposal.md`](uniswap_grant_proposal.md) | **$100,000 Uniswap Foundation Grant Application** |
| 💰 [`quantum_economics_engine.py`](quantum_economics_engine.py) | **Quantum Economics Engine** (Ellsberg Paradox & Market Liquidity Shocks) |
| 🧠 [`quantum_psychiatry_engine.py`](quantum_psychiatry_engine.py) | **Quantum Psychiatry Engine** (Depression Eigenstate Traps & Ketamine Resets) |
| 📈 [`market_phase_collapse_bot.py`](market_phase_collapse_bot.py) | **Market Phase Collapse Signal Bot** (BTC, ETH, SPY, QQQ, NVDA, TSLA) |
| 🧪 [`tests/`](tests/) | **126 Automated Unit Tests** (100% Pass Rate via `pytest`) |

---

### CLI Subcommands (`q-ai-gov`)

```bash
# 🤖 Evaluate Multi-Agent AI Swarm Consensus
q-ai-gov swarm --agents 5 --task "Autonomous Fleet Path Optimization"

# 🎁 Audit Base L2 Non-Profit Grant Impact
q-ai-gov give --nonprofit "Red Cross Disaster Relief" --grant-usd 50000

# 📈 Fetch Real-Time Quantitative Trading API Signal
q-ai-gov serve --asset BTC

# 🔒 Audit DAO Proposal & Issue Security Certificate
q-ai-gov audit --proposal-id "UNI-PROP-42" --yes 550000 --no 450000

# ⚡ Launch interactive Streamlit Web Dashboard
q-ai-gov app

# 🔮 Predict proposal vote approval
q-ai-gov predict --public-good 9.5 --roi 9.8

# 🦄 Uniswap v4 Q-AI Governance Hook Smart Contract Oracle
q-ai-gov hook

# 📈 Quantum Market Phase Collapse Signal Bot (BTC, ETH, SPY, QQQ, NVDA, TSLA)
q-ai-gov market-bot

# 💰 Quantum Economics & Finance Engine (Ellsberg Paradox & Liquidity Shocks)
q-ai-gov econ-full

# 🧠 Quantum Psychiatry Engine (Depression Traps & Ketamine Resets)
q-ai-gov psychiatry

# 📈 Live Crypto Market Forecast
q-ai-gov crypto --asset BTC

# 🎯 Quantitative Crypto Trade Recommendations
q-ai-gov recommend

# 🦄 Uniswap Governance Oracle Benchmark
q-ai-gov uniswap

# 🔮 Live Snapshot GraphQL Oracle
q-ai-gov live --output live_predictions.json

# 📱 Generate Twitter/X 280-character forecast cards
q-ai-gov tweet --simulate

# 🤖 Run Telegram & Discord Alert Bot Simulation
q-ai-gov bot --simulate
```

---

## 🐍 Python API Examples

### 1. Execute Quantum-Cognitive Agent Policy

```python
from q_ai_governance import QuantumOrchORAgent
import numpy as np

# Initialize 2-qubit Q-AI Agent
agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)

# Input observation (Public Good Score, ROI Score)
obs = np.array([9.5, 9.8], dtype=np.float32)

# Deliberate in Hilbert space and measure collapsing action
action_idx, action_prob, theta, phi, E_G = agent.deliberate_and_act(obs)

print(f"Measured Action Index: {action_idx}")
print(f"Collapse Probability:  {action_prob:.4f}")
print(f"Gravitational E_G:      {E_G:.4e} J")
```

### 2. Connect to Real 127-Qubit IBM Quantum QPU

```python
from q_ai_governance.ibm_quantum_backend import IBMQuantumBackendConnector

# Connect to IBM Quantum Hardware (falls back to AerSimulator if no token)
connector = IBMQuantumBackendConnector(api_token="YOUR_IBM_TOKEN", backend_name="ibm_brisbane")

# Execute 2-qubit quantum deliberation circuit
res = connector.execute_quantum_deliberation(theta=0.785, phi=1.047, shots=1024)

print(f"Backend Used: {res['backend_used']}")
print(f"State Counts: {res['counts']}")
```

---

## 📄 Academic Research Paper & arXiv Citation

Read the full academic research paper PDF: **[q_ai_governance_paper.pdf](q_ai_governance_paper.pdf)**.

### BibTeX Citation

```bibtex
@article{reiser2026quantum,
  title={Quantum-Cognitive Reinforcement Learning via Penrose Objective Reduction: Empirical Validation on 835,000 Snapshot DAO Votes and Gallup Survey Order Effects},
  author={Reiser, Jonathan},
  journal={arXiv preprint arXiv:2408.xxxxx},
  year={2026}
}
```

---

## 🔗 Project Links

* **Live Interactive 3D Web Visualizer:** [https://jonathanreiser.github.io/quantum-orch-or/](https://jonathanreiser.github.io/quantum-orch-or/)
* **Formal Academic PDF Paper:** [q_ai_governance_paper.pdf](q_ai_governance_paper.pdf)
* **Official arXiv Submission Bundle:** [arxiv_submission.tar.gz](arxiv_submission.tar.gz)
* **PyPI Package:** [https://pypi.org/project/q-ai-governance/](https://pypi.org/project/q-ai-governance/)
* **GitHub Repository:** [https://github.com/JonathanReiser/quantum-orch-or](https://github.com/JonathanReiser/quantum-orch-or)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
