"""
Tests for quantum_game.py's EWL Quantum Prisoner's Dilemma model.

simulate_game() computes payoffs from an exact statevector (no shot
sampling), so these are deterministic and can be checked against the
payoff table documented in README.md to tight tolerance — this doubles
as a regression test for that table.

Note the returned probs tuple's order is (p_CC, p_CD, p_DC, p_DD) — see
simulate_game()'s own return statement — which is NOT the same order as
the function's internal `probs` array (p_CC, p_DC, p_CD, p_DD indices
0-3); tests below index into the tuple simulate_game() actually returns.
"""
import pytest

from quantum_game import simulate_game, U_C, U_D, U_Q


def test_classical_mutual_cooperation():
    (pay1, pay2), probs = simulate_game(U_C, U_C)
    assert (pay1, pay2) == pytest.approx((3.0, 3.0))
    assert probs[0] == pytest.approx(1.0)  # p_CC


def test_classical_mutual_defection():
    (pay1, pay2), probs = simulate_game(U_D, U_D)
    assert (pay1, pay2) == pytest.approx((1.0, 1.0))
    assert probs[3] == pytest.approx(1.0)  # p_DD


def test_classical_unilateral_defection():
    (pay1, pay2), probs = simulate_game(U_D, U_C)
    assert (pay1, pay2) == pytest.approx((5.0, 0.0))
    assert probs[2] == pytest.approx(1.0)  # p_DC (tuple position 2 — see module docstring)


def test_quantum_strategy_punishes_a_defector():
    # The headline EWL result: playing Q against a classical defector
    # flips the exploitation around — Player 1 (Q) gets 5, the defector
    # gets 0 — per README's documented payoff table.
    (pay1, pay2), probs = simulate_game(U_Q, U_D)
    assert (pay1, pay2) == pytest.approx((5.0, 0.0))


def test_quantum_mutual_cooperation_is_new_nash_equilibrium():
    (pay1, pay2), probs = simulate_game(U_Q, U_Q)
    assert (pay1, pay2) == pytest.approx((3.0, 3.0))
    assert probs[0] == pytest.approx(1.0)  # p_CC


def test_probabilities_always_sum_to_one():
    for s1, s2 in [(U_C, U_C), (U_D, U_D), (U_D, U_C), (U_Q, U_D), (U_Q, U_Q)]:
        _, probs = simulate_game(s1, s2)
        assert sum(probs) == pytest.approx(1.0)
