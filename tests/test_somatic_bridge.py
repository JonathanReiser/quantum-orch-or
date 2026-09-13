import numpy as np
import pytest

from quantum_orch_or.somatic_bridge import BridgeConfig, SomaticBridge, WearableWindow, canonical_commitment, rmssd_ms


def window(spread: float, motion: float = 0.01) -> WearableWindow:
    rr = tuple(np.resize(np.array([800 - spread, 800 + spread]), 32))
    accel = tuple(map(tuple, np.column_stack((np.resize([-motion, motion], 50), np.zeros(50), np.ones(50)))))
    return WearableWindow(0, rr, accel)


def test_rmssd_known_sequence():
    assert rmssd_ms([800, 810, 800]) == pytest.approx(10.0)


def test_lower_hrv_increases_gamma_after_baseline():
    bridge = SomaticBridge(BridgeConfig(baseline_windows=3))
    for _ in range(3):
        assert bridge.process(window(30)).gamma_per_s is None
    estimate = bridge.process(window(8))
    assert estimate.variability_drop > 0.6
    assert estimate.gamma_per_s > 0.5


def test_motion_window_is_excluded():
    bridge = SomaticBridge(BridgeConfig(baseline_windows=1, motion_rms_threshold_g=0.1))
    bridge.process(window(30))
    estimate = bridge.process(window(8, motion=0.3))
    assert estimate.excluded_for_motion and estimate.gamma_per_s is None


def test_commitment_is_salted():
    payload = {"baseline_rmssd_ms": 42.0, "schema": 1}
    assert canonical_commitment(payload, "00" * 16) != canonical_commitment(payload, "01" * 16)

