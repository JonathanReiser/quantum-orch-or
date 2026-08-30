import math

import pytest

from q_ai_governance.ewl_tournament import (
    TournamentConfig,
    classical_distribution,
    ewl_distribution,
    run_condition,
    run_tournament,
)


def test_ewl_preserves_classical_actions_at_zero_entanglement():
    assert ewl_distribution("D", "C", entanglement=0.0) == classical_distribution("D", "C")


def test_matched_classical_control_and_ewl_have_identical_replay_records():
    correlated = run_condition(TournamentConfig("classical-correlated", "Q", "D", math.pi / 2, 25, 9))
    ewl = run_condition(TournamentConfig("ewl-simulator", "Q", "D", math.pi / 2, 25, 9))

    assert correlated["probabilities"] == ewl["probabilities"]
    assert correlated["events"] == ewl["events"]
    assert correlated["replay_hash"] != ewl["replay_hash"]


def test_classical_condition_does_not_hide_quantum_strategy_as_classical():
    with pytest.raises(ValueError, match="permits C and D only"):
        run_condition(TournamentConfig("classical", "Q", "D"))


def test_hardware_adapter_is_not_presented_as_a_result():
    report = run_condition(TournamentConfig("hardware-adapter", "Q", "Q"))

    assert report["status"] == "not-executed"
    assert "job_id" in report["required_fields_before_analysis"]
    assert "measurements" not in report


def test_tournament_exposes_control_invariant():
    report = run_tournament(player_1="C", player_2="D", rounds=10, seed=1)

    assert report["control_checks"]["matched_probability_distribution"] is True
    assert report["control_checks"]["matched_sampled_event_sequence"] is True
