"""Generate machine-readable claim status from local experiment outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=["smoke", "full"], default="full")
    args = parser.parse_args()
    summary_path = ROOT / "results" / args.preset / "summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing {summary_path}; run experiments first")

    summary = pd.read_csv(summary_path)
    max_n = int(summary["n"].max())
    at_max = summary[summary["n"] == max_n].set_index("strategy")
    symbolic = at_max.loc["symbolic_proxy"]
    simulator = at_max.loc["simulator_proxy"]
    adv = at_max.loc["adversarial_gate"]
    lcb = at_max.loc["uncertainty_lcb"]
    best_repair_name = (
        at_max.loc[["calibrated_boundary", "adversarial_gate", "uncertainty_lcb"], "mean_true_utility"].idxmax()
    )
    best_repair = at_max.loc[best_repair_name]

    claims = {
        "preset": args.preset,
        "max_n": max_n,
        "claim_boundary": "controlled synthetic language/symbolic planner domains only",
        "supported": {
            "symbolic_proxy_concentrates_loopholes": bool(symbolic["loophole_rate"] >= 0.9),
            "simulator_proxy_concentrates_loopholes": bool(simulator["loophole_rate"] >= 0.9),
            "repairs_reduce_loopholes": bool(best_repair["loophole_rate"] <= 0.1),
            "repairs_restore_execution_success": bool(best_repair["success_rate"] >= 0.9),
        },
        "numbers": {
            "symbolic_proxy_true_utility": round(float(symbolic["mean_true_utility"]), 3),
            "symbolic_proxy_loophole_rate": pct(float(symbolic["loophole_rate"])),
            "symbolic_proxy_proxy_true_gap": round(float(symbolic["mean_proxy_true_gap"]), 3),
            "simulator_proxy_true_utility": round(float(simulator["mean_true_utility"]), 3),
            "simulator_proxy_loophole_rate": pct(float(simulator["loophole_rate"])),
            "adversarial_gate_true_utility": round(float(adv["mean_true_utility"]), 3),
            "uncertainty_lcb_true_utility": round(float(lcb["mean_true_utility"]), 3),
            "best_repair": str(best_repair_name),
            "best_repair_true_utility": round(float(best_repair["mean_true_utility"]), 3),
            "best_repair_success_rate": pct(float(best_repair["success_rate"])),
            "best_repair_loophole_rate": pct(float(best_repair["loophole_rate"])),
        },
        "unsupported": [
            "real-robot safety claims",
            "claims about arbitrary external verifiers",
            "claims that symbolic planning is intrinsically unsafe",
            "claims that semantic uncertainty penalties are a complete solution",
        ],
    }
    out_json = ROOT / "docs" / "claims.json"
    out_md = ROOT / "docs" / "claim_audit.md"
    out_json.write_text(json.dumps(claims, indent=2), encoding="utf-8")
    out_md.write_text(
        "# Claim Audit\n\n"
        f"Preset: `{args.preset}`. Max N: `{max_n}`.\n\n"
        "## Supported\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in claims["supported"].items())
        + "\n\n## Key Numbers\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in claims["numbers"].items())
        + "\n\n## Unsupported\n\n"
        + "\n".join(f"- {item}" for item in claims["unsupported"])
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
