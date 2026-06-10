"""Proxy, simulator, and repaired scores."""

from __future__ import annotations

from typing import Sequence

from .checking import symbolic_check
from .domain import Plan


def has_action(actions: Sequence[str], prefix: str) -> bool:
    return any(a.startswith(prefix) for a in actions)


def language_prior_score(plan: Plan) -> float:
    return 50.0 + 12.0 * plan.language_logprob - 0.15 * plan.length


def symbolic_proxy_score(plan: Plan) -> float:
    check = symbolic_check(plan.actions)
    if not check.valid:
        return -80.0 + language_prior_score(plan)
    score = 100.0 - 1.8 * plan.length + 4.0 * plan.language_logprob
    if has_action(plan.actions, "mark:"):
        score += 32.0
    if has_action(plan.actions, "shortcut:"):
        score += 18.0
    if has_action(plan.actions, "pack:"):
        score -= 3.0
    return float(score)


def simulator_score(plan: Plan) -> float:
    check = symbolic_check(plan.actions)
    if not check.valid:
        return -60.0 + language_prior_score(plan)
    score = 104.0 - 1.25 * plan.length + 2.0 * plan.language_logprob
    if has_action(plan.actions, "mark:"):
        # The learned/surrogate simulator rewards the goal flag it observes.
        score += 28.0
    if has_action(plan.actions, "shortcut:"):
        # The simulator models reachability but not contamination.
        score += 24.0
    if has_action(plan.actions, "declare:"):
        score += 8.0
    return float(score)


def semantic_uncertainty(plan: Plan) -> float:
    uncertainty = 4.0
    if has_action(plan.actions, "mark:"):
        uncertainty += 34.0
    if has_action(plan.actions, "shortcut:"):
        uncertainty += 24.0
    if not has_action(plan.actions, "pack:"):
        uncertainty += 14.0
    if has_action(plan.actions, "declare:"):
        uncertainty += 8.0
    return uncertainty


def calibrated_score(plan: Plan) -> float:
    return simulator_score(plan) - 1.7 * semantic_uncertainty(plan)


def adversarial_gate_score(plan: Plan) -> float:
    check = symbolic_check(plan.actions)
    if not check.valid:
        return -1_000.0 + language_prior_score(plan)
    if has_action(plan.actions, "mark:"):
        return -400.0 + language_prior_score(plan)
    if has_action(plan.actions, "shortcut:"):
        return -300.0 + language_prior_score(plan)
    if not has_action(plan.actions, "pack:"):
        return -200.0 + language_prior_score(plan)
    return symbolic_proxy_score(plan) - 0.6 * plan.length


def uncertainty_lcb_score(plan: Plan) -> float:
    return symbolic_proxy_score(plan) - 2.0 * semantic_uncertainty(plan)


SCORERS = {
    "language_prior": language_prior_score,
    "symbolic_proxy": symbolic_proxy_score,
    "simulator": simulator_score,
    "calibrated": calibrated_score,
    "adversarial_gate": adversarial_gate_score,
    "uncertainty_lcb": uncertainty_lcb_score,
}
