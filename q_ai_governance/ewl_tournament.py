"""Auditable controls for a mechanism-blind EWL game tournament.

This module is deliberately small and uses only NumPy.  It distinguishes a
quantum *calculation* from a claim about player cognition: the ``ewl-simulator``
and ``classical-correlated`` conditions share the same outcome distribution.
The latter samples that distribution with ordinary pseudorandomness.  Any
difference in a future human study therefore cannot be credited to the
probability distribution alone.

``hardware-adapter`` is a protocol record, not a pretend hardware result.  It
does not submit jobs or synthesize measurements without an explicit backend
integration and credentials.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Dict, Iterable, List, Mapping, Sequence

import numpy as np


OUTCOMES: Sequence[str] = ("CC", "CD", "DC", "DD")
PAYOFFS: Mapping[str, Sequence[float]] = {
    "CC": (3.0, 3.0),
    "CD": (0.0, 5.0),
    "DC": (5.0, 0.0),
    "DD": (1.0, 1.0),
}
CLASSICAL_ACTIONS = frozenset(("C", "D"))
EWL_ACTIONS = frozenset(("C", "D", "Q"))

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Q = np.array([[1j, 0], [0, -1j]], dtype=complex)
_STRATEGIES: Mapping[str, np.ndarray] = {"C": _I, "D": _X, "Q": _Q}
_I4 = np.eye(4, dtype=complex)
_XX = np.kron(_X, _X)


@dataclass(frozen=True)
class TournamentConfig:
    """A fully recorded treatment configuration."""

    condition: str
    player_1: str = "C"
    player_2: str = "D"
    entanglement: float = math.pi / 2
    rounds: int = 100
    seed: int = 0

    def validate(self) -> None:
        if self.condition not in {
            "classical",
            "classical-correlated",
            "ewl-simulator",
            "hardware-adapter",
        }:
            raise ValueError(f"Unknown tournament condition: {self.condition}")
        if self.player_1 not in EWL_ACTIONS or self.player_2 not in EWL_ACTIONS:
            raise ValueError("Strategies must be one of C, D, or Q.")
        if self.condition == "classical" and (
            self.player_1 not in CLASSICAL_ACTIONS or self.player_2 not in CLASSICAL_ACTIONS
        ):
            raise ValueError("The classical condition permits C and D only; Q is an EWL strategy.")
        if not 0.0 <= self.entanglement <= math.pi / 2:
            raise ValueError("entanglement must be between 0 and pi/2.")
        if self.rounds < 1:
            raise ValueError("rounds must be at least 1.")


def ewl_distribution(player_1: str, player_2: str, entanglement: float = math.pi / 2) -> Dict[str, float]:
    """Return exact EWL outcome probabilities for the documented strategy set.

    Qubit zero is Player 1, so the local operation has the tensor order
    ``U_player_2 ⊗ U_player_1`` in NumPy's conventional basis ordering.
    """
    config = TournamentConfig("ewl-simulator", player_1, player_2, entanglement)
    config.validate()
    entangler = math.cos(entanglement / 2) * _I4 + 1j * math.sin(entanglement / 2) * _XX
    state = entangler @ np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    local_operations = np.kron(_STRATEGIES[player_2], _STRATEGIES[player_1])
    final_state = entangler.conj().T @ local_operations @ state
    basis_probabilities = np.abs(final_state) ** 2
    # NumPy basis order is 00, 01(DC), 10(CD), 11; public outcome order is CC, CD, DC, DD.
    probabilities = {
        "CC": float(basis_probabilities[0]),
        "CD": float(basis_probabilities[2]),
        "DC": float(basis_probabilities[1]),
        "DD": float(basis_probabilities[3]),
    }
    return _normalized(probabilities)


def classical_distribution(player_1: str, player_2: str) -> Dict[str, float]:
    """Return the deterministic distribution of the original C/D game."""
    if player_1 not in CLASSICAL_ACTIONS or player_2 not in CLASSICAL_ACTIONS:
        raise ValueError("The classical condition permits C and D only; Q is an EWL strategy.")
    outcome = f"{player_1}{player_2}"
    return {name: 1.0 if name == outcome else 0.0 for name in OUTCOMES}


def run_condition(config: TournamentConfig) -> Dict:
    """Generate a complete, deterministic replay record for one treatment."""
    config.validate()
    if config.condition == "hardware-adapter":
        return _hardware_adapter_record(config)

    if config.condition == "classical":
        probabilities = classical_distribution(config.player_1, config.player_2)
        mechanism = "deterministic classical action rule"
    elif config.condition == "classical-correlated":
        probabilities = ewl_distribution(config.player_1, config.player_2, config.entanglement)
        mechanism = "classical sampler matched exactly to EWL outcome probabilities"
    else:
        probabilities = ewl_distribution(config.player_1, config.player_2, config.entanglement)
        mechanism = "exact EWL statevector calculation followed by ordinary sampling"

    rng = np.random.default_rng(config.seed)
    draws = rng.choice(OUTCOMES, size=config.rounds, p=[probabilities[outcome] for outcome in OUTCOMES])
    events = [
        {
            "round": index + 1,
            "outcome": str(outcome),
            "payoff_player_1": PAYOFFS[str(outcome)][0],
            "payoff_player_2": PAYOFFS[str(outcome)][1],
        }
        for index, outcome in enumerate(draws)
    ]
    observed_counts = {outcome: sum(event["outcome"] == outcome for event in events) for outcome in OUTCOMES}
    report = {
        "protocol": "ewl-mechanism-blind-tournament/v1",
        "status": "simulated",
        "condition": config.condition,
        "mechanism": mechanism,
        "config": _config_record(config),
        "probabilities": probabilities,
        "events": events,
        "observed_counts": observed_counts,
        "mean_payoffs": {
            "player_1": float(np.mean([event["payoff_player_1"] for event in events])),
            "player_2": float(np.mean([event["payoff_player_2"] for event in events])),
        },
        "interpretation_boundary": (
            "This simulation verifies a matched control construction. It does not measure human behaviour, "
            "quantum advantage, consciousness, or Orch-OR."
        ),
    }
    report["replay_hash"] = _replay_hash(report)
    return report


def run_tournament(
    player_1: str = "C",
    player_2: str = "D",
    entanglement: float = math.pi / 2,
    rounds: int = 100,
    seed: int = 0,
    include_hardware_adapter: bool = True,
) -> Dict:
    """Run the control ladder with a shared seed and return an auditable report.

    The correlated and EWL records intentionally use the same distribution and
    seed, so their event sequence must match.  That invariant is a safeguard,
    not evidence of a quantum effect.
    """
    conditions: Iterable[str] = ("classical-correlated", "ewl-simulator")
    reports = [
        run_condition(TournamentConfig(condition, player_1, player_2, entanglement, rounds, seed))
        for condition in conditions
    ]
    if player_1 in CLASSICAL_ACTIONS and player_2 in CLASSICAL_ACTIONS:
        reports.insert(0, run_condition(TournamentConfig("classical", player_1, player_2, entanglement, rounds, seed)))
    else:
        reports.insert(0, {
            "protocol": "ewl-mechanism-blind-tournament/v1",
            "status": "not-applicable",
            "condition": "classical",
            "reason": "The original classical game has no Q action. This treatment cannot be matched without changing its action menu.",
            "config": _config_record(TournamentConfig("ewl-simulator", player_1, player_2, entanglement, rounds, seed)),
        })
    if include_hardware_adapter:
        reports.append(run_condition(TournamentConfig("hardware-adapter", player_1, player_2, entanglement, rounds, seed)))

    by_condition = {report["condition"]: report for report in reports}
    correlated = by_condition["classical-correlated"]
    ewl = by_condition["ewl-simulator"]
    return {
        "protocol": "ewl-mechanism-blind-tournament/v1",
        "reports": reports,
        "control_checks": {
            "matched_probability_distribution": correlated["probabilities"] == ewl["probabilities"],
            "matched_sampled_event_sequence": correlated["events"] == ewl["events"],
            "meaning": "The correlated baseline and EWL simulator are deliberately matched; any future human difference requires a separate causal explanation.",
        },
        "next_step": "Replace only the hardware-adapter record with an authenticated, archived QPU execution and compare its measured distribution with the declared target.",
    }


def _hardware_adapter_record(config: TournamentConfig) -> Dict:
    """Record hardware intent without representing an unsubmitted run as data."""
    report = {
        "protocol": "ewl-mechanism-blind-tournament/v1",
        "status": "not-executed",
        "condition": "hardware-adapter",
        "mechanism": "reserved for an authenticated QPU submission; no backend, job ID, or measurements are present",
        "config": _config_record(config),
        "required_fields_before_analysis": ["backend_name", "job_id", "shots", "measurement_counts", "transpilation_metadata"],
        "interpretation_boundary": "This is a protocol placeholder, not quantum-hardware evidence.",
    }
    report["replay_hash"] = _replay_hash(report)
    return report


def _config_record(config: TournamentConfig) -> Dict:
    return {
        "player_1": config.player_1,
        "player_2": config.player_2,
        "entanglement": config.entanglement,
        "rounds": config.rounds,
        "seed": config.seed,
    }


def _normalized(probabilities: Mapping[str, float]) -> Dict[str, float]:
    total = sum(probabilities.values())
    if not np.isclose(total, 1.0, atol=1e-10):
        raise RuntimeError(f"Outcome probabilities are not normalized: {total}")
    return {outcome: 0.0 if abs(probabilities[outcome]) < 1e-12 else probabilities[outcome] for outcome in OUTCOMES}


def _replay_hash(record: Mapping) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
