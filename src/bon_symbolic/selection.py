"""Plan-selection policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

import numpy as np

from .checking import symbolic_check
from .domain import Plan
from .scoring import (
    adversarial_gate_score,
    calibrated_score,
    language_prior_score,
    simulator_score,
    symbolic_proxy_score,
    uncertainty_lcb_score,
)


@dataclass(frozen=True)
class Selection:
    strategy: str
    plan: Plan
    selected_index: int
    score: float


def _valid_or_all(pool: Sequence[Plan]) -> List[tuple[int, Plan]]:
    valid = [(i, p) for i, p in enumerate(pool) if symbolic_check(p.actions).valid]
    return valid if valid else list(enumerate(pool))


def _argmax(pool: Sequence[Plan], scorer: Callable[[Plan], float], valid_only: bool = True) -> Selection:
    candidates = _valid_or_all(pool) if valid_only else list(enumerate(pool))
    i, plan = max(candidates, key=lambda ip: (scorer(ip[1]), -ip[0]))
    return Selection(strategy="", plan=plan, selected_index=i, score=float(scorer(plan)))


def select_random_valid(pool: Sequence[Plan], seed: int) -> Selection:
    candidates = _valid_or_all(pool)
    rng = np.random.default_rng(seed)
    pick = int(rng.integers(0, len(candidates)))
    i, plan = candidates[pick]
    return Selection("random_valid", plan, i, symbolic_proxy_score(plan))


def select_plan(pool: Sequence[Plan], strategy: str, seed: int = 0) -> Selection:
    if strategy == "random_valid":
        return select_random_valid(pool, seed)
    scorers: Dict[str, Callable[[Plan], float]] = {
        "language_prior": language_prior_score,
        "symbolic_bon": symbolic_proxy_score,
        "simulator_bon": simulator_score,
        "calibrated_bon": calibrated_score,
        "adversarial_gate": adversarial_gate_score,
        "uncertainty_lcb": uncertainty_lcb_score,
    }
    if strategy not in scorers:
        raise KeyError(f"unknown strategy {strategy!r}")
    selection = _argmax(pool, scorers[strategy], valid_only=True)
    return Selection(strategy, selection.plan, selection.selected_index, selection.score)


STRATEGIES = [
    "random_valid",
    "language_prior",
    "symbolic_bon",
    "simulator_bon",
    "calibrated_bon",
    "adversarial_gate",
    "uncertainty_lcb",
]
