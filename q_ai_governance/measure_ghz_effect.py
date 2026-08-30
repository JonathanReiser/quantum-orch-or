"""
measure_ghz_effect.py — what does `entangled_consensus` actually change?

The published claim is that GHZ statevector entanglement "doubles public-good
proposal approval consensus from 40% to 80%". governance_integration.py reports
a `consensus_metric`, but that metric is max(yes, no) / num_voters — it measures
agreement in *either* direction, so a mechanism that makes voters copy each
other raises it regardless of what they agree on.

This script separates the two quantities the claim conflates:
  * YES rate   — did the public-good proposal actually get approved more?
  * consensus  — did voters merely agree with each other more?

on strong public-good proposals (impact vector [0.9, 0.1]), across 5 seeds.

Usage:  python3 q_ai_governance/measure_ghz_effect.py
"""

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from governance_integration import QuantumGovernanceSimulation, GovernanceProposal

N_PROPS, N_VOTERS, N_SEEDS = 20, 8, 5
PUBLIC_GOOD_VECTOR = [0.9, 0.1]   # high public good, low private profit


def main():
    rows = {False: [], True: []}
    for seed in range(N_SEEDS):
        for entangled in (False, True):
            np.random.seed(seed)
            sim = QuantumGovernanceSimulation(
                num_voters=N_VOTERS, entangled_consensus=entangled)
            yes_rates, consensus = [], []
            for i in range(N_PROPS):
                proposal = GovernanceProposal(i, f"public-good-{i}", PUBLIC_GOOD_VECTOR)
                votes, _passed, _latency, cons = sim.run_proposal_vote(proposal)
                yes_rates.append(votes.count(0) / N_VOTERS)   # vote 0 == YES
                consensus.append(cons)
            rows[entangled].append((float(np.mean(yes_rates)), float(np.mean(consensus))))

    print(f"{N_SEEDS} seeds | {N_VOTERS} voters | {N_PROPS} proposals "
          f"| impact vector {PUBLIC_GOOD_VECTOR}\n")
    print(f"{'seed':>5}{'YES off':>10}{'YES on':>9}{'dYES':>9}"
          f"{'cons off':>11}{'cons on':>10}{'dcons':>9}")
    d_yes, d_cons = [], []
    for s in range(N_SEEDS):
        y0, c0 = rows[False][s]
        y1, c1 = rows[True][s]
        d_yes.append(y1 - y0)
        d_cons.append(c1 - c0)
        print(f"{s:>5}{y0*100:>9.1f}%{y1*100:>8.1f}%{(y1-y0)*100:>+8.1f}"
              f"{c0*100:>10.1f}%{c1*100:>9.1f}%{(c1-c0)*100:>+8.1f}")

    pct = lambda a: float(np.mean(a)) * 100
    print(f"\nmean YES  : {pct([r[0] for r in rows[False]]):.1f}% -> "
          f"{pct([r[0] for r in rows[True]]):.1f}%  "
          f"(delta {pct(d_yes):+.1f}pp, range {min(d_yes)*100:+.1f} to {max(d_yes)*100:+.1f})")
    print(f"mean cons : {pct([r[1] for r in rows[False]]):.1f}% -> "
          f"{pct([r[1] for r in rows[True]]):.1f}%  "
          f"(delta {pct(d_cons):+.1f}pp, range {min(d_cons)*100:+.1f} to {max(d_cons)*100:+.1f})")
    print(f"\nconsensus rose in {sum(1 for d in d_cons if d > 0)}/{N_SEEDS} seeds; "
          f"YES rose in {sum(1 for d in d_yes if d > 0)}/{N_SEEDS} seeds")


if __name__ == "__main__":
    main()
