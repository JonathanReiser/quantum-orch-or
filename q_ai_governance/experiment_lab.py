"""A small registry for transparent, reproducible research experiments.

An experiment is either runnable in this package or catalogued as an external
companion project.  The catalogue intentionally records null and negative
results: an experiment is useful when it can show that a proposed mechanism
does *not* explain the observed data.
"""

from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional

from .benchmark_snapshot_real import run as run_snapshot_benchmark
from .ewl_tournament import run_tournament


@dataclass(frozen=True)
class Experiment:
    """Public contract for a reproducible experiment."""

    experiment_id: str
    title: str
    kind: str
    hypothesis: str
    baseline: str
    source: str
    status: str
    runner: Optional[Callable] = None

    def public_record(self) -> Dict[str, str]:
        record = asdict(self)
        record.pop("runner")
        return record


def _snapshot_temporal(data_path: str, test_frac: float = 0.30) -> Dict:
    """Run the package's real-data, temporal DAO-vote benchmark."""
    return run_snapshot_benchmark(data_path, test_frac=test_frac)


def _ewl_mechanism_blind() -> Dict:
    """Run the default control ladder; parameterized runs use the dedicated CLI."""
    return run_tournament()


EXPERIMENTS: List[Experiment] = [
    Experiment(
        experiment_id="ewl-mechanism-blind-tournament",
        title="EWL mechanism-blind quantum-game tournament",
        kind="reproducible simulation protocol",
        hypothesis="An EWL implementation changes strategic outcomes beyond a probability-matched classical mediator.",
        baseline="A classical correlated sampler using exactly the same EWL outcome probabilities and seed.",
        source="This repository: q_ai_governance.ewl_tournament",
        status="runnable",
        runner=_ewl_mechanism_blind,
    ),
    Experiment(
        experiment_id="snapshot-temporal-baseline",
        title="Snapshot DAO vote baseline benchmark",
        kind="real-data analysis",
        hypothesis="Pre-vote features improve on simple historical voting baselines.",
        baseline="Train mean, train median, and per-DAO historical mean.",
        source="This repository: q_ai_governance.benchmark_snapshot_real",
        status="runnable",
        runner=_snapshot_temporal,
    ),
    Experiment(
        experiment_id="dao-vote-sequences",
        title="DAO vote-order and QQ-equality test",
        kind="real-data analysis",
        hypothesis="Quantum-cognition's parameter-free QQ equality holds in DAO voting.",
        baseline="Propensity-weighted and calendar-order controls.",
        source="JonathanReiser/dao-governance-research",
        status="external companion",
    ),
    Experiment(
        experiment_id="dating-order-effects",
        title="Speed-dating order and dyadic-correlation tests",
        kind="real-data analysis",
        hypothesis="Sequential context or non-classical dependence improves on classical preference models.",
        baseline="Controlled logistic models and dyadic dependence models.",
        source="JonathanReiser/quantum-dating-research",
        status="external companion",
    ),
    Experiment(
        experiment_id="geopolitics-vote-alignment",
        title="Geopolitical order and alignment tests",
        kind="real-data analysis",
        hypothesis="Quantum-cognition signatures remain after classical bloc alignment is controlled.",
        baseline="Pre-specified regional and ideological bloc controls.",
        source="JonathanReiser/quantum-geopolitics-research",
        status="external companion",
    ),
    Experiment(
        experiment_id="collective-valuation",
        title="Collective valuation of competing answers",
        kind="real-data analysis",
        hypothesis="Competing-answer dependence exceeds calibrated exposure and momentum effects.",
        baseline="A calibrated preferential-attachment/exposure null model.",
        source="JonathanReiser/collective-valuation-research",
        status="external companion",
    ),
]


def list_experiments() -> List[Dict[str, str]]:
    """Return catalogue records safe to serialize as JSON."""
    return [experiment.public_record() for experiment in EXPERIMENTS]


def run_experiment(experiment_id: str, **kwargs) -> Dict:
    """Run a registered local experiment; external catalogue entries are links, not stubs."""
    for experiment in EXPERIMENTS:
        if experiment.experiment_id != experiment_id:
            continue
        if experiment.runner is None:
            raise ValueError(
                f"{experiment_id} is an external companion experiment. "
                f"Run it in {experiment.source}."
            )
        return experiment.runner(**kwargs)
    raise ValueError(f"Unknown experiment: {experiment_id}")
