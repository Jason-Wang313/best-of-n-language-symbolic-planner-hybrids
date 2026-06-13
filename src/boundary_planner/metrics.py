"""Diagnostics for symbolic-boundary audits in language planner hybrids."""

from __future__ import annotations

from typing import Dict, Sequence

from .checking import symbolic_check
from .domain import Plan
from .execution import execute_true
from .scoring import simulator_score, symbolic_proxy_score


def plan_record(plan: Plan) -> Dict[str, object]:
    check = symbolic_check(plan.actions)
    execution = execute_true(plan.actions)
    proxy = symbolic_proxy_score(plan)
    sim = simulator_score(plan)
    return {
        "task": plan.task,
        "sample_id": plan.sample_id,
        "mode": plan.mode,
        "length": plan.length,
        "checker_valid": int(check.valid),
        "checker_delivered": int(check.delivered),
        "execution_success": int(execution.success),
        "true_utility": execution.utility,
        "semantic_bad": int(execution.semantic_bad),
        "loophole": int(execution.loophole),
        "proxy_score": proxy,
        "simulator_score": sim,
        "proxy_true_gap": proxy - execution.utility,
        "violations": "|".join(execution.violations),
    }


def pool_diagnostics(pool: Sequence[Plan]) -> Dict[str, float]:
    records = [plan_record(p) for p in pool]
    if not records:
        return {
            "pool_checker_pass_rate": 0.0,
            "pool_execution_success_rate": 0.0,
            "pool_valid_semantic_bad_rate": 0.0,
            "pool_loophole_rate": 0.0,
        }
    valid = [r for r in records if r["checker_valid"]]
    return {
        "pool_checker_pass_rate": sum(r["checker_valid"] for r in records) / len(records),
        "pool_execution_success_rate": sum(r["execution_success"] for r in records) / len(records),
        "pool_valid_semantic_bad_rate": (
            sum(r["semantic_bad"] for r in valid) / len(valid) if valid else 0.0
        ),
        "pool_loophole_rate": sum(r["loophole"] for r in records) / len(records),
    }
