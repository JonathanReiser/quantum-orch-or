# Does entanglement change the equilibrium?

**2026-08-30.** This is the constructive half of [CORRECTIONS.md](CORRECTIONS.md).

That document retracts this project's "GHZ Entanglement Consensus Theorem" —
the claim that entanglement doubles public-good proposal approval from 40% to
80%. The claim failed because the implementation was a 75% chance of copying one
voter, and because it measured *agreement* while reporting *public-good
alignment*.

The underlying question was worth asking. This is that question, asked somewhere
it has a published answer, so the result can be checked rather than believed.

Run it:

```bash
python3 q_ai_governance/ewl_equilibrium.py
```

---

## The setup

The Eisert–Wilkens–Lewenstein quantisation of the Prisoner's Dilemma
(*Phys. Rev. Lett.* **83**, 3077, 1999). Two players share an entangled qubit
pair, each applies a local unitary, the pair is disentangled, and the result is
measured. Payoffs are the ones already in this repository's
`QuantumPrisonerDilemmaEnv`: (C,C)=(3,3), (C,D)=(0,5), (D,C)=(5,0), (D,D)=(1,1).

An entanglement parameter γ tunes the game: γ=0 is the ordinary classical
dilemma, γ=π/2 is maximal entanglement.

**Two classical baselines**, because both objections need answering:

| baseline | payoff | why it matters |
|---|---|---|
| Nash equilibrium (D,D) | (1, 1) | the classical dilemma's trap |
| **best correlated equilibrium** | **(1, 1)** | the "it's just shared randomness" objection |

The second is the important one. Any claim of quantum advantage in a game
invites the reply that entanglement is merely correlated randomness — and
correlated randomness has a name, the correlated equilibrium. It cannot help
here: D strictly dominates C, so *every* correlated equilibrium places all its
mass on (D,D). This is solved by linear programming in
`classical_correlated_equilibrium()` rather than asserted.

## What the code does, and does not, do

* Payoffs are computed **analytically from the statevector**. No sampling, no
  estimator noise, exactly reproducible.
* Equilibria are found by **exhaustive grid search**, never by an optimiser.
  `CORRECTIONS.md` §7 explains why: this project's hill climb is noise-dominated
  and accepted 0 of 40 moves while printing a converged-looking loss curve. A
  grid cannot fail that way.
* Grid coarseness biases *towards* finding spurious equilibria, since fewer
  deviations get tested. So "no equilibrium found" is the conservative
  direction, and the central positive claim is re-checked independently against
  a dense random deviation search.
* **Nothing here is fitted, and nothing is hardcoded.**

---

## Result 1 — EWL reproduces, above a threshold

Restricted (2-parameter) strategy space, 861 strategies, 741,321 profiles:

| γ | pure Nash equilibria | best NE payoff | (Q,Q) an equilibrium? |
|---|---|---|---|
| 0.000 | 441 | 1.000 | no |
| 0.314 | 441 | 1.000 | no |
| 0.628 | 42 | 2.500 | no |
| 0.942 | **1** | **3.000** | **yes** |
| 1.257 | 1 | 3.000 | yes |
| 1.571 (π/2) | 1 | 3.000 | yes |

At γ=0 the game is exactly the classical dilemma and the equilibrium pays 1.
Above a threshold, (Q,Q) with Q = diag(i, −i) becomes the *unique* pure
equilibrium and pays **(3,3)** — beating classical Nash **and** the best
correlated equilibrium, both stuck at (1,1).

**The threshold is derived, not fitted.** While the opponent plays Q, the best
deviation is D, and it pays (T−S)·cos²γ + S. That falls to the cooperative
payoff R when

> cos²(γ_c) = (R−S)/(T−S) = 3/5,  γ_c = arccos(√(3/5)) ≈ 0.684719 rad ≈ 39.23°

A dense sweep confirms it to |error| ≈ 2×10⁻¹⁰.

## Result 2 — and it does not survive Benjamin–Hayden

Full SU(2) strategy space, 2,197 strategies, 4,826,809 profiles:

| γ | pure Nash equilibria | best NE payoff |
|---|---|---|
| 0.000 | 28,561 | 1.000 |
| 0.314 | 4,394 | 1.188 |
| 0.628 | **0** | — |
| 0.942 | **0** | — |
| 1.257 | **0** | — |
| 1.571 (π/2) | **0** | — |

Benjamin & Hayden (*Phys. Rev. Lett.* **87**, 069801) objected that EWL's result
depends on an arbitrarily restricted strategy set. It does. Allow the second
phase to vary — nothing exotic, just the rest of SU(2) — and (Q,Q) stops being
an equilibrium at every γ, and no pure-strategy equilibrium exists at all above
γ≈0.63.

## Result 3 — but Benjamin–Hayden removes the equilibrium, not the advantage

"No pure equilibrium" is not "no equilibrium." Glicksberg's theorem guarantees a
mixed one exists here, since SU(2) is compact and the payoffs are continuous. So
the question Result 2 leaves open is: played well over the *full* strategy space,
what is this game worth?

At maximal entanglement the answer is exact. Against an opponent drawing its
strategy Haar-uniformly from SU(2), the payoff is

> u_A(θ, γ) = (T+R+P+S)/4 − [(T+P−R−S)/4] · cos²γ · cos θ

computed in closed form via the twirl identity
E_U[(I⊗U)σ(I⊗U)†] = Tr_B(σ)⊗I/2, and agreeing with the exact channel to
~10⁻¹⁵. Two things follow:

* The payoff depends on **neither phase** — only on θ.
* The θ-dependence carries a factor of cos²γ, so it vanishes **exactly** at
  γ=π/2 and at no smaller entanglement.

At γ=π/2 every SU(2) strategy therefore earns exactly the same amount, every
strategy is a best response, and the Haar-uniform strategy is a symmetric Nash
equilibrium. Its value is (T+R+P+S)/4 = **2.25**.

| γ | C vs Haar | D vs Haar | exploitability | equilibrium? |
|---|---|---|---|---|
| 0.000 | 1.500 | 3.000 | 1.50 | no |
| 0.524 | 1.688 | 2.813 | 1.13 | no |
| 1.047 | 2.063 | 2.438 | 0.375 | no |
| 1.309 | 2.200 | 2.300 | 0.100 | no |
| **1.571 (π/2)** | **2.250** | **2.250** | **0** | **yes** |

So the full ordering is:

| | payoff |
|---|---|
| classical Nash (D,D) | 1.00 |
| best classical correlated equilibrium | 1.00 |
| **full SU(2) Haar equilibrium** | **2.25** |
| EWL restricted-space (Q,Q) | 3.00 |

**Benjamin–Hayden removes EWL's pure equilibrium, not the entanglement
advantage.** The full-space equilibrium recovers 62.5% of the distance from the
classical trap to full cooperation, and still strictly beats everything
classically available.

Three caveats, because they matter more than the headline:

1. **This is not cooperation.** The equilibrium outcome distribution is uniform
   over all four cells — 25% mutual cooperation, 25% mutual defection, 50%
   one-sided exploitation. The 2.25 is the flat average of the payoff matrix.
   Players are not coordinating; they are scrambling. It Pareto-dominates the
   classical equilibrium, which is a real statement, but calling it cooperation
   would be the same conflation this repository was previously guilty of.
2. **It is a knife-edge.** Haar is an equilibrium only at γ=π/2 exactly. At any
   smaller entanglement D strictly beats it, with the gap
   ((T+P−R−S)/2)·cos²γ. What the equilibrium looks like for
   0.63 < γ < π/2 is not answered here.
3. **Uniqueness is not established.** One equilibrium has been certified
   exactly. Others may exist with different values; no claim is made that 2.25
   is *the* value of the game.

A note on method: replicator dynamics was tried first and is the wrong tool. The
uniform point is an equilibrium but an unstable one under replicator, so the
dynamics amplify differences and wander away from the very solution being looked
for — it reported a "value" of 2.56 with exploitability 2.34 after 20,000
iterations. The closed form has no such failure mode, and no optimiser appears
anywhere in `ewl_mixed_equilibrium.py`.

---

## The honest conclusion

Both statements are true, and neither is usable alone:

1. Entanglement genuinely changes the equilibrium structure of this game, and at
   γ ≥ 0.685 it supports a cooperative equilibrium that **no classical
   correlated device can reach**. That is a real separation from shared
   randomness, not a rhetorical one.
2. That cooperative equilibrium exists **only because the strategy space was
   restricted**, and the restriction has no physical justification. Widen it and
   the equilibrium disappears.
3. Widening it does **not** return you to the classical game. At maximal
   entanglement the full space still has an exact equilibrium worth 2.25 against
   the classical 1.00 — but it buys that with randomisation, not cooperation.

So the defensible claim is narrow and conditional: *given* a restricted strategy
set, entanglement above a derived threshold converts the Prisoner's Dilemma into
a game with a cooperative equilibrium. Anything broader — "quantum entanglement
solves cooperation", "entanglement doubles public-good approval" — is not
supported here, and the second of those is what this repository previously
published.

This result also transfers nothing to DAO governance on its own. Real voters are
not entangled qubits, and no claim in this file should be read as being about
Snapshot proposals. The empirical governance question is answered separately,
and negatively, in [CORRECTIONS.md](CORRECTIONS.md).

## Reproducing

```bash
python3 q_ai_governance/ewl_equilibrium.py --out data/ewl_equilibrium_results.json
python3 q_ai_governance/ewl_mixed_equilibrium.py
python3 -m pytest tests/test_ewl_equilibrium.py tests/test_ewl_mixed_equilibrium.py -q
```

Nine tests pin the landmarks above to their published values — the classical
limit, unitarity, Q beating D under entanglement, the threshold's closed form,
the Benjamin–Hayden collapse, and the correlated-equilibrium bound.
