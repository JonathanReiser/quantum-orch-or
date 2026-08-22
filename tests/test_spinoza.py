"""
Tests for spinoza_mind.py's entangled dual-mind circuit.

run_local_simulation() samples 1024 shots, so exactly-zero-probability
outcomes are asserted exactly (an ideal simulator never samples an
outcome with zero amplitude), while genuinely probabilistic outcomes
(the 50/50 split) are checked with a generous statistical tolerance.
"""
import pytest

from spinoza_mind import run_local_simulation


def test_no_deliberation_keeps_minds_in_bell_state_agreement():
    # theta=0: RY(0) is identity, so the state stays the Bell state
    # (|00>+|11>)/sqrt(2) — P(01)=P(10) should be exactly 0, and P(00)/P(11)
    # should each land near 50%.
    counts = run_local_simulation(0.0)
    total = sum(counts.values())

    assert counts.get("01", 0) == 0
    assert counts.get("10", 0) == 0

    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total
    assert p00 == pytest.approx(0.5, abs=0.1)
    assert p11 == pytest.approx(0.5, abs=0.1)


def test_pi_deliberation_flips_to_full_disagreement():
    # theta=pi: RY(pi) on Mind A flips the Bell state to the anti-correlated
    # (|01> - |10>)/sqrt(2) branch — P(00)=P(11) should be exactly 0, and
    # P(01)/P(10) should each land near 50%.
    import numpy as np

    counts = run_local_simulation(np.pi)
    total = sum(counts.values())

    assert counts.get("00", 0) == 0
    assert counts.get("11", 0) == 0

    p01 = counts.get("01", 0) / total
    p10 = counts.get("10", 0) / total
    assert p01 == pytest.approx(0.5, abs=0.1)
    assert p10 == pytest.approx(0.5, abs=0.1)


def test_counts_total_matches_shot_count():
    counts = run_local_simulation(0.7854)
    assert sum(counts.values()) == 1024
