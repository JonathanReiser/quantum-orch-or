"""
benchmark_qai_real.py — put QuantumOrchORAgent on the real Snapshot benchmark.

The agent is *fitted* on the training split before it is scored, because an
unfitted QuantumOrchORAgent has random weights: the same proposal scores
differently on every run, so any number it produces is noise. (This is the bug
behind the original benchmark, which never called update_policy at all.)

Fitting uses the same (1+1) random-mutation hill climb as
train_uniswap_governance_agent.py, generalised to arbitrary feature width and
parallelised across cores, since each rollout is a Trotterised simulation.

Everything is evaluated on the same temporal split as the classical baselines
so the numbers are directly comparable.
"""

import argparse
import json
import os
import time
from multiprocessing import Pool

# Aer and the BLAS backends each spawn their own thread pool. With one worker
# per core that oversubscribes badly (6 workers x 6 threads on 6 cores), so pin
# every worker to a single thread before numpy or qiskit is imported.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "QISKIT_NUM_PROCS", "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

try:
    from .features import build_matrix, FEATURE_NAMES
    from .benchmark_snapshot_real import metrics
except ImportError:
    from features import build_matrix, FEATURE_NAMES
    from benchmark_snapshot_real import metrics

NUM_QUBITS = 2
_AGENT = None


def standardise(Xtr, Xte):
    """Z-score using TRAIN statistics only, so the test split leaks nothing."""
    A = np.asarray(Xtr, dtype=float)
    mu, sd = A.mean(0), A.std(0)
    sd[sd == 0] = 1.0
    return ((A - mu) / sd).tolist(), ((np.asarray(Xte, dtype=float) - mu) / sd).tolist()


def _init_worker(num_qubits, state_dim):
    """One agent per worker process; rollouts are the expensive part, not setup."""
    global _AGENT
    from quantum_agent import QuantumOrchORAgent
    _AGENT = QuantumOrchORAgent(num_qubits=num_qubits, state_dim=state_dim)


def _rollout_batch(task):
    """Estimate P(YES) for one observation under given weights."""
    weights, bias, obs, n_rollouts, seed = task
    np.random.seed(seed)
    _AGENT.weights = weights
    _AGENT.bias = bias
    yes = 0
    for _ in range(n_rollouts):
        collapsed_idx = _AGENT.deliberate_and_act(np.asarray(obs, dtype=np.float32))[0]
        # Same YES convention as the original benchmark: even collapse index.
        if collapsed_idx % 2 == 0:
            yes += 1
    return 100.0 * yes / n_rollouts


def predict(pool, weights, bias, Xs, n_rollouts, seed0):
    tasks = [(weights, bias, x, n_rollouts, seed0 + i) for i, x in enumerate(Xs)]
    return np.array(pool.map(_rollout_batch, tasks))


def fit(pool, Xtr, ytr, state_dim, iters, n_rollouts, seed=42, sigma=0.25):
    """(1+1) hill climb with the incumbent RE-EVALUATED every iteration.

    The loss is estimated from a finite number of stochastic rollouts, so it is
    noisy. train_uniswap_governance_agent.py scores the incumbent once and then
    only ever compares fresh candidates against that single measurement; when
    the first measurement happens to land low, no candidate can beat it and the
    search accepts nothing for the whole run while appearing to have "converged".
    That failure is silent — the loss history is flat, which reads like success.

    Re-scoring the incumbent on a fresh seed each iteration costs one extra
    evaluation per step and removes the ratchet.
    """
    rng = np.random.default_rng(seed)
    w = rng.normal(scale=0.1, size=(NUM_QUBITS * 2 + 2, state_dim))
    b = rng.normal(scale=0.1, size=(NUM_QUBITS * 2 + 2,))

    def loss(ww, bb, s):
        pred = predict(pool, ww, bb, Xtr, n_rollouts, s)
        return float(np.mean((pred - np.asarray(ytr)) ** 2))

    best = loss(w, b, 10_000)
    history, accepted = [best], 0
    for i in range(iters):
        cw = w + rng.normal(scale=sigma, size=w.shape)
        cb = b + rng.normal(scale=sigma, size=b.shape)
        seed_i = 20_000 + i * 997
        cand = loss(cw, cb, seed_i)
        incumbent = loss(w, b, seed_i + 1)   # fresh estimate, same budget
        if cand < incumbent:
            w, b, best, accepted = cw, cb, cand, accepted + 1
        else:
            best = incumbent
        history.append(best)
        if (i + 1) % 10 == 0:
            print(f"    iter {i+1:>3}/{iters}  train MSE {best:9.2f}  "
                  f"(RMSE {best**0.5:.2f} pp)  accepted {accepted}", flush=True)
    return w, b, history, accepted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/snapshot_dao_dataset.json")
    ap.add_argument("--test-frac", type=float, default=0.30)
    ap.add_argument("--fit-sample", type=int, default=100,
                    help="training proposals sampled per loss evaluation")
    ap.add_argument("--iters", type=int, default=60)
    ap.add_argument("--rollouts-fit", type=int, default=8)
    ap.add_argument("--rollouts-eval", type=int, default=30)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="data/benchmark_qai_results.json")
    args = ap.parse_args()

    payload = json.load(open(args.data))
    X, y, meta = build_matrix(payload["proposals"])
    cut = int(len(y) * (1 - args.test_frac))
    Xtr, ytr, Xte, yte = X[:cut], y[:cut], X[cut:], y[cut:]
    Xtr, Xte = standardise(Xtr, Xte)
    state_dim = len(FEATURE_NAMES)

    rng = np.random.default_rng(7)
    idx = rng.choice(len(Xtr), size=min(args.fit_sample, len(Xtr)), replace=False)
    Xfit = [Xtr[i] for i in idx]
    yfit = [ytr[i] for i in idx]

    print(f"train {cut} / test {len(yte)} | fitting on {len(Xfit)} sampled train proposals")
    print(f"workers={args.workers}  iters={args.iters}  "
          f"rollouts fit/eval = {args.rollouts_fit}/{args.rollouts_eval}\n")

    t0 = time.time()
    with Pool(args.workers, initializer=_init_worker,
              initargs=(NUM_QUBITS, state_dim)) as pool:
        print("  [1/3] fitting agent weights on the training split")
        w, b, history, accepted = fit(pool, Xfit, yfit, state_dim,
                                      args.iters, args.rollouts_fit)

        print("\n  [2/3] scoring the UNFITTED agent on the test split")
        r0 = np.random.default_rng(3)
        w0 = r0.normal(scale=0.1, size=w.shape)
        b0 = r0.normal(scale=0.1, size=b.shape)
        pred_untrained = predict(pool, w0, b0, Xte, args.rollouts_eval, 500_000)

        print("  [3/3] scoring the FITTED agent on the test split")
        pred_trained = predict(pool, w, b, Xte, args.rollouts_eval, 900_000)

    out = {
        "n_train": cut, "n_test": len(yte),
        "fit_sample": len(Xfit), "iters": args.iters,
        "rollouts_fit": args.rollouts_fit, "rollouts_eval": args.rollouts_eval,
        "elapsed_sec": round(time.time() - t0, 1),
        "train_mse_history": [round(float(h), 3) for h in history],
        "accepted_moves": accepted,
        "qai_untrained": metrics(yte, pred_untrained),
        "qai_trained": metrics(yte, pred_trained),
        "qai_trained_pred_mean": float(np.mean(pred_trained)),
        "qai_trained_pred_sd": float(np.std(pred_trained)),
        "qai_untrained_pred_mean": float(np.mean(pred_untrained)),
        "qai_untrained_pred_sd": float(np.std(pred_untrained)),
        "predictions_trained": [float(v) for v in pred_trained],
        "y_test": [float(v) for v in yte],
    }
    np.savez("q_ai_governance/trained_snapshot_agent_weights.npz", weights=w, bias=b)
    json.dump(out, open(args.out, "w"), indent=2)

    print(f"\n{'model':<28}{'MAE (pp)':>10}{'RMSE (pp)':>11}{'R^2':>9}")
    print("-" * 60)
    for k in ("qai_untrained", "qai_trained"):
        m = out[k]
        print(f"{k:<28}{m['mae_pp']:>10.2f}{m['rmse_pp']:>11.2f}{m['r2']:>9.3f}")
    print("-" * 60)
    print(f"accepted moves during fit: {accepted}/{args.iters}")
    print(f"fitted agent predictions: mean {out['qai_trained_pred_mean']:.1f}%  "
          f"sd {out['qai_trained_pred_sd']:.2f}pp")
    print(f"elapsed {out['elapsed_sec']}s -> {args.out}")


if __name__ == "__main__":
    main()
