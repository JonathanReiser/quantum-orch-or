"""
Tests for the narrow-band contestedness benchmark.

Every test here must be able to FAIL. This repo has a history of assertions that
could not (tests/test_quantum_economics.py:19 asserts `abs(x) >= 0.0`), so each
test below pins something a plausible future edit would actually break, and the
mutation that breaks it is named in the docstring.
"""

import json
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q_ai_governance import benchmark_narrow_contestedness as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "benchmark_narrow_contestedness_results.json")


# ---- the locked band --------------------------------------------------------
def test_contested_band_is_exactly_40_60():
    """Fails if anyone widens the band to rescue a weak result.

    The pre-registration locks [40, 60]. Widening to [5, 95] would raise
    prevalence from ~4% to ~26% and make every metric look better, which is
    exactly why this is pinned.
    """
    assert (B.CONTESTED_LO, B.CONTESTED_HI) == (40.0, 60.0)


def test_preregistered_constants_unchanged():
    """Fails if the filters, split, or seed drift from the pre-registration."""
    assert B.MIN_VOTERS == 100
    assert B.MIN_USABLE_N == 150
    assert B.TEST_FRAC == 0.30
    assert B.SEED == 20260904
    assert B.N_BOOTSTRAP >= 1000      # the brief's floor


# ---- metrics behave, including where they are allowed to look bad -----------
def test_auc_spans_the_full_range():
    """Fails if AUC is clamped. A perfectly WRONG ranking must report 0.0."""
    y = np.array([0, 0, 1, 1])
    assert B.auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == 1.0
    assert B.auc(y, np.array([0.9, 0.8, 0.2, 0.1])) == 0.0     # not floored
    assert B.auc(y, np.array([0.5, 0.5, 0.5, 0.5])) == 0.5     # ties -> chance


def test_auc_below_half_is_reported_not_floored():
    """Fails if someone adds max(0.5, auc) 'for readability'.

    benchmark_real_dao_data.py:128 does exactly this shape of thing to R^2.
    """
    y = np.array([0, 0, 0, 1, 1])
    bad = B.auc(y, np.array([0.9, 0.8, 0.7, 0.2, 0.1]))
    assert bad < 0.5 and bad == 0.0


def test_average_precision_of_constant_scorer_equals_prevalence():
    """Fails if tied scores inherit array order instead of sharing a precision.

    This is a regression test for a real bug: without tied-block handling a
    constant scorer reported 0.199 on the test set -- an artefact of the rows
    being in time order -- instead of the 0.042 prevalence.
    """
    for prev_n, n in [(1, 10), (2, 10), (3, 12)]:
        y = np.array([1.0] * prev_n + [0.0] * (n - prev_n))
        np.random.default_rng(0).shuffle(y)
        got = B.average_precision(y, np.zeros(n))
        assert got == pytest.approx(y.mean()), f"{got} != {y.mean()}"


def test_average_precision_perfect_and_ordering():
    """Fails if AP stops rewarding a correct ranking."""
    y = np.array([1.0, 1.0, 0.0, 0.0, 0.0])
    assert B.average_precision(y, np.array([9.0, 8.0, 3.0, 2.0, 1.0])) == 1.0
    worst = B.average_precision(y, np.array([1.0, 2.0, 3.0, 8.0, 9.0]))
    assert worst < y.mean()


# ---- the split really is temporal ------------------------------------------
def test_temporal_split_does_not_leak_the_future():
    """Fails if the split becomes random, which would inflate every metric.

    The brief's Step 3: a random split leaks future information into the past.
    """
    payload, kept, _ = B.load_and_filter("data/snapshot_dao_dataset.json")
    X, y, meta = B.build_features(kept)
    cut = int(len(y) * (1 - B.TEST_FRAC))
    max_train_end = max(m["end"] for m in meta[:cut])
    min_test_end = min(m["end"] for m in meta[cut:])
    assert max_train_end <= min_test_end, (
        f"train contains a proposal ending at {max_train_end}, after the "
        f"earliest test proposal at {min_test_end} -- the split is not temporal")


def test_features_are_strictly_past_only():
    """Fails if a prior starts including the row's own outcome.

    Checked structurally: the first proposal of each DAO must carry the neutral
    defaults, because it has no history to average over.
    """
    payload, kept, _ = B.load_and_filter("data/snapshot_dao_dataset.json")
    X, y, meta = B.build_features(kept)
    i_yes = B.FEATURE_NAMES.index("prior_dao_yes")
    i_n = B.FEATURE_NAMES.index("log_prior_dao_n")
    seen = set()
    checked = 0
    for row, m in zip(X, meta):
        if m["dao"] in seen:
            continue
        seen.add(m["dao"])
        assert row[i_n] == 0.0, f"{m['dao']} first proposal claims prior history"
        assert row[i_yes] == pytest.approx(0.84), (
            f"{m['dao']} first proposal has a fitted prior, not the neutral default")
        checked += 1
    assert checked == len(B.DAOS)


def test_binary_ish_filter_rejects_multi_option():
    """Fails if non-binary proposals leak in, where YES share is undefined."""
    assert B.is_binary_ish({"choices": ["For", "Against", "Abstain"]})
    assert B.is_binary_ish({"choices": ["Yes", "No"]})
    assert not B.is_binary_ish({"choices": ["A", "B", "C"]})
    assert not B.is_binary_ish({"choices": ["For", "Against", "Abstain", "Veto"]})
    assert not B.is_binary_ish({"choices": ["Option 1", "Option 2"]})


# ---- the engine properties the pre-registration relies on -------------------
def test_engine_is_deterministic_given_an_observation():
    """Fails if the engine gains real per-rollout stochasticity.

    The pre-registration states that coherence_at_collapse and the step count
    are deterministic, so score (c) is a fixed feature map rather than an
    uncertainty estimate. If that stops being true, the interpretation in
    NARROW_CONTESTEDNESS.md is wrong and must be rewritten.
    """
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
    np.random.seed(B.SEED)
    agent = QuantumOrchORAgent(num_qubits=4, state_dim=2)
    obs = np.array([1.0, -2.0], dtype=np.float32)
    out = [agent.deliberate_and_act(obs) for _ in range(12)]
    assert len({o[1] for o in out}) == 1, "step count varies across rollouts"
    assert np.std([o[2] for o in out]) < 1e-12, "coherence varies across rollouts"


def test_initial_circuit_has_no_entangling_gates():
    """Fails if entangling gates are added -- which would be an improvement, and
    would invalidate the 'product state' claim in the pre-registration."""
    from q_ai_governance.quantum_agent import QuantumOrchORAgent
    np.random.seed(B.SEED)
    agent = QuantumOrchORAgent(num_qubits=4, state_dim=2)
    rot, _, _ = agent._compute_circuit_params(np.zeros(2, dtype=np.float32))
    ops = agent._build_initial_circuit(rot).count_ops()
    assert sum(c for n, c in ops.items() if n in ("cx", "cz", "rzz", "swap")) == 0


# ---- the committed results file --------------------------------------------
@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_results_file_is_internally_consistent():
    """Fails if the JSON's verdict stops matching its own numbers.

    Guards against a headline being edited without the metrics behind it.
    """
    r = json.load(open(RESULTS))
    assert r["config"]["contested_band_yes_pct"] == [40.0, 60.0]
    assert r["auc_null"] == 0.5
    c = r["counts"]
    assert c["n_train"] + c["n_test"] == c["n_kept"]
    assert c["n_kept"] >= r["config"]["min_usable_n"]
    for k, v in r["verdict"].items():
        res = r["results"][k]
        assert v["ci_lower_above_half"] == (res["ci95"]["lo"] > 0.5)
        assert v["beats_logistic"] == (res["auc"] > r["results"]["logistic"]["auc"])
        assert v["PASSES_PREREGISTERED_CRITERION"] == (
            v["ci_lower_above_half"] and v["beats_logistic"])


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_pr_auc_is_reported_against_prevalence_not_half():
    """Fails if PR-AUC's null is ever recorded as 0.5.

    At ~4% prevalence a PR-AUC of 0.2 is good and 0.5 would be extraordinary;
    reading it against 0.5 inverts the conclusion.
    """
    r = json.load(open(RESULTS))
    prev = r["counts"]["prevalence_test"]
    assert prev < 0.10
    for name, res in r["results"].items():
        assert res["pr_auc_null_prevalence"] == pytest.approx(prev)


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_no_metric_is_clamped():
    """Fails if any reported metric sits suspiciously on a clamp boundary."""
    r = json.load(open(RESULTS))
    for name, res in r["results"].items():
        assert 0.0 <= res["auc"] <= 1.0
        assert res["auc"] not in (0.98,), f"{name} AUC pinned at a clamp value"
        assert not math.isnan(res["auc"]), f"{name} AUC is NaN"


# ---- the headline numbers, pinned ------------------------------------------
@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_all_three_quantum_scores_fail_the_criterion():
    """Fails if a future change turns the negative result positive without the
    pre-registration being revisited.

    This is the finding. All three score functions miss the criterion, and the
    reason is not that a classical model beat them -- the logistic baseline
    misses chance too.
    """
    r = json.load(open(RESULTS))
    for k in ("quantum_point", "quantum_dispersion", "quantum_coherence"):
        assert r["verdict"][k]["PASSES_PREREGISTERED_CRITERION"] is False


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_logistic_baseline_also_fails_to_clear_chance():
    """Fails if the write-up's central caveat stops being true.

    NARROW_CONTESTEDNESS.md says the honest reading is 'nothing resolves at this
    band', not 'classical beat quantum'. That rests on the logistic CI covering
    0.5. If it ever stops covering 0.5 the prose is wrong and must change.
    """
    r = json.load(open(RESULTS))
    ci = r["results"]["logistic"]["ci95"]
    assert ci["lo"] < 0.5 < ci["hi"], (
        f"logistic CI {ci} no longer covers chance -- the write-up's framing is stale")


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_seed_spread_is_wide_enough_to_have_faked_a_result():
    """Fails if the seed-sensitivity argument stops holding.

    The pre-registered 10-seed check exists because one seed could manufacture a
    headline. It did: across seeds the AUCs span roughly 0.17 to 0.78, and 4 of
    10 land above chance for every score function.
    """
    r = json.load(open(RESULTS))
    for k in ("quantum_point", "quantum_dispersion", "quantum_coherence"):
        a = np.array(r["results"][k]["auc_per_seed"])
        assert len(a) == 10
        assert a.max() - a.min() > 0.3, f"{k} seed spread collapsed to {a.ptp():.3f}"
        assert a.max() > 0.5, f"{k} never exceeds chance on any seed"
        assert a.min() < 0.5


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_test_set_positive_count_is_small_and_said_so():
    """Fails if n_contested_test grows without the instability caveat being
    reconsidered. Nine positives is the binding constraint on everything."""
    r = json.load(open(RESULTS))
    assert r["counts"]["n_contested_test"] == 9
    assert r["counts"]["n_test"] == 214


@pytest.mark.skipif(not os.path.exists(RESULTS), reason="benchmark not yet run")
def test_trivial_baseline_is_accurate_and_worthless():
    """Fails if the accuracy-is-useless demonstration stops working.

    Always predicting 'not contested' scores 1 - prevalence = 95.8% accuracy
    while carrying an AUC of exactly 0.5 and a PR-AUC of exactly the prevalence.
    """
    r = json.load(open(RESULTS))
    t = r["results"]["trivial_constant"]
    prev = r["counts"]["prevalence_test"]
    assert t["auc"] == 0.5
    assert t["pr_auc"] == pytest.approx(prev), "constant scorer must score prevalence"
    assert (1.0 - prev) > 0.95


SENS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "sensitivity_yes_share_definition.json")


@pytest.mark.skipif(not os.path.exists(SENS), reason="sensitivity not yet run")
def test_sensitivity_rederives_the_primary_exactly():
    """Fails if the raw-scores file stops reproducing the committed primary run.

    The whole point of persisting raw scores is that re-analysis needs no second
    multi-hour engine pass. That is only safe while the re-derivation is exact.
    """
    s = json.load(open(SENS))
    assert s["rederivation_max_auc_drift_vs_committed_primary"] == 0.0


@pytest.mark.skipif(not os.path.exists(SENS), reason="sensitivity not yet run")
def test_conclusion_survives_the_other_yes_share_definition():
    """Fails if the negative result stops holding under the abstain-excluding
    denominator -- in which case the answer depends on a definition the brief
    and the dataset disagreed about, and that must be said loudly."""
    s = json.load(open(SENS))
    assert s["not_preregistered"] is True
    for k in ("quantum_point", "quantum_dispersion", "quantum_coherence"):
        b = s["results_B_sensitivity"][k]
        assert b["ci95"]["lo"] < 0.5, f"{k} clears chance under definition B"
    assert s["n_contested_test"]["B_sensitivity"] == 3
