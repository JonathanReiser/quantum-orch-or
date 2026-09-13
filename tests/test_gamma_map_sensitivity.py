import numpy as np

from tools.gamma_map_sensitivity import (
    coherence_at_gamma_t_2,
    coherence_half_life,
    continuous_summary,
)


def test_positive_gamma_metrics_are_not_censored_by_wall_clock_window():
    assert np.isclose(coherence_half_life(0.1), 2.0 * np.log(2.0) / 0.1)
    assert coherence_half_life(0.1) > 10.0
    assert np.isclose(coherence_at_gamma_t_2(0.1), np.exp(-1.0))


def test_dimensionless_metrics_are_undefined_only_at_zero_rate():
    assert coherence_half_life(0.0) is None
    assert coherence_at_gamma_t_2(0.0) is None


def test_signed_summary_does_not_report_a_multiplicative_range():
    summary = continuous_summary([-0.1, 0.2])
    assert summary["n_negative"] == 1
    assert summary["n_positive"] == 1
    assert "max_over_min" not in summary
