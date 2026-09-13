import numpy as np
import pytest

from quantum_orch_or.cognitive_lindblad import simulate
from tools.gamma_map_sensitivity import (
    THERMAL,
    coherence_at_gamma_t_2,
    coherence_half_life,
    continuous_summary,
    dimensionless_trajectory,
)

GAMMAS = (0.05, 0.37, 0.82, 3.20)


def test_positive_gamma_metrics_are_not_censored_by_wall_clock_window():
    # 2 ln 2 / 0.1 = 13.86 s, well beyond the 10 s window Q1 and Q5 use.
    assert coherence_half_life(0.1) == pytest.approx(2.0 * np.log(2.0) / 0.1, rel=1e-6)
    assert coherence_half_life(0.1) > 10.0
    assert coherence_at_gamma_t_2(0.1) == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_dimensionless_metrics_are_undefined_only_at_zero_rate():
    assert coherence_half_life(0.0) is None
    assert coherence_at_gamma_t_2(0.0) is None
    assert dimensionless_trajectory(0.0) is None


def test_signed_summary_does_not_report_a_multiplicative_range():
    summary = continuous_summary([-0.1, 0.2])
    assert summary["n_negative"] == 1
    assert summary["n_positive"] == 1
    assert "max_over_min" not in summary


# --- the study's formulas must track the module, not merely restate themselves ---


@pytest.mark.parametrize("gamma", GAMMAS)
def test_coherence_decays_at_half_gamma_in_the_module(gamma):
    """Fails if the dissipator strengths change: Q2's 2ln2/gamma would be wrong."""
    tr = simulate(gamma, duration_s=6.0 / gamma, samples=2001,
                  thermal_excited_fraction=THERMAL, mindfulness_at_s=None)
    expected = tr.coherence_l1[0] * np.exp(-gamma * tr.time_s / 2.0)
    assert np.max(np.abs(tr.coherence_l1 - expected)) < 1e-8


@pytest.mark.parametrize("gamma", GAMMAS)
def test_measured_half_life_matches_the_closed_form(gamma):
    assert coherence_half_life(gamma) == pytest.approx(2.0 * np.log(2.0) / gamma, rel=1e-6)


@pytest.mark.parametrize("gamma", GAMMAS)
def test_measured_q4_equals_exp_minus_one(gamma):
    """Q4 is a measurement; exp(-1) is the prediction it is checked against."""
    assert coherence_at_gamma_t_2(gamma) == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_steady_excited_population_equals_thermal_fraction():
    """Fails if the up/down dissipator balance changes."""
    for p_th in (0.05, 0.10, 0.35):
        tr = simulate(1.0, duration_s=60.0, samples=2001,
                      thermal_excited_fraction=p_th, mindfulness_at_s=None)
        assert tr.p_choice_1[-1] == pytest.approx(p_th, abs=1e-9)


def test_generator_depends_on_gamma_and_time_only_through_their_product():
    """Fails if a Hamiltonian is introduced: scale would stop being a time
    reparameterization, which is the study's central structural claim."""
    tau = np.linspace(0.0, 2.0, 50)
    reference = None
    for gamma in GAMMAS:
        tr = simulate(gamma, duration_s=6.0 / gamma, samples=2001,
                      thermal_excited_fraction=THERMAL, mindfulness_at_s=None)
        coherence = np.interp(tau / gamma, tr.time_s, tr.coherence_l1)
        population = np.interp(tau / gamma, tr.time_s, tr.p_choice_1)
        if reference is None:
            reference = (coherence, population)
            continue
        assert np.max(np.abs(coherence - reference[0])) < 1e-8
        assert np.max(np.abs(population - reference[1])) < 1e-7


def test_full_density_matrix_scales_with_gamma_times_time():
    """The pre-registered structural claim is about the generator, not only the
    two reported observables. A diagonal Hamiltonian leaves |rho01| and the
    populations untouched while winding a gamma-independent phase, so it is
    invisible to the observable-level check above but breaks scale covariance
    of the dynamics. Compare the density matrices themselves."""
    tau = np.linspace(0.0, 2.0, 40)
    reference = None
    for gamma in GAMMAS:
        tr = simulate(gamma, duration_s=6.0 / gamma, samples=2001,
                      thermal_excited_fraction=THERMAL, mindfulness_at_s=None)
        rho = np.stack([
            np.array([np.interp(tau / gamma, tr.time_s, tr.density_matrices[:, i, j])
                      for j in range(2)]) for i in range(2)])
        if reference is None:
            reference = rho
            continue
        assert np.max(np.abs(rho - reference)) < 1e-7
