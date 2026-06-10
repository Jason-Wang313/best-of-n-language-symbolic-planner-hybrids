"""Run controlled Best-of-N language/symbolic planner experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Iterable, List

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bon_symbolic import STRATEGIES, TASKS, select_plan
from bon_symbolic.generator import generate_pool
from bon_symbolic.metrics import plan_record, pool_diagnostics


def parse_ns(value: str) -> List[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def preset_config(preset: str) -> tuple[int, List[int]]:
    if preset == "smoke":
        return 24, [1, 2, 4, 8, 16, 32]
    if preset == "full":
        return 96, [1, 2, 4, 8, 16, 32, 64, 128]
    raise ValueError(f"unknown preset {preset!r}")


def run_trials(seeds: int, ns: Iterable[int]) -> pd.DataFrame:
    rows = []
    max_n = max(ns)
    for task_index, task_name in enumerate(TASKS):
        for seed in range(seeds):
            base_seed = 10_000 * task_index + seed
            max_pool = generate_pool(task_name, max_n, seed=base_seed)
            for n in ns:
                pool = max_pool[:n]
                pool_diag = pool_diagnostics(pool)
                for strategy in STRATEGIES:
                    selection = select_plan(pool, strategy, seed=base_seed + n + len(strategy))
                    record = plan_record(selection.plan)
                    rows.append(
                        {
                            "task": task_name,
                            "seed": seed,
                            "n": n,
                            "strategy": strategy,
                            "selected_index": selection.selected_index,
                            "selection_score": selection.score,
                            **pool_diag,
                            **{f"selected_{k}": v for k, v in record.items()},
                        }
                    )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["strategy", "n"], as_index=False)
        .agg(
            mean_true_utility=("selected_true_utility", "mean"),
            std_true_utility=("selected_true_utility", "std"),
            success_rate=("selected_execution_success", "mean"),
            semantic_bad_rate=("selected_semantic_bad", "mean"),
            loophole_rate=("selected_loophole", "mean"),
            mean_proxy_true_gap=("selected_proxy_true_gap", "mean"),
            mean_pool_pass_rate=("pool_checker_pass_rate", "mean"),
            mean_pool_exec_success_rate=("pool_execution_success_rate", "mean"),
            mean_pool_valid_semantic_bad_rate=("pool_valid_semantic_bad_rate", "mean"),
        )
        .sort_values(["strategy", "n"])
    )
    return grouped


def save_figures(summary: pd.DataFrame, df: pd.DataFrame, fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "random_valid": "#737373",
        "language_prior": "#8c6bb1",
        "symbolic_bon": "#de2d26",
        "simulator_bon": "#fd8d3c",
        "calibrated_bon": "#3182bd",
        "adversarial_gate": "#31a354",
        "uncertainty_lcb": "#006d2c",
    }

    plt.figure(figsize=(7.2, 4.4))
    for strategy, part in summary.groupby("strategy"):
        plt.plot(
            part["n"],
            part["mean_true_utility"],
            marker="o",
            label=strategy.replace("_", " "),
            color=colors.get(strategy),
        )
    plt.xscale("log", base=2)
    plt.xlabel("candidate budget N")
    plt.ylabel("selected plan true utility")
    plt.title("Best-of-N scaling under semantic-symbolic mismatch")
    plt.grid(True, alpha=0.25)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(fig_dir / "figure1_best_of_n_collapse.png", dpi=220)
    plt.close()

    plt.figure(figsize=(7.2, 4.4))
    for strategy, part in summary.groupby("strategy"):
        plt.plot(
            part["n"],
            part["loophole_rate"],
            marker="o",
            label=strategy.replace("_", " "),
            color=colors.get(strategy),
        )
    plt.xscale("log", base=2)
    plt.ylim(-0.03, 1.03)
    plt.xlabel("candidate budget N")
    plt.ylabel("selected loophole occupancy")
    plt.title("Verifier selection concentrates rare loopholes")
    plt.grid(True, alpha=0.25)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(fig_dir / "figure2_loophole_occupancy.png", dpi=220)
    plt.close()

    pool_by_n = (
        df.groupby("n", as_index=False)
        .agg(
            checker_pass=("pool_checker_pass_rate", "mean"),
            execution_success=("pool_execution_success_rate", "mean"),
            valid_semantic_bad=("pool_valid_semantic_bad_rate", "mean"),
        )
        .sort_values("n")
    )
    plt.figure(figsize=(6.8, 4.2))
    plt.plot(pool_by_n["n"], pool_by_n["checker_pass"], marker="o", label="checker pass rate", color="#756bb1")
    plt.plot(
        pool_by_n["n"],
        pool_by_n["execution_success"],
        marker="o",
        label="execution success in pool",
        color="#2b8cbe",
    )
    plt.plot(
        pool_by_n["n"],
        pool_by_n["valid_semantic_bad"],
        marker="o",
        label="valid but semantically bad",
        color="#e6550d",
    )
    plt.xscale("log", base=2)
    plt.ylim(-0.03, 1.03)
    plt.xlabel("candidate budget N")
    plt.ylabel("rate")
    plt.title("Symbolic validity and execution validity diverge")
    plt.grid(True, alpha=0.25)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(fig_dir / "figure3_checker_executor_gap.png", dpi=220)
    plt.close()

    max_n = int(summary["n"].max())
    ladder = summary[summary["n"] == max_n].copy()
    order = [
        "random_valid",
        "language_prior",
        "symbolic_bon",
        "simulator_bon",
        "calibrated_bon",
        "adversarial_gate",
        "uncertainty_lcb",
    ]
    ladder["strategy"] = pd.Categorical(ladder["strategy"], categories=order, ordered=True)
    ladder = ladder.sort_values("strategy")
    fig, ax1 = plt.subplots(figsize=(7.4, 4.5))
    ax1.bar(
        ladder["strategy"].astype(str).str.replace("_", "\n"),
        ladder["mean_true_utility"],
        color=[colors.get(str(s), "#999999") for s in ladder["strategy"]],
        alpha=0.86,
    )
    ax1.set_ylabel("true utility")
    ax1.set_title(f"Repair ladder at N={max_n}")
    ax1.tick_params(axis="x", labelsize=8)
    ax2 = ax1.twinx()
    ax2.plot(
        ladder["strategy"].astype(str).str.replace("_", "\n"),
        ladder["loophole_rate"],
        color="#111111",
        marker="D",
        linewidth=1.5,
        label="loophole rate",
    )
    ax2.set_ylim(-0.03, 1.03)
    ax2.set_ylabel("loophole rate")
    fig.tight_layout()
    fig.savefig(fig_dir / "figure4_repair_ladder.png", dpi=220)
    plt.close(fig)


def write_json_summary(summary: pd.DataFrame, out_dir: Path, preset: str, seeds: int, ns: List[int]) -> None:
    max_n = max(ns)
    at_max = summary[summary["n"] == max_n].set_index("strategy")
    payload = {
        "preset": preset,
        "seeds": seeds,
        "ns": ns,
        "max_n": max_n,
        "symbolic_bon_utility_at_max_n": float(at_max.loc["symbolic_bon", "mean_true_utility"]),
        "symbolic_bon_loophole_at_max_n": float(at_max.loc["symbolic_bon", "loophole_rate"]),
        "simulator_bon_utility_at_max_n": float(at_max.loc["simulator_bon", "mean_true_utility"]),
        "adversarial_gate_utility_at_max_n": float(at_max.loc["adversarial_gate", "mean_true_utility"]),
        "uncertainty_lcb_utility_at_max_n": float(at_max.loc["uncertainty_lcb", "mean_true_utility"]),
        "best_repair_at_max_n": str(
            at_max.loc[["calibrated_bon", "adversarial_gate", "uncertainty_lcb"], "mean_true_utility"].idxmax()
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--ns", type=parse_ns, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--figures", type=Path, default=None)
    args = parser.parse_args()

    default_seeds, default_ns = preset_config(args.preset)
    seeds = args.seeds or default_seeds
    ns = args.ns or default_ns
    out_dir = args.out or ROOT / "results" / args.preset
    fig_dir = args.figures or ROOT / "figures" / args.preset
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = run_trials(seeds, ns)
    summary = summarize(df)
    df.to_csv(out_dir / "rollouts.csv", index=False)
    summary.to_csv(out_dir / "summary.csv", index=False)
    write_json_summary(summary, out_dir, args.preset, seeds, ns)
    save_figures(summary, df, fig_dir)
    print(f"wrote {out_dir / 'summary.csv'}")
    print(f"wrote figures to {fig_dir}")


if __name__ == "__main__":
    main()
