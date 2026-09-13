"""Canonicalisation must erase cross-platform float noise and nothing else."""

import json
import math
import random

import pytest

from q_ai_governance.canonical_json import (
    MEASURED_NOISE_FLOOR_REL,
    SIGNIFICANT_DIGITS,
    canonicalise,
    round_significant,
)

COMMITTED = ("data/benchmark_classical_results.json",
             "data/benchmark_contestedness_results.json")


def _floats(obj, acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for v in obj.values():
            _floats(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _floats(v, acc)
    elif isinstance(obj, float):
        acc.append(obj)
    return acc


def _committed_floats():
    out = []
    for path in COMMITTED:
        out.extend(_floats(json.load(open(path))))
    return out


# --- insignificant differences canonicalise away -----------------------------


def test_noise_floor_perturbations_canonicalise_identically():
    """Every committed value, perturbed at the measured cross-platform noise
    floor, must round to the same thing. This is the property the ledger's byte
    comparison depends on."""
    rng = random.Random(20260913)
    values = _committed_floats()
    assert len(values) > 500, "expected the full committed float population"
    for value in values:
        for _ in range(20):
            perturbed = value * (1.0 + rng.uniform(-MEASURED_NOISE_FLOOR_REL,
                                                   MEASURED_NOISE_FLOOR_REL))
            assert round_significant(value) == round_significant(perturbed), (
                f"{value!r} and {perturbed!r} disagree after canonicalisation")


def test_one_ulp_differences_canonicalise_identically():
    for value in (0.012863197394856307, 97.4197554900778, 0.65964, 0.001):
        assert round_significant(value) == round_significant(math.nextafter(value, math.inf))
        assert round_significant(value) == round_significant(math.nextafter(value, -math.inf))


def test_the_observed_worst_case_disagreement_canonicalises_away():
    """The real three-platform values for results.ridge_prevote_features.r2,
    which had the worst relative spread measured (9.494e-14)."""
    observed = (0.012863197394856307, 0.012863197394857528, 0.01286319739485653)
    canonical = {round_significant(v) for v in observed}
    assert len(canonical) == 1, canonical


# --- meaningful differences survive ------------------------------------------


def test_differences_that_matter_are_preserved():
    """A change large enough to alter any published three-decimal claim must
    NOT be canonicalised away."""
    cases = [
        (0.65964, 0.66064),      # AUC would print 0.660 vs 0.661
        (10.438801, 10.448801),  # MAE would print 10.44 vs 10.45
        (-0.124770, -0.125770),  # R^2 would print -0.125 vs -0.126
        (0.001, 0.0011),         # p would print 0.0010 vs 0.0011
        (0.416, 0.417),          # within-DAO AUC
    ]
    for a, b in cases:
        assert round_significant(a) != round_significant(b), (a, b)


def test_a_difference_just_above_the_rounding_step_is_preserved():
    base = 1.0
    assert round_significant(base) != round_significant(base * (1 + 1e-5))


@pytest.mark.parametrize("digits", [SIGNIFICANT_DIGITS])
def test_significant_digits_sit_far_above_the_noise_floor(digits):
    """The margin argument in canonical_json.py, as an executable check: the
    relative rounding step must exceed the measured noise by >= 1e6."""
    coarsest_step = 10.0 ** -(digits)      # worst case within a decade
    assert coarsest_step / MEASURED_NOISE_FLOOR_REL >= 1e6


# --- structure and exactness --------------------------------------------------


def test_integers_and_bools_are_untouched():
    payload = {"n": 861, "n_train": 602, "ok": True, "off": False}
    assert canonicalise(payload) == payload
    assert isinstance(canonicalise(payload)["n"], int)
    assert canonicalise(payload)["ok"] is True


def test_negative_zero_is_normalised():
    assert math.copysign(1.0, canonicalise(-0.0)) == 1.0
    assert json.dumps(canonicalise({"x": -0.0})) == '{"x": 0.0}'


def test_nested_structure_is_preserved():
    payload = {"a": [1, 2.5000000001, {"b": (3, 4.0)}], "c": "text", "d": None}
    out = canonicalise(payload)
    assert out["c"] == "text" and out["d"] is None
    assert out["a"][0] == 1
    assert isinstance(out["a"][2]["b"], list)


def test_canonicalisation_is_idempotent():
    for path in COMMITTED:
        data = json.load(open(path))
        assert canonicalise(canonicalise(data)) == canonicalise(data)


def test_committed_artifacts_are_already_canonical():
    """The files on disk must be fixed points, or the ledger hash would change
    the next time anything regenerates them."""
    for path in COMMITTED:
        data = json.load(open(path))
        assert canonicalise(data) == data, f"{path} is not canonical"


def test_published_claims_survive_canonicalisation():
    classical = json.load(open("data/benchmark_classical_results.json"))
    contested = json.load(open("data/benchmark_contestedness_results.json"))
    median = classical["results"]["constant_train_median"]
    ridge = classical["results"]["ridge_prevote_features"]
    logistic = contested["results"]["logistic_all_features"]
    assert f"{median['mae_pp']:.2f}" == "10.44"
    assert f"{median['rmse_pp']:.2f}" == "26.73"
    assert f"{median['r2']:.3f}" == "-0.125"
    assert f"{ridge['mae_pp']:.2f}" == "11.20"
    assert f"{ridge['rmse_pp']:.2f}" == "25.04"
    assert f"{logistic['auc']:.3f}" == "0.660"
    assert f"{logistic['auc_ci95'][0]:.3f}" == "0.555"
    assert f"{logistic['auc_ci95'][1]:.3f}" == "0.763"
    assert f"{logistic['auc_p_gt_0.5']:.4f}" == "0.0010"
