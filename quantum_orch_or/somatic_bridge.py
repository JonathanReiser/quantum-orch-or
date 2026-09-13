"""Motion-aware HRV features for research simulations.

``gamma`` is a declared model parameter, not a diagnosis. Never put raw
identifiers or biometric samples on-chain.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class WearableWindow:
    timestamp_s: float
    rr_intervals_ms: tuple[float, ...]
    accel_xyz_g: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class SomaticEstimate:
    timestamp_s: float
    rmssd_ms: float | None
    baseline_rmssd_ms: float | None
    variability_drop: float | None
    gamma_per_s: float | None
    motion_rms_g: float
    excluded_for_motion: bool
    quality_ok: bool


@dataclass(frozen=True)
class BridgeConfig:
    motion_rms_threshold_g: float = 0.12
    min_rr_count: int = 20
    rr_min_ms: float = 300.0
    rr_max_ms: float = 2_000.0
    baseline_windows: int = 5
    gamma_floor_per_s: float = 0.02
    gamma_scale_per_s: float = 0.80
    gamma_ceiling_per_s: float = 1.00


def rmssd_ms(rr_intervals_ms: Sequence[float]) -> float:
    rr = np.asarray(rr_intervals_ms, dtype=float)
    if rr.ndim != 1 or rr.size < 2 or not np.all(np.isfinite(rr)):
        raise ValueError("rr_intervals_ms must contain at least two finite values")
    return float(np.sqrt(np.mean(np.diff(rr) ** 2)))


def motion_rms_g(accel_xyz_g: Sequence[Sequence[float]]) -> float:
    accel = np.asarray(accel_xyz_g, dtype=float)
    if accel.ndim != 2 or accel.shape[1] != 3 or accel.shape[0] < 2:
        raise ValueError("accel_xyz_g must have shape (n, 3), n >= 2")
    dynamic = accel - accel.mean(axis=0, keepdims=True)
    return float(np.sqrt(np.mean(np.sum(dynamic**2, axis=1))))


class SomaticBridge:
    """Build a resting-window baseline and map fractional RMSSD loss to gamma."""

    def __init__(self, config: BridgeConfig = BridgeConfig()) -> None:
        self.config = config
        self._resting_rmssd: list[float] = []

    def process(self, window: WearableWindow) -> SomaticEstimate:
        cfg = self.config
        motion = motion_rms_g(window.accel_xyz_g)
        excluded = motion > cfg.motion_rms_threshold_g
        rr = np.asarray(window.rr_intervals_ms, dtype=float)
        quality = bool(
            rr.size >= cfg.min_rr_count
            and np.all(np.isfinite(rr))
            and np.all((rr >= cfg.rr_min_ms) & (rr <= cfg.rr_max_ms))
        )
        baseline = (
            float(np.median(self._resting_rmssd[-cfg.baseline_windows :]))
            if len(self._resting_rmssd) >= cfg.baseline_windows
            else None
        )
        if excluded or not quality:
            return SomaticEstimate(window.timestamp_s, None, baseline, None, None, motion, excluded, quality)

        current = rmssd_ms(rr)
        if baseline is None:
            self._resting_rmssd.append(current)
            return SomaticEstimate(window.timestamp_s, current, None, None, None, motion, False, True)

        drop = float(np.clip((baseline - current) / max(baseline, 1e-9), 0.0, 1.0))
        gamma = float(np.clip(
            cfg.gamma_floor_per_s + cfg.gamma_scale_per_s * drop,
            cfg.gamma_floor_per_s,
            cfg.gamma_ceiling_per_s,
        ))
        return SomaticEstimate(window.timestamp_s, current, baseline, drop, gamma, motion, False, True)


def canonical_commitment(payload: dict, salt_hex: str) -> str:
    """Create a salted SHA-256 commitment; retain payload and salt off-chain."""
    salt = bytes.fromhex(salt_hex)
    if len(salt) < 16:
        raise ValueError("salt must contain at least 16 random bytes")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return "0x" + hashlib.sha256(salt + encoded).hexdigest()

