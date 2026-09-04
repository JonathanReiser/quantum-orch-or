"""
probe_engine_degeneracy.py — what the Q-AI engine actually does, measured.

Run BEFORE interpreting any benchmark that uses QuantumOrchORAgent, and cited by
PREREGISTRATION_narrow_contestedness.md. Every claim in the pre-registration's
"Known properties of the engine" section is produced here, from a live run, so
that none of them can later be presented as a convenient post-hoc explanation.

    python3 tools/probe_engine_degeneracy.py

Touches no labels and no dataset — it probes the engine alone.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q_ai_governance.quantum_agent import QuantumOrchORAgent  # noqa: E402

SEED = 20260904
DT = 0.005


def probe_determinism(agent, obs, n=50):
    """Is anything except the final collapse draw stochastic?"""
    coh, steps, idx = [], [], []
    for _ in range(n):
        i, s, c, _, _ = agent.deliberate_and_act(obs, dt=DT)
        coh.append(c); steps.append(s); idx.append(i)
    return {
        "coherence_std": float(np.std(coh)),
        "coherence_unique": len(set(np.round(coh, 12))),
        "steps_unique": sorted(set(steps)),
        "collapsed_idx_counts": np.bincount(idx, minlength=2 ** agent.num_qubits).tolist(),
    }


def probe_coupling(agent, obs):
    """How much phase does the 'quantum coupling' actually accumulate?"""
    _, J, g = agent._compute_circuit_params(obs)
    _, steps, _, _, _ = agent.deliberate_and_act(obs, dt=DT)
    return {
        "J_coupling": float(J),
        "g_tunneling": float(g),
        "rzz_angle_per_step_rad": float(-2.0 * J * DT),
        "steps_to_collapse": int(steps),
        "total_zz_phase_rad": float(abs(2.0 * J * DT * steps)),
    }


def probe_entangling_gates(agent):
    """Does the initial circuit entangle at all?"""
    rot, _, _ = agent._compute_circuit_params(np.zeros(agent.state_dim, dtype=np.float32))
    qc = agent._build_initial_circuit(rot)
    ops = {name: int(count) for name, count in qc.count_ops().items()}
    two_qubit = sum(c for n, c in ops.items() if n in ("cx", "cz", "rzz", "swap"))
    return {"initial_circuit_ops": ops, "two_qubit_gate_count": two_qubit}


def main():
    np.random.seed(SEED)
    agent = QuantumOrchORAgent(num_qubits=4, state_dim=2)
    obs = np.array([1.0, -2.0], dtype=np.float32)

    det = probe_determinism(agent, obs)
    cpl = probe_coupling(agent, obs)
    ent = probe_entangling_gates(agent)

    print(f"engine degeneracy probe — seed {SEED}, obs {obs.tolist()}\n")

    print("1. determinism across 50 rollouts at a FIXED observation")
    print(f"   coherence_at_collapse std   : {det['coherence_std']:.3e}")
    print(f"   coherence_at_collapse unique: {det['coherence_unique']}")
    print(f"   steps_to_collapse unique    : {det['steps_unique']}")
    verdict_det = det["coherence_std"] < 1e-12 and len(det["steps_unique"]) == 1
    print(f"   => deterministic given obs  : {verdict_det}")
    print("      (the ONLY stochastic element is the final collapse draw)\n")

    print("2. entangling structure of the initial circuit")
    print(f"   ops                : {ent['initial_circuit_ops']}")
    print(f"   two-qubit gates    : {ent['two_qubit_gate_count']}")
    print(f"   => product state   : {ent['two_qubit_gate_count'] == 0}\n")

    print("3. is the ZZ coupling numerically active?")
    print(f"   J_coupling         : {cpl['J_coupling']:.6e}")
    print(f"   rzz angle per step : {cpl['rzz_angle_per_step_rad']:.3e} rad")
    print(f"   steps to collapse  : {cpl['steps_to_collapse']}")
    print(f"   total ZZ phase     : {cpl['total_zz_phase_rad']:.3e} rad")
    print(f"   => inert (<1e-3 rad): {cpl['total_zz_phase_rad'] < 1e-3}\n")

    print("conclusion: the engine is a deterministic nonlinear map from the")
    print("observation to a fixed probability vector, plus one multinomial draw.")
    print("Its score functions are a fixed random feature map, not quantum")
    print("uncertainty, and must be described that way.")


if __name__ == "__main__":
    main()
