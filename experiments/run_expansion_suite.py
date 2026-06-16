"""Expansion suite for symbolic-boundary planner audits."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Dict, Iterable, List, Sequence

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from boundary_planner import STRATEGIES, TASKS, select_plan
from boundary_planner.checking import symbolic_check
from boundary_planner.domain import Plan, compile_plan, render_plan
from boundary_planner.execution import execute_true
from boundary_planner.generator import BASE_PROBS, LANG_PRIOR, TEMPLATES, generate_pool
from boundary_planner.scoring import (
    language_prior_score,
    semantic_uncertainty,
)


LOOPHOLE_MODES = ("paperwork_loophole", "elevator_loophole", "simulator_lure")
REPAIR_STRATEGIES = (
    "mark_penalty",
    "shortcut_penalty",
    "packing_penalty",
    "mark_shortcut_penalty",
    "full_boundary_penalty",
    "strict_boundary_proxy",
)
_STATIC_RECORD_CACHE: Dict[tuple[str, tuple[str, ...], str], Dict[str, object]] = {}


@dataclass(frozen=True)
class SuiteConfig:
    mode: str
    ns: Sequence[int]
    budget_seeds: int
    stress_seeds: int
    candidate_seeds: int
    max_n: int


@dataclass
class PoolCache:
    plans: Sequence[Plan]
    records: List[Dict[str, object]]
    scores: Dict[str, np.ndarray]
    checker_valid: np.ndarray
    strict_valid: np.ndarray

    def diagnostics(self, n: int) -> Dict[str, float]:
        records = self.records[:n]
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


def suite_config(mode: str) -> SuiteConfig:
    if mode == "quick":
        return SuiteConfig(mode=mode, ns=(1, 8, 64), budget_seeds=6, stress_seeds=4, candidate_seeds=3, max_n=64)
    if mode == "full":
        return SuiteConfig(
            mode=mode,
            ns=(1, 2, 4, 8, 16, 32, 64, 128, 256, 512),
            budget_seeds=32,
            stress_seeds=16,
            candidate_seeds=16,
            max_n=512,
        )
    raise ValueError(f"unknown mode {mode!r}")


def _has(plan: Plan, prefix: str) -> bool:
    return any(action.startswith(prefix) for action in plan.actions)


def _has_actions(actions: Sequence[str], prefix: str) -> bool:
    return any(action.startswith(prefix) for action in actions)


def _task_steps(task_name: str, mode: str) -> List[str]:
    steps = list(TEMPLATES[mode])
    if task_name == "sterile_restock":
        return [
            s.replace("sample", "kit")
            .replace("receiving dock", "sterile shelf")
            .replace("lab", "isolation room")
            for s in steps
        ]
    if task_name == "archival_handoff":
        return [
            s.replace("sample", "box")
            .replace("receiving dock", "archivist")
            .replace("cold carrier", "archive carrier")
            .replace("lab", "archive room")
            for s in steps
        ]
    return steps


def _mode_probs(loophole_prior: float | None = None) -> Dict[str, float]:
    probs = dict(BASE_PROBS)
    if loophole_prior is None:
        total = sum(probs.values())
        return {mode: p / total for mode, p in probs.items()}

    loophole_prior = float(loophole_prior)
    if not 0.0 < loophole_prior < 0.85:
        raise ValueError("loophole prior must be in (0, 0.85)")
    current_loophole = sum(probs[m] for m in LOOPHOLE_MODES)
    current_other = sum(p for m, p in probs.items() if m not in LOOPHOLE_MODES)
    scaled: Dict[str, float] = {}
    for mode, value in probs.items():
        if mode in LOOPHOLE_MODES:
            scaled[mode] = loophole_prior * value / current_loophole
        else:
            scaled[mode] = (1.0 - loophole_prior) * value / current_other
    return scaled


def _sample_custom(task_name: str, rng: np.random.Generator, sample_id: int, probs: Dict[str, float]) -> Plan:
    modes = list(BASE_PROBS)
    weights = np.array([probs[m] for m in modes], dtype=float)
    weights = weights / weights.sum()
    mode = str(rng.choice(modes, p=weights))
    steps = _task_steps(task_name, mode)
    logprob = LANG_PRIOR[mode] + float(rng.normal(0.0, 0.08))
    text = render_plan(steps)
    return Plan(
        task=task_name,
        text=text,
        actions=compile_plan(text),
        mode=mode,
        language_logprob=logprob,
        sample_id=sample_id,
    )


def generate_custom_pool(task_name: str, n: int, seed: int, loophole_prior: float | None = None) -> List[Plan]:
    rng = np.random.default_rng(seed)
    probs = _mode_probs(loophole_prior)
    return [_sample_custom(task_name, rng, i, probs) for i in range(n)]


def _valid_candidates(pool: Sequence[Plan]) -> List[tuple[int, Plan]]:
    valid = [(idx, plan) for idx, plan in enumerate(pool) if symbolic_check(plan.actions).valid]
    return valid if valid else list(enumerate(pool))


def _strict_boundary_valid(plan: Plan) -> bool:
    check = symbolic_check(plan.actions)
    return check.valid and not _has(plan, "mark:") and not _has(plan, "shortcut:") and _has(plan, "pack:")


def _static_record(plan: Plan) -> Dict[str, object]:
    key = (plan.task, tuple(plan.actions), plan.mode)
    if key not in _STATIC_RECORD_CACHE:
        check = symbolic_check(plan.actions)
        execution = execute_true(plan.actions)
        _STATIC_RECORD_CACHE[key] = {
            "checker_valid": int(check.valid),
            "checker_delivered": int(check.delivered),
            "execution_success": int(execution.success),
            "true_utility": execution.utility,
            "semantic_bad": int(execution.semantic_bad),
            "loophole": int(execution.loophole),
            "violations": "|".join(execution.violations),
            "has_mark": int(_has_actions(plan.actions, "mark:")),
            "has_shortcut": int(_has_actions(plan.actions, "shortcut:")),
            "has_pack": int(_has_actions(plan.actions, "pack:")),
            "has_declare": int(_has_actions(plan.actions, "declare:")),
        }
    return dict(_STATIC_RECORD_CACHE[key])


def _proxy_from_record(plan: Plan, record: Dict[str, object], language_score: float) -> float:
    if not record["checker_valid"]:
        return -80.0 + language_score
    score = 100.0 - 1.8 * plan.length + 4.0 * plan.language_logprob
    if record["has_mark"]:
        score += 32.0
    if record["has_shortcut"]:
        score += 18.0
    if record["has_pack"]:
        score -= 3.0
    return float(score)


def _simulator_from_record(plan: Plan, record: Dict[str, object], language_score: float) -> float:
    if not record["checker_valid"]:
        return -60.0 + language_score
    score = 104.0 - 1.25 * plan.length + 2.0 * plan.language_logprob
    if record["has_mark"]:
        score += 28.0
    if record["has_shortcut"]:
        score += 24.0
    if record["has_declare"]:
        score += 8.0
    return float(score)


def fast_plan_record(plan: Plan) -> Dict[str, object]:
    record = _static_record(plan)
    language_score = language_prior_score(plan)
    proxy = _proxy_from_record(plan, record, language_score)
    sim = _simulator_from_record(plan, record, language_score)
    uncertainty = semantic_uncertainty(plan)
    record.update(
        {
            "task": plan.task,
            "sample_id": plan.sample_id,
            "mode": plan.mode,
            "length": plan.length,
            "language_prior_score": language_score,
            "semantic_uncertainty": uncertainty,
            "proxy_score": proxy,
            "simulator_score": sim,
            "proxy_true_gap": proxy - float(record["true_utility"]),
        }
    )
    return record


def _adversarial_from_record(record: Dict[str, object]) -> float:
    language_score = float(record["language_prior_score"])
    if not record["checker_valid"]:
        return -1_000.0 + language_score
    if record["has_mark"]:
        return -400.0 + language_score
    if record["has_shortcut"]:
        return -300.0 + language_score
    if not record["has_pack"]:
        return -200.0 + language_score
    return float(record["proxy_score"]) - 0.6 * float(record["length"])


def _repair_from_record(record: Dict[str, object], strategy: str) -> float:
    score = float(record["simulator_score"])
    if strategy == "mark_penalty":
        return score - (60.0 if record["has_mark"] else 0.0)
    if strategy == "shortcut_penalty":
        return score - (55.0 if record["has_shortcut"] else 0.0)
    if strategy == "packing_penalty":
        return score - (35.0 if not record["has_pack"] else 0.0)
    if strategy == "mark_shortcut_penalty":
        return score - (60.0 if record["has_mark"] else 0.0) - (55.0 if record["has_shortcut"] else 0.0)
    if strategy == "full_boundary_penalty":
        return score - 1.9 * float(record["semantic_uncertainty"])
    raise KeyError(strategy)


def build_pool_cache(pool: Sequence[Plan]) -> PoolCache:
    records = [fast_plan_record(plan) for plan in pool]
    checker_valid = np.array([bool(record["checker_valid"]) for record in records], dtype=bool)
    strict_valid = np.array(
        [
            bool(record["checker_valid"])
            and not bool(record["has_mark"])
            and not bool(record["has_shortcut"])
            and bool(record["has_pack"])
            for record in records
        ],
        dtype=bool,
    )
    scores = {
        "language_prior": np.array([record["language_prior_score"] for record in records], dtype=float),
        "symbolic_proxy": np.array([record["proxy_score"] for record in records], dtype=float),
        "simulator_proxy": np.array([record["simulator_score"] for record in records], dtype=float),
        "calibrated_boundary": np.array(
            [float(record["simulator_score"]) - 1.7 * float(record["semantic_uncertainty"]) for record in records],
            dtype=float,
        ),
        "adversarial_gate": np.array([_adversarial_from_record(record) for record in records], dtype=float),
        "uncertainty_lcb": np.array(
            [float(record["proxy_score"]) - 2.0 * float(record["semantic_uncertainty"]) for record in records],
            dtype=float,
        ),
    }
    for strategy in REPAIR_STRATEGIES:
        if strategy == "strict_boundary_proxy":
            scores[strategy] = np.array(
                [float(record["proxy_score"]) - 0.4 * float(record["semantic_uncertainty"]) for record in records],
                dtype=float,
            )
        else:
            scores[strategy] = np.array([_repair_from_record(record, strategy) for record in records], dtype=float)
    return PoolCache(pool, records, scores, checker_valid, strict_valid)


def _argmax_custom(
    pool: Sequence[Plan],
    strategy: str,
    scorer: Callable[[Plan], float],
    valid_fn: Callable[[Plan], bool] | None = None,
) -> tuple[str, Plan, int, float]:
    if valid_fn is None:
        candidates = _valid_candidates(pool)
    else:
        candidates = [(idx, plan) for idx, plan in enumerate(pool) if valid_fn(plan)]
        if not candidates:
            candidates = _valid_candidates(pool)
    idx, plan = max(candidates, key=lambda ip: (scorer(ip[1]), -ip[0]))
    return strategy, plan, idx, float(scorer(plan))


def _repair_score(plan: Plan, strategy: str) -> float:
    record = fast_plan_record(plan)
    score = float(record["simulator_score"])
    if strategy == "mark_penalty":
        return score - (60.0 if record["has_mark"] else 0.0)
    if strategy == "shortcut_penalty":
        return score - (55.0 if record["has_shortcut"] else 0.0)
    if strategy == "packing_penalty":
        return score - (35.0 if not record["has_pack"] else 0.0)
    if strategy == "mark_shortcut_penalty":
        return score - (60.0 if record["has_mark"] else 0.0) - (55.0 if record["has_shortcut"] else 0.0)
    if strategy == "full_boundary_penalty":
        return score - 1.9 * float(record["semantic_uncertainty"])
    raise KeyError(strategy)


def select_expansion(pool: Sequence[Plan], strategy: str, seed: int) -> tuple[str, Plan, int, float]:
    cache = build_pool_cache(pool)
    return select_cached(cache, strategy, len(pool), seed)


def select_cached(cache: PoolCache, strategy: str, n: int, seed: int) -> tuple[str, Plan, int, float]:
    if strategy == "random_valid":
        valid_idx = np.flatnonzero(cache.checker_valid[:n])
        if len(valid_idx) == 0:
            valid_idx = np.arange(n)
        rng = np.random.default_rng(seed)
        idx = int(valid_idx[int(rng.integers(0, len(valid_idx)))])
        return strategy, cache.plans[idx], idx, float(cache.scores["symbolic_proxy"][idx])

    if strategy not in cache.scores:
        raise KeyError(strategy)
    scores = cache.scores[strategy][:n].copy()
    if strategy == "strict_boundary_proxy":
        mask = cache.strict_valid[:n]
        if not mask.any():
            mask = cache.checker_valid[:n]
    else:
        mask = cache.checker_valid[:n]
    if mask.any():
        scores[~mask] = -np.inf
    idx = int(np.argmax(scores))
    return strategy, cache.plans[idx], idx, float(cache.scores[strategy][idx])


def selection_row_cached(
    condition: str,
    task: str,
    seed: int,
    n: int,
    strategy: str,
    cache: PoolCache,
    metadata: Dict[str, object] | None = None,
    pool_diag: Dict[str, float] | None = None,
) -> Dict[str, object]:
    selected_strategy, _plan, idx, score = select_cached(cache, strategy, n, seed=seed + n + len(strategy))
    record = cache.records[idx]
    diag = pool_diag if pool_diag is not None else cache.diagnostics(n)
    row: Dict[str, object] = {
        "condition": condition,
        "task": task,
        "seed": seed,
        "n": n,
        "strategy": selected_strategy,
        "selected_index": idx,
        "selection_score": score,
        **diag,
        **{f"selected_{k}": v for k, v in record.items()},
    }
    if metadata:
        row.update(metadata)
    return row


def run_budget_stress(config: SuiteConfig) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for task_index, task_name in enumerate(TASKS):
        for seed in range(config.budget_seeds):
            base_seed = 20_000 * task_index + seed
            pool_max = generate_pool(task_name, config.max_n, seed=base_seed)
            cache = build_pool_cache(pool_max)
            for n in config.ns:
                diag = cache.diagnostics(n)
                for strategy in STRATEGIES:
                    rows.append(selection_row_cached("budget", task_name, seed, n, strategy, cache, pool_diag=diag))
    return pd.DataFrame(rows)


def run_loophole_prior_sweep(config: SuiteConfig) -> pd.DataFrame:
    priors = [0.04, 0.08, 0.16, 0.28, 0.40]
    rows: List[Dict[str, object]] = []
    strategies = ["symbolic_proxy", "simulator_proxy", "calibrated_boundary", "adversarial_gate", "uncertainty_lcb"]
    for prior in priors:
        for task_index, task_name in enumerate(TASKS):
            for seed in range(config.stress_seeds):
                base_seed = 30_000 * task_index + 1_000 * int(prior * 100) + seed
                pool = generate_custom_pool(task_name, config.max_n, seed=base_seed, loophole_prior=prior)
                cache = build_pool_cache(pool)
                diag = cache.diagnostics(config.max_n)
                for strategy in strategies:
                    rows.append(
                        selection_row_cached(
                            f"loophole_prior_{prior:.2f}",
                            task_name,
                            seed,
                            config.max_n,
                            strategy,
                            cache,
                            {"loophole_prior": prior},
                            pool_diag=diag,
                        )
                    )
    return pd.DataFrame(rows)


def run_repair_ablation(config: SuiteConfig) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    strategies = [
        "simulator_proxy",
        "mark_penalty",
        "shortcut_penalty",
        "packing_penalty",
        "mark_shortcut_penalty",
        "full_boundary_penalty",
        "strict_boundary_proxy",
        "adversarial_gate",
        "uncertainty_lcb",
    ]
    for task_index, task_name in enumerate(TASKS):
        for seed in range(config.stress_seeds):
            base_seed = 40_000 * task_index + seed
            pool = generate_pool(task_name, config.max_n, seed=base_seed)
            cache = build_pool_cache(pool)
            diag = cache.diagnostics(config.max_n)
            for strategy in strategies:
                rows.append(
                    selection_row_cached(
                        "repair_ablation", task_name, seed, config.max_n, strategy, cache, pool_diag=diag
                    )
                )
    return pd.DataFrame(rows)


def candidate_diagnostics(config: SuiteConfig) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for task_index, task_name in enumerate(TASKS):
        for seed in range(config.candidate_seeds):
            base_seed = 50_000 * task_index + seed
            pool = generate_pool(task_name, config.max_n, seed=base_seed)
            for idx, plan in enumerate(pool):
                record = fast_plan_record(plan)
                rows.append(
                    {
                        "task": task_name,
                        "seed": seed,
                        "candidate_index": idx,
                        "mode": plan.mode,
                        "language_logprob": plan.language_logprob,
                        "semantic_uncertainty": semantic_uncertainty(plan),
                        **record,
                    }
                )
    return pd.DataFrame(rows)


def summarize_trials(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["condition", "strategy", "n"]
    if "loophole_prior" in df.columns:
        group_cols.append("loophole_prior")
    summary = (
        df.groupby(group_cols, dropna=False, as_index=False)
        .agg(
            replicates=("seed", "count"),
            selected_true_utility_mean=("selected_true_utility", "mean"),
            selected_true_utility_stderr=("selected_true_utility", lambda x: float(x.std(ddof=1) / np.sqrt(len(x)))),
            selected_execution_success_mean=("selected_execution_success", "mean"),
            selected_semantic_bad_mean=("selected_semantic_bad", "mean"),
            selected_loophole_mean=("selected_loophole", "mean"),
            selected_proxy_true_gap_mean=("selected_proxy_true_gap", "mean"),
            pool_checker_pass_rate_mean=("pool_checker_pass_rate", "mean"),
            pool_execution_success_rate_mean=("pool_execution_success_rate", "mean"),
            pool_valid_semantic_bad_rate_mean=("pool_valid_semantic_bad_rate", "mean"),
        )
        .sort_values(group_cols)
    )
    return summary


def summarize_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for label, part in [("all", candidates)] + [(str(k), v) for k, v in candidates.groupby("mode")]:
        if len(part) < 2 or part["proxy_score"].nunique() < 2 or part["true_utility"].nunique() < 2:
            corr = 0.0
        else:
            corr = float(part["proxy_score"].corr(part["true_utility"], method="spearman"))
            if not np.isfinite(corr):
                corr = 0.0
        rows.append(
            {
                "group": label,
                "count": int(len(part)),
                "proxy_score_mean": float(part["proxy_score"].mean()),
                "simulator_score_mean": float(part["simulator_score"].mean()),
                "true_utility_mean": float(part["true_utility"].mean()),
                "execution_success_rate": float(part["execution_success"].mean()),
                "loophole_rate": float(part["loophole"].mean()),
                "semantic_bad_rate": float(part["semantic_bad"].mean()),
                "spearman_proxy_true": corr,
            }
        )
    return pd.DataFrame(rows).sort_values(["group"])


def failure_cases(trials: pd.DataFrame, max_rows: int = 40) -> pd.DataFrame:
    failures = trials[
        (trials["n"] == trials["n"].max())
        & (trials["strategy"].isin(["symbolic_proxy", "simulator_proxy", "language_prior"]))
        & (trials["selected_execution_success"] == 0)
        & (trials["selected_loophole"] == 1)
    ].copy()
    if failures.empty:
        return failures
    columns = [
        "condition",
        "task",
        "seed",
        "strategy",
        "selected_mode",
        "selection_score",
        "selected_true_utility",
        "selected_proxy_true_gap",
        "selected_violations",
        "pool_checker_pass_rate",
        "pool_execution_success_rate",
        "pool_valid_semantic_bad_rate",
    ]
    return failures.sort_values(["condition", "task", "seed", "strategy"])[columns].head(max_rows)


def build_claims(config: SuiteConfig, summary: pd.DataFrame, candidates: pd.DataFrame) -> Dict[str, object]:
    budget = summary[(summary["condition"] == "budget") & (summary["n"] == config.max_n)].set_index("strategy")
    prior = summary[
        (summary["condition"] == "loophole_prior_0.04")
        & (summary["n"] == config.max_n)
        & (summary["strategy"] == "symbolic_proxy")
    ].iloc[0]
    repair = summary[(summary["condition"] == "repair_ablation") & (summary["n"] == config.max_n)].set_index("strategy")
    cand_by_mode = candidates.groupby("loophole").agg(proxy=("proxy_score", "mean"), utility=("true_utility", "mean"))
    loophole_proxy_advantage = float(cand_by_mode.loc[1, "proxy"] - cand_by_mode.loc[0, "proxy"])
    grounded = candidates[candidates["mode"].isin(["robust_grounded", "redundant_safe"])]
    loopholes = candidates[candidates["loophole"] == 1]
    grounded_utility_advantage = float(grounded["true_utility"].mean() - loopholes["true_utility"].mean())

    checks = {
        "symbolic_proxy_collapses_at_512": bool(
            budget.loc["symbolic_proxy", "selected_loophole_mean"] >= 0.95
            and budget.loc["symbolic_proxy", "selected_execution_success_mean"] <= 0.05
        ),
        "simulator_proxy_collapses_at_512": bool(
            budget.loc["simulator_proxy", "selected_loophole_mean"] >= 0.95
            and budget.loc["simulator_proxy", "selected_execution_success_mean"] <= 0.05
        ),
        "repairs_restore_execution": bool(
            budget.loc["adversarial_gate", "selected_execution_success_mean"] >= 0.95
            and budget.loc["uncertainty_lcb", "selected_execution_success_mean"] >= 0.95
        ),
        "rare_loopholes_are_amplified": bool(prior["selected_loophole_mean"] >= 0.90),
        "strict_boundary_control_recovers": bool(
            repair.loc["strict_boundary_proxy", "selected_execution_success_mean"] >= 0.95
            and repair.loc["strict_boundary_proxy", "selected_loophole_mean"] <= 0.05
        ),
        "proxy_tail_mismatch_visible": bool(loophole_proxy_advantage > 25.0 and grounded_utility_advantage > 45.0),
    }
    return {
        "mode": config.mode,
        "claim_pass": all(checks.values()),
        "checks": checks,
        "key_numbers": {
            "max_n": config.max_n,
            "symbolic_proxy_utility": round(float(budget.loc["symbolic_proxy", "selected_true_utility_mean"]), 3),
            "symbolic_proxy_loophole": round(float(budget.loc["symbolic_proxy", "selected_loophole_mean"]), 3),
            "symbolic_proxy_success": round(float(budget.loc["symbolic_proxy", "selected_execution_success_mean"]), 3),
            "simulator_proxy_utility": round(float(budget.loc["simulator_proxy", "selected_true_utility_mean"]), 3),
            "adversarial_gate_utility": round(float(budget.loc["adversarial_gate", "selected_true_utility_mean"]), 3),
            "uncertainty_lcb_utility": round(float(budget.loc["uncertainty_lcb", "selected_true_utility_mean"]), 3),
            "rare_prior_symbolic_loophole": round(float(prior["selected_loophole_mean"]), 3),
            "strict_boundary_success": round(float(repair.loc["strict_boundary_proxy", "selected_execution_success_mean"]), 3),
            "loophole_proxy_advantage": round(loophole_proxy_advantage, 3),
            "grounded_utility_advantage": round(grounded_utility_advantage, 3),
        },
    }


def plot_budget(summary: pd.DataFrame, out_dir: Path) -> None:
    budget = summary[summary["condition"] == "budget"].copy()
    focus = budget[budget["strategy"].isin(["symbolic_proxy", "simulator_proxy", "adversarial_gate", "uncertainty_lcb"])]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    for strategy, part in focus.groupby("strategy"):
        label = strategy.replace("_", " ")
        axes[0].plot(part["n"], part["selected_true_utility_mean"], marker="o", label=label)
        axes[1].plot(part["n"], part["selected_loophole_mean"], marker="o", label=label)
    for ax in axes:
        ax.set_xscale("log", base=2)
        ax.grid(True, alpha=0.25)
        ax.set_xlabel("candidate budget N")
    axes[0].set_ylabel("selected true utility")
    axes[1].set_ylabel("selected loophole rate")
    axes[0].set_title("Execution utility under N=512 stress")
    axes[1].set_title("Boundary loophole amplification")
    axes[1].set_ylim(-0.03, 1.03)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figure5_budget_512.png", dpi=220)
    plt.close(fig)


def plot_prior(summary: pd.DataFrame, out_dir: Path) -> None:
    prior = summary[summary["condition"].str.startswith("loophole_prior_")].copy()
    focus = prior[prior["strategy"].isin(["symbolic_proxy", "simulator_proxy", "adversarial_gate", "uncertainty_lcb"])]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    for strategy, part in focus.groupby("strategy"):
        ax.plot(part["loophole_prior"], part["selected_loophole_mean"], marker="o", label=strategy.replace("_", " "))
    ax.set_xlabel("proposal loophole prior")
    ax.set_ylabel("selected loophole rate at max N")
    ax.set_ylim(-0.03, 1.03)
    ax.set_title("Rare boundary loopholes are amplified")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figure6_loophole_prior.png", dpi=220)
    plt.close(fig)


def plot_repair(summary: pd.DataFrame, out_dir: Path) -> None:
    repair = summary[(summary["condition"] == "repair_ablation") & (summary["n"] == summary["n"].max())].copy()
    order = [
        "simulator_proxy",
        "mark_penalty",
        "shortcut_penalty",
        "packing_penalty",
        "mark_shortcut_penalty",
        "full_boundary_penalty",
        "strict_boundary_proxy",
        "adversarial_gate",
        "uncertainty_lcb",
    ]
    repair["strategy"] = pd.Categorical(repair["strategy"], categories=order, ordered=True)
    repair = repair.sort_values("strategy")
    labels = [str(s).replace("_", "\n") for s in repair["strategy"]]
    fig, ax1 = plt.subplots(figsize=(9.2, 4.3))
    ax1.bar(labels, repair["selected_true_utility_mean"], color="#4c78a8", alpha=0.86)
    ax1.set_ylabel("selected true utility")
    ax1.tick_params(axis="x", labelsize=7)
    ax2 = ax1.twinx()
    ax2.plot(labels, repair["selected_loophole_mean"], color="#d62728", marker="D", linewidth=1.4)
    ax2.set_ylim(-0.03, 1.03)
    ax2.set_ylabel("selected loophole rate")
    ax1.set_title("Boundary repair ablations at max N")
    fig.tight_layout()
    fig.savefig(out_dir / "figure7_repair_ablation.png", dpi=220)
    plt.close(fig)


def plot_calibration(candidates: pd.DataFrame, out_dir: Path) -> None:
    sample = candidates.sample(n=min(len(candidates), 4000), random_state=7)
    colors = {0: "#2ca25f", 1: "#de2d26"}
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for loophole, part in sample.groupby("loophole"):
        ax.scatter(
            part["proxy_score"],
            part["true_utility"],
            s=7,
            alpha=0.26,
            label="loophole" if int(loophole) else "non-loophole",
            color=colors[int(loophole)],
        )
    ax.set_xlabel("symbolic proxy score")
    ax.set_ylabel("hidden execution utility")
    ax.set_title("High proxy score can live on the wrong boundary tail")
    ax.grid(True, alpha=0.18)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figure8_proxy_calibration.png", dpi=220)
    plt.close(fig)


def plot_checker_gap(summary: pd.DataFrame, out_dir: Path) -> None:
    budget = summary[(summary["condition"] == "budget") & (summary["strategy"] == "symbolic_proxy")]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.plot(budget["n"], budget["pool_checker_pass_rate_mean"], marker="o", label="checker pass in pool")
    ax.plot(budget["n"], budget["pool_execution_success_rate_mean"], marker="o", label="execution success in pool")
    ax.plot(
        budget["n"],
        budget["pool_valid_semantic_bad_rate_mean"],
        marker="o",
        label="checker-valid but semantic-bad",
    )
    ax.set_xscale("log", base=2)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("candidate budget N")
    ax.set_ylabel("rate")
    ax.set_title("Checker validity and execution validity diverge")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figure9_checker_executor_gap.png", dpi=220)
    plt.close(fig)


def run_suite(mode: str, output: Path) -> Dict[str, object]:
    config = suite_config(mode)
    output.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "expansion" if output.resolve() == (ROOT / "results" / "expansion").resolve() else output / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    budget = run_budget_stress(config)
    prior = run_loophole_prior_sweep(config)
    repair = run_repair_ablation(config)
    trials = pd.concat([budget, prior, repair], ignore_index=True, sort=False)
    summary = summarize_trials(trials)
    candidates = candidate_diagnostics(config)
    correlations = summarize_candidates(candidates)
    failures = failure_cases(trials)
    claims = build_claims(config, summary, candidates)

    trials.to_csv(output / "expanded_trials.csv", index=False)
    summary.to_csv(output / "expanded_summary.csv", index=False)
    candidates.to_csv(output / "candidate_diagnostics.csv", index=False)
    correlations.to_csv(output / "candidate_correlation_summary.csv", index=False)
    failures.to_csv(output / "failure_cases.csv", index=False)
    (output / "claims.json").write_text(json.dumps(claims, indent=2), encoding="utf-8")
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "mode": mode,
                "max_n": config.max_n,
                "budget_seeds": config.budget_seeds,
                "stress_seeds": config.stress_seeds,
                "candidate_seeds": config.candidate_seeds,
                "figures": [
                    "figure5_budget_512.png",
                    "figure6_loophole_prior.png",
                    "figure7_repair_ablation.png",
                    "figure8_proxy_calibration.png",
                    "figure9_checker_executor_gap.png",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    plot_budget(summary, fig_dir)
    plot_prior(summary, fig_dir)
    plot_repair(summary, fig_dir)
    plot_calibration(candidates, fig_dir)
    plot_checker_gap(summary, fig_dir)
    for figure in fig_dir.glob("figure*.png"):
        target = output / figure.name
        target.write_bytes(figure.read_bytes())

    return claims


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "expansion")
    args = parser.parse_args()
    claims = run_suite(args.mode, args.output)
    print(f"expansion suite complete: {args.mode}; claim_pass={claims['claim_pass']}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
