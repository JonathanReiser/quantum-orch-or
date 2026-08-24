"""
Tests for quantum_orch_or/lottery.py — the commit-reveal + quantum-beacon
verifiable lottery. Covers the commitment scheme, the unbiased index
sampler, a full run_lottery/verify_draw round trip, and that verify_draw
actually catches tampering (a swapped winner, a forged reveal, an
altered entry list, and a spoofed quantum bitstring).
"""
import copy

import pytest

from quantum_orch_or.lottery import (
    Participant,
    QuantumBeaconResult,
    draw_quantum_entropy,
    generate_secret,
    make_commitment,
    run_lottery,
    verify_draw,
    _unbiased_index,
)


def test_make_commitment_is_deterministic():
    secret = b"a fixed secret"
    assert make_commitment(secret) == make_commitment(secret)


def test_make_commitment_differs_for_different_secrets():
    assert make_commitment(b"secret-a") != make_commitment(b"secret-b")


def test_participant_commitment_matches_make_commitment():
    secret = generate_secret()
    p = Participant(entry_id="alice", secret=secret)
    assert p.commitment == make_commitment(secret)


def test_generate_secret_returns_32_random_bytes():
    a, b = generate_secret(), generate_secret()
    assert isinstance(a, bytes) and len(a) == 32
    assert a != b  # astronomically unlikely to collide


def test_draw_quantum_entropy_returns_valid_bitstring():
    result = draw_quantum_entropy(num_qubits=8)
    assert isinstance(result, QuantumBeaconResult)
    assert len(result.bitstring) == 8
    assert set(result.bitstring) <= {"0", "1"}


def test_unbiased_index_is_deterministic_given_same_inputs():
    seed = b"\x00" * 32
    assert _unbiased_index(seed, upper=7, salt=0) == _unbiased_index(seed, upper=7, salt=0)


def test_unbiased_index_stays_in_range():
    seed = b"\x01" * 32
    for upper in [1, 2, 5, 7, 100, 257]:
        idx = _unbiased_index(seed, upper=upper, salt=0)
        assert 0 <= idx < upper


def test_unbiased_index_rejects_non_positive_upper():
    with pytest.raises(ValueError):
        _unbiased_index(b"\x00" * 32, upper=0, salt=0)


def _make_participants(names):
    return [Participant(entry_id=name, secret=generate_secret()) for name in names]


def test_run_lottery_picks_requested_number_of_distinct_winners():
    participants = _make_participants(["alice", "bob", "carol", "dave"])
    result = run_lottery(participants, num_winners=2, num_qubits=8)
    assert len(result.winners) == 2
    assert len(set(result.winners)) == 2
    assert set(result.winners) <= set(result.entries)


def test_run_lottery_rejects_duplicate_entry_ids():
    participants = _make_participants(["alice", "alice"])
    with pytest.raises(ValueError):
        run_lottery(participants, num_winners=1)


@pytest.mark.parametrize("num_winners", [0, 5])
def test_run_lottery_rejects_invalid_num_winners(num_winners):
    participants = _make_participants(["alice", "bob", "carol"])
    with pytest.raises(ValueError):
        run_lottery(participants, num_winners=num_winners)


def test_verify_draw_accepts_an_untampered_result():
    participants = _make_participants(["alice", "bob", "carol", "dave", "erin"])
    result = run_lottery(participants, num_winners=2, num_qubits=8)
    assert verify_draw(result) is True


def test_verify_draw_rejects_a_swapped_winner():
    participants = _make_participants(["alice", "bob", "carol", "dave"])
    result = run_lottery(participants, num_winners=1, num_qubits=8)
    tampered = copy.deepcopy(result)
    non_winner = next(e for e in tampered.entries if e not in tampered.winners)
    tampered.winners[0] = non_winner
    assert verify_draw(tampered) is False


def test_verify_draw_rejects_a_forged_reveal():
    participants = _make_participants(["alice", "bob", "carol"])
    result = run_lottery(participants, num_winners=1, num_qubits=8)
    tampered = copy.deepcopy(result)
    victim = tampered.entries[0]
    tampered.reveals[victim] = generate_secret().hex()  # doesn't hash to the published commitment
    assert verify_draw(tampered) is False


def test_verify_draw_rejects_an_altered_entry_list():
    participants = _make_participants(["alice", "bob", "carol"])
    result = run_lottery(participants, num_winners=1, num_qubits=8)
    tampered = copy.deepcopy(result)
    tampered.entries.append("mallory")  # ballot-stuffed after the fact
    assert verify_draw(tampered) is False


def test_verify_draw_rejects_a_spoofed_quantum_bitstring():
    participants = _make_participants(["alice", "bob", "carol"])
    result = run_lottery(participants, num_winners=1, num_qubits=8)
    tampered = copy.deepcopy(result)
    flipped = "".join("1" if c == "0" else "0" for c in tampered.quantum.bitstring)
    tampered.quantum.bitstring = flipped
    assert verify_draw(tampered) is False
