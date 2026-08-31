"""
train_uniswap_governance_agent.py — Actually fits QuantumOrchORAgent's policy weights
to real historical DAO vote outcomes, instead of leaving them at their random init.

Method (documented plainly, not oversold):
  - Supervised fit, not the REINFORCE stub in quantum_agent.update_policy() (that stub
    is used elsewhere for a different purpose — modeling multi-agent self-play voting
    dynamics under reward shaping — and is left untouched here).
  - Objective: squared error between the agent's sampled YES-fraction (average of
    N_ROLLOUTS_TRAIN independent deliberate_and_act() calls) and the real historical
    YES fraction, averaged over the training proposals.
  - Optimizer: (1+1) random-mutation hill climbing — perturb the current weights with
    Gaussian noise, keep the perturbation only if it lowers training loss. Simple,
    fully budget-controlled (exactly N_ITERS+1 loss evaluations), and appropriate for
    a noisy, low-dimensional, non-differentiable-in-practice objective (the "loss" is
    a Monte Carlo estimate over stochastic quantum circuit collapses).
  - Evaluation: leave-one-out cross-validation across the (only) 5 known real historical
    proposals in benchmark_real_dao_data.py. LOO is used *because* n=5 is too small for
    a held-out test split to mean anything otherwise — every example gets exactly one
    genuine out-of-fold prediction. This still does not make n=5 a large-sample claim;
    treat the resulting error estimate as a rough, honest signal, not a headline number.

Run: python -m q_ai_governance.train_uniswap_governance_agent
"""

import copy
import json
import time

import numpy as np

try:
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
    from q_ai_governance.benchmark_real_dao_data import REAL_DAO_HISTORICAL_DATA
except ImportError:
    from quantum_agent import QuantumOrchORAgent
    from benchmark_real_dao_data import REAL_DAO_HISTORICAL_DATA

N_ROLLOUTS_TRAIN = 8     # cheap, noisy estimate used while searching
N_ROLLOUTS_EVAL = 50     # same rollout count the rest of the codebase already uses for reporting
N_ITERS = 35              # hill-climbing steps (fixed budget, see module docstring)
SIGMA0 = 0.15              # initial mutation stddev
SIGMA_DECAY = 0.97


def _predict_yes_fraction(weights, bias, obs, n_rollouts):
    agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)
    agent.weights = weights
    agent.bias = bias
    yes = 0
    for _ in range(n_rollouts):
        idx, _, _, _, _ = agent.deliberate_and_act(obs)
        if idx % 2 == 0:
            yes += 1
    return yes / n_rollouts


def _train_loss(weights, bias, examples, n_rollouts):
    errs = [
        (_predict_yes_fraction(weights, bias, obs, n_rollouts) - real_frac) ** 2
        for obs, real_frac in examples
    ]
    return float(np.mean(errs))


def fit_weights(train_examples, n_iters=N_ITERS, n_rollouts=N_ROLLOUTS_TRAIN, seed=None):
    """(1+1) hill-climb weights/bias to minimize squared error on train_examples.
    Returns (weights, bias, loss_history)."""
    rng = np.random.default_rng(seed)
    init_agent = QuantumOrchORAgent(num_qubits=2, state_dim=2)
    weights, bias = init_agent.weights.copy(), init_agent.bias.copy()

    loss = _train_loss(weights, bias, train_examples, n_rollouts)
    sigma = SIGMA0
    history = [loss]

    for _ in range(n_iters):
        cand_w = weights + rng.normal(scale=sigma, size=weights.shape)
        cand_b = bias + rng.normal(scale=sigma, size=bias.shape)
        cand_loss = _train_loss(cand_w, cand_b, train_examples, n_rollouts)
        if cand_loss < loss:
            weights, bias, loss = cand_w, cand_b, cand_loss
        sigma *= SIGMA_DECAY
        history.append(loss)

    return weights, bias, history


def run_leave_one_out():
    data = REAL_DAO_HISTORICAL_DATA
    examples = [
        (np.array([d["public_good_score"], d["roi_score"]], dtype=np.float32),
         d["historical_yes_pct"] / 100.0,
         d)
        for d in data
    ]

    fold_results = []
    t_start = time.time()
    for i in range(len(examples)):
        test_obs, test_real, test_meta = examples[i]
        train_set = [(obs, real) for j, (obs, real, _) in enumerate(examples) if j != i]

        weights, bias, history = fit_weights(train_set, seed=1000 + i)
        pred = _predict_yes_fraction(weights, bias, test_obs, N_ROLLOUTS_EVAL)
        err_pct = abs(pred * 100.0 - test_meta["historical_yes_pct"])

        fold_results.append({
            "held_out_proposal_id": test_meta["proposal_id"],
            "dao": test_meta["dao"],
            "real_yes_pct": test_meta["historical_yes_pct"],
            "predicted_yes_pct": round(pred * 100.0, 1),
            "abs_error_pct": round(err_pct, 1),
            "train_loss_start": round(history[0], 4),
            "train_loss_end": round(history[-1], 4),
        })
        print(f"[fold {i+1}/{len(examples)}] held out {test_meta['proposal_id']} "
              f"({test_meta['dao']}): real={test_meta['historical_yes_pct']}% "
              f"pred={round(pred*100.0,1)}% abs_err={round(err_pct,1)}pp "
              f"(train loss {history[0]:.4f} -> {history[-1]:.4f})")

    elapsed = time.time() - t_start
    mae = float(np.mean([r["abs_error_pct"] for r in fold_results]))

    summary = {
        "method": "leave-one-out CV, (1+1) hill-climb supervised fit "
                  "(see train_uniswap_governance_agent.py docstring)",
        "n_examples": len(examples),
        "n_rollouts_eval_per_prediction": N_ROLLOUTS_EVAL,
        "hillclimb_iters": N_ITERS,
        "mean_absolute_error_pct": round(mae, 2),
        "elapsed_seconds": round(elapsed, 1),
        "folds": fold_results,
        "caveat": "n=5 is too small to support a headline accuracy claim; this is an "
                  "honest signal on the only real historical data currently in the repo, "
                  "not a statistically meaningful validation.",
    }
    return summary


def fit_production_weights(output_path="q_ai_governance/trained_uniswap_agent_weights.npz"):
    """Final fit on ALL 5 known examples (no held-out fold) — these are the weights
    actually used for predicting genuinely new/unseen proposals."""
    data = REAL_DAO_HISTORICAL_DATA
    examples = [
        (np.array([d["public_good_score"], d["roi_score"]], dtype=np.float32),
         d["historical_yes_pct"] / 100.0)
        for d in data
    ]
    weights, bias, history = fit_weights(examples, seed=42)
    np.savez(output_path, weights=weights, bias=bias)
    print(f"Saved production-fit weights to {output_path} "
          f"(train loss {history[0]:.4f} -> {history[-1]:.4f})")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("  LEAVE-ONE-OUT CV — QuantumOrchORAgent vs REAL_DAO_HISTORICAL_DATA")
    print("=" * 60)
    summary = run_leave_one_out()
    with open("uniswap_agent_loo_cv_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nMean Absolute Error (LOO-CV, n={summary['n_examples']}): "
          f"{summary['mean_absolute_error_pct']}pp")
    print(f"Elapsed: {summary['elapsed_seconds']}s")
    print("Saved full results to uniswap_agent_loo_cv_results.json")

    fit_production_weights()
