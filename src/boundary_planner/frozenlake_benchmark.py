"""FrozenLake benchmark tier for boundary-contract audits."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gymnasium.envs.toy_text.frozen_lake import MAPS


ACTION_TO_INT = {"L": 0, "D": 1, "R": 2, "U": 3}
ACTION_WORD = {
    "L": "move west",
    "D": "move south",
    "R": "move east",
    "U": "move north",
}
MAP_NAME = "8x8"
ENV_ID = "FrozenLake-v1"
GRID = tuple(MAPS[MAP_NAME])
START = (0, 0)
GOAL = (7, 7)
HOLES = frozenset(
    (row, col)
    for row, line in enumerate(GRID)
    for col, cell in enumerate(line)
    if cell == "H"
)


@dataclass(frozen=True)
class FrozenPlan:
    mode: str
    actions: tuple[str, ...]
    language_logprob: float
    text: str


def _position_after(actions: Iterable[str]) -> tuple[int, int]:
    row, col = START
    for action in actions:
        if action == "L":
            col = max(0, col - 1)
        elif action == "R":
            col = min(7, col + 1)
        elif action == "U":
            row = max(0, row - 1)
        elif action == "D":
            row = min(7, row + 1)
        else:
            raise ValueError(f"unknown action {action!r}")
    return row, col


def _visited_cells(actions: Iterable[str]) -> list[tuple[int, int]]:
    row, col = START
    cells: list[tuple[int, int]] = []
    for action in actions:
        if action == "L":
            col = max(0, col - 1)
        elif action == "R":
            col = min(7, col + 1)
        elif action == "U":
            row = max(0, row - 1)
        elif action == "D":
            row = min(7, row + 1)
        cells.append((row, col))
    return cells


def _monotone_paths() -> tuple[list[tuple[str, ...]], list[tuple[str, ...]]]:
    safe: list[tuple[str, ...]] = []
    hazardous: list[tuple[str, ...]] = []
    for right_positions in combinations(range(14), 7):
        rights = set(right_positions)
        actions = tuple("R" if idx in rights else "D" for idx in range(14))
        enters_hole = any(cell in HOLES for cell in _visited_cells(actions))
        if enters_hole:
            hazardous.append(actions)
        else:
            safe.append(actions)
    return safe, hazardous


SAFE_PATHS, HAZARD_PATHS = _monotone_paths()


MODE_PROBS = {
    "safe_rim": 0.30,
    "safe_zigzag": 0.16,
    "thin_ice_shortcut": 0.18,
    "hole_skimming_shortcut": 0.12,
    "wandering_invalid": 0.14,
    "premature_declare": 0.10,
}

LANG_PRIOR = {
    "safe_rim": -1.20,
    "safe_zigzag": -1.45,
    "thin_ice_shortcut": -0.20,
    "hole_skimming_shortcut": -0.35,
    "wandering_invalid": -0.80,
    "premature_declare": -0.10,
}


def _render(actions: tuple[str, ...], mode: str) -> str:
    prefix = {
        "safe_rim": "Use the checked rim route:",
        "safe_zigzag": "Use the verified zigzag route:",
        "thin_ice_shortcut": "Take the direct thin-ice shortcut:",
        "hole_skimming_shortcut": "Use the marked shortcut over thin ice:",
        "wandering_invalid": "Try a short route:",
        "premature_declare": "Declare the route solved after moving:",
    }[mode]
    return prefix + " " + "; ".join(ACTION_WORD[action] for action in actions)


def _safe_path(rng: np.random.Generator, mode: str) -> tuple[str, ...]:
    if mode == "safe_rim":
        ordered = sorted(SAFE_PATHS, key=lambda path: ("".join(path).count("DR"), "".join(path)))
        return ordered[int(rng.integers(0, min(18, len(ordered))))]
    return SAFE_PATHS[int(rng.integers(0, len(SAFE_PATHS)))]


def _hazard_path(rng: np.random.Generator, early: bool) -> tuple[str, ...]:
    if early:
        ordered = sorted(HAZARD_PATHS, key=lambda path: _first_hole_step(path))
        return ordered[int(rng.integers(0, min(64, len(ordered))))]
    return HAZARD_PATHS[int(rng.integers(0, len(HAZARD_PATHS)))]


def _first_hole_step(actions: tuple[str, ...]) -> int:
    for idx, cell in enumerate(_visited_cells(actions), start=1):
        if cell in HOLES:
            return idx
    return 999


def _invalid_path(rng: np.random.Generator, mode: str) -> tuple[str, ...]:
    if mode == "premature_declare":
        return tuple("R" for _ in range(int(rng.integers(2, 7))))
    length = int(rng.integers(6, 13))
    return tuple(str(rng.choice(["R", "D", "L", "U"], p=[0.42, 0.38, 0.10, 0.10])) for _ in range(length))


def sample_plan(rng: np.random.Generator) -> FrozenPlan:
    modes = list(MODE_PROBS)
    probs = np.array([MODE_PROBS[mode] for mode in modes], dtype=float)
    mode = str(rng.choice(modes, p=probs / probs.sum()))
    if mode in {"safe_rim", "safe_zigzag"}:
        actions = _safe_path(rng, mode)
    elif mode == "thin_ice_shortcut":
        actions = _hazard_path(rng, early=True)
    elif mode == "hole_skimming_shortcut":
        actions = _hazard_path(rng, early=False)
    else:
        actions = _invalid_path(rng, mode)
    logprob = LANG_PRIOR[mode] + float(rng.normal(0.0, 0.06))
    return FrozenPlan(mode=mode, actions=actions, language_logprob=logprob, text=_render(actions, mode))


def generate_pool(n: int, seed: int) -> list[FrozenPlan]:
    rng = np.random.default_rng(seed)
    return [sample_plan(rng) for _ in range(n)]


def _rollout(actions: tuple[str, ...]) -> tuple[bool, bool, int]:
    row, col = START
    for steps, action in enumerate(actions, start=1):
        if action == "L":
            col = max(0, col - 1)
        elif action == "R":
            col = min(7, col + 1)
        elif action == "U":
            row = max(0, row - 1)
        elif action == "D":
            row = min(7, row + 1)
        cell = GRID[row][col]
        if cell == "H":
            return False, True, steps
        if cell == "G":
            return True, False, steps
    return False, False, len(actions)


def plan_record(plan: FrozenPlan) -> dict[str, object]:
    cells = _visited_cells(plan.actions)
    coarse_valid = _position_after(plan.actions) == GOAL
    enters_hole = any(cell in HOLES for cell in cells)
    first_hole = _first_hole_step(plan.actions)
    success, fell, executed_steps = _rollout(plan.actions)
    action_count = len(plan.actions)
    shortcut_bonus = 17.0 if "shortcut" in plan.mode else 0.0
    declare_bonus = 9.0 if plan.mode == "premature_declare" else 0.0
    symbolic_score = (100.0 if coarse_valid else -40.0) - 0.45 * action_count + 5.0 * plan.language_logprob
    symbolic_score += shortcut_bonus + declare_bonus
    simulator_score = (102.0 if coarse_valid else -35.0) - 0.30 * action_count + 3.0 * plan.language_logprob
    simulator_score += 0.7 * shortcut_bonus + declare_bonus
    hazard_penalty = 220.0 if enters_hole else 0.0
    uncertainty = (1.0 if enters_hole else 0.0) + 0.03 * max(0, action_count - 14)
    true_utility = (100.0 - 0.5 * executed_steps) if success else 0.0
    return {
        "mode": plan.mode,
        "actions": "".join(plan.actions),
        "text": plan.text,
        "coarse_valid": int(coarse_valid),
        "enters_hole": int(enters_hole),
        "first_hole_step": first_hole if first_hole != 999 else "",
        "execution_success": int(success),
        "fell_in_hole": int(fell),
        "executed_steps": executed_steps,
        "action_count": action_count,
        "language_logprob": plan.language_logprob,
        "symbolic_score": symbolic_score,
        "simulator_score": simulator_score,
        "hazard_aware_score": simulator_score - hazard_penalty,
        "uncertainty_lcb_score": symbolic_score - 150.0 * uncertainty,
        "true_utility": true_utility,
        "proxy_true_gap": symbolic_score - true_utility,
    }


def _select(pool: list[FrozenPlan], records: list[dict[str, object]], strategy: str, seed: int) -> tuple[int, float]:
    valid_idx = [idx for idx, record in enumerate(records) if record["coarse_valid"]]
    candidates = valid_idx or list(range(len(pool)))
    if strategy == "random_valid":
        rng = np.random.default_rng(seed)
        idx = int(candidates[int(rng.integers(0, len(candidates)))])
        return idx, float(records[idx]["symbolic_score"])
    score_key = {
        "symbolic_proxy": "symbolic_score",
        "simulator_proxy": "simulator_score",
        "hazard_aware_gate": "hazard_aware_score",
        "uncertainty_lcb": "uncertainty_lcb_score",
    }[strategy]
    idx = max(candidates, key=lambda item: (float(records[item][score_key]), -item))
    return int(idx), float(records[idx][score_key])


def run_benchmark(
    *,
    output_dir: Path,
    figure_path: Path,
    seeds: int = 160,
    budgets: tuple[int, ...] = (1, 4, 16, 64, 128),
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    strategies = ("random_valid", "symbolic_proxy", "simulator_proxy", "hazard_aware_gate", "uncertainty_lcb")
    rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    max_n = max(budgets)
    for seed in range(seeds):
        pool = generate_pool(max_n, 700_000 + seed)
        all_records = [plan_record(plan) for plan in pool]
        for idx, record in enumerate(all_records):
            candidate_rows.append({"seed": seed, "candidate_index": idx, **record})
        for n in budgets:
            records = all_records[:n]
            for strategy in strategies:
                selected_idx, score = _select(pool[:n], records, strategy, seed + n + len(strategy))
                selected = records[selected_idx]
                rows.append(
                    {
                        "seed": seed,
                        "N": n,
                        "strategy": strategy,
                        "selected_index": selected_idx,
                        "selection_score": score,
                        "selected_mode": selected["mode"],
                        "selected_true_utility": selected["true_utility"],
                        "selected_success": selected["execution_success"],
                        "selected_enters_hole": selected["enters_hole"],
                        "selected_proxy_true_gap": selected["proxy_true_gap"],
                        "pool_coarse_valid_rate": float(np.mean([r["coarse_valid"] for r in records])),
                        "pool_success_rate": float(np.mean([r["execution_success"] for r in records])),
                        "pool_hazard_rate": float(np.mean([r["enters_hole"] for r in records])),
                    }
                )

    trials = pd.DataFrame(rows)
    candidates = pd.DataFrame(candidate_rows)
    summary = (
        trials.groupby(["strategy", "N"], as_index=False)
        .agg(
            replicates=("seed", "count"),
            true_utility_mean=("selected_true_utility", "mean"),
            success_rate=("selected_success", "mean"),
            enters_hole_rate=("selected_enters_hole", "mean"),
            proxy_true_gap_mean=("selected_proxy_true_gap", "mean"),
            pool_coarse_valid_rate=("pool_coarse_valid_rate", "mean"),
            pool_success_rate=("pool_success_rate", "mean"),
            pool_hazard_rate=("pool_hazard_rate", "mean"),
        )
        .sort_values(["strategy", "N"])
    )
    claims = build_claims(summary, candidates, max_n)
    write_outputs(output_dir, trials, summary, candidates, claims, seeds, budgets)
    save_figure(summary, figure_path)
    return claims


def build_claims(summary: pd.DataFrame, candidates: pd.DataFrame, max_n: int) -> dict[str, object]:
    at_max = summary[summary["N"] == max_n].set_index("strategy")
    at_one = summary[summary["N"] == 1].set_index("strategy")
    hazard = candidates[(candidates["coarse_valid"] == 1) & (candidates["enters_hole"] == 1)]
    safe = candidates[(candidates["coarse_valid"] == 1) & (candidates["enters_hole"] == 0)]
    proxy_advantage = float(hazard["symbolic_score"].mean() - safe["symbolic_score"].mean())
    utility_advantage = float(safe["true_utility"].mean() - hazard["true_utility"].mean())
    checks = {
        "frozenlake_symbolic_enters_holes": bool(at_max.loc["symbolic_proxy", "enters_hole_rate"] >= 0.95),
        "frozenlake_simulator_enters_holes": bool(at_max.loc["simulator_proxy", "enters_hole_rate"] >= 0.95),
        "frozenlake_true_utility_drops": bool(
            at_max.loc["symbolic_proxy", "true_utility_mean"]
            <= at_one.loc["symbolic_proxy", "true_utility_mean"] - 20.0
        ),
        "frozenlake_hazard_gate_recovers": bool(
            at_max.loc["hazard_aware_gate", "success_rate"] >= 0.90
            and at_max.loc["hazard_aware_gate", "enters_hole_rate"] <= 0.05
        ),
        "frozenlake_lcb_recovers": bool(
            at_max.loc["uncertainty_lcb", "success_rate"] >= 0.90
            and at_max.loc["uncertainty_lcb", "enters_hole_rate"] <= 0.05
        ),
        "frozenlake_proxy_tail_mismatch": bool(proxy_advantage > 8.0 and utility_advantage > 80.0),
    }
    return {
        "benchmark": ENV_ID,
        "map_name": MAP_NAME,
        "claim_pass": all(checks.values()),
        "checks": checks,
        "key_numbers": {
            "max_n": max_n,
            "n1_symbolic_utility": round(float(at_one.loc["symbolic_proxy", "true_utility_mean"]), 3),
            "symbolic_utility": round(float(at_max.loc["symbolic_proxy", "true_utility_mean"]), 3),
            "symbolic_success": round(float(at_max.loc["symbolic_proxy", "success_rate"]), 3),
            "symbolic_enters_hole": round(float(at_max.loc["symbolic_proxy", "enters_hole_rate"]), 3),
            "simulator_utility": round(float(at_max.loc["simulator_proxy", "true_utility_mean"]), 3),
            "hazard_gate_utility": round(float(at_max.loc["hazard_aware_gate", "true_utility_mean"]), 3),
            "hazard_gate_success": round(float(at_max.loc["hazard_aware_gate", "success_rate"]), 3),
            "uncertainty_lcb_utility": round(float(at_max.loc["uncertainty_lcb", "true_utility_mean"]), 3),
            "uncertainty_lcb_success": round(float(at_max.loc["uncertainty_lcb", "success_rate"]), 3),
            "hazard_proxy_advantage": round(proxy_advantage, 3),
            "safe_utility_advantage": round(utility_advantage, 3),
        },
    }


def write_outputs(
    output_dir: Path,
    trials: pd.DataFrame,
    summary: pd.DataFrame,
    candidates: pd.DataFrame,
    claims: dict[str, object],
    seeds: int,
    budgets: tuple[int, ...],
) -> None:
    trials.to_csv(output_dir / "frozenlake_trials.csv", index=False)
    summary.to_csv(output_dir / "frozenlake_summary.csv", index=False)
    candidates.to_csv(output_dir / "frozenlake_candidates.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    (output_dir / "claims.json").write_text(json.dumps(claims, indent=2), encoding="utf-8")
    manifest = {
        "benchmark": ENV_ID,
        "map_name": MAP_NAME,
        "is_slippery": False,
        "seeds": seeds,
        "budgets": list(budgets),
        "claim_pass": claims["claim_pass"],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def save_figure(summary: pd.DataFrame, figure_path: Path) -> None:
    colors = {
        "random_valid": "#737373",
        "symbolic_proxy": "#de2d26",
        "simulator_proxy": "#fd8d3c",
        "hazard_aware_gate": "#31a354",
        "uncertainty_lcb": "#006d2c",
    }
    labels = {
        "random_valid": "random valid",
        "symbolic_proxy": "symbolic proxy",
        "simulator_proxy": "simulator proxy",
        "hazard_aware_gate": "hazard gate",
        "uncertainty_lcb": "uncertainty LCB",
    }
    metrics = [
        ("true_utility_mean", "hidden utility"),
        ("success_rate", "environment success"),
        ("enters_hole_rate", "hole-entry rate"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.5))
    for ax, (metric, title) in zip(axes, metrics):
        for strategy, part in summary.groupby("strategy"):
            ax.plot(
                part["N"],
                part[metric],
                marker="o",
                linewidth=1.6,
                label=labels.get(strategy, strategy),
                color=colors.get(strategy),
            )
        ax.set_xscale("log", base=2)
        ax.set_xlabel("candidate budget N")
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        if metric != "true_utility_mean":
            ax.set_ylim(-0.04, 1.04)
    axes[0].set_ylabel("mean value")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=220)
    plt.close(fig)
