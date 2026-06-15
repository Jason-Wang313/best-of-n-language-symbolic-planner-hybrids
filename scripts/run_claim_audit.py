"""Generate machine-readable claim status from local experiment outputs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPANSION_CLAIMS = ROOT / "results" / "expansion" / "claims.json"
FROZENLAKE_CLAIMS = ROOT / "results" / "frozenlake_benchmark" / "claims.json"
PAPER = ROOT / "paper" / "main.tex"
REPO_PDF = ROOT / "paper" / "final" / "best-of-n-language-symbolic-planner-hybrids-v4.pdf"
DESKTOP_PDF = Path.home() / "OneDrive" / "Desktop" / "best-of-n-language-symbolic-planner-hybrids-v4.pdf"

STALE_PATTERNS = [
    "best-of-n-language-symbolic-planner-hybrids-" + "v" + "2",
    "best-of-n-language-symbolic-planner-hybrids-" + "v" + "3",
    "submission-ready " + "v" + "3",
    "v" + "3" + " filename",
    "best of n llm",
    "inference value theorem",
    "iclr_submission",
]


def pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def _pdf_page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=["smoke", "full"], default="full")
    args = parser.parse_args()
    failures: list[str] = []
    expansion: dict | None = None
    frozenlake: dict | None = None
    summary_path = ROOT / "results" / args.preset / "summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing {summary_path}; run experiments first")
    if EXPANSION_CLAIMS.exists():
        expansion = json.loads(EXPANSION_CLAIMS.read_text(encoding="utf-8"))
    if FROZENLAKE_CLAIMS.exists():
        frozenlake = json.loads(FROZENLAKE_CLAIMS.read_text(encoding="utf-8"))

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
        "version": "v4",
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
        "stress_expansion": expansion,
        "frozenlake_benchmark": frozenlake,
    }
    out_json = ROOT / "docs" / "claims.json"
    out_md = ROOT / "docs" / "claim_audit.md"
    out_json.write_text(json.dumps(claims, indent=2), encoding="utf-8")
    expansion_checks = expansion.get("checks", {}) if expansion else {}
    expansion_numbers = expansion.get("key_numbers", {}) if expansion else {}
    expansion_block = (
        "## Expansion Checks\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in expansion_checks.items())
        + "\n\n## Expansion Key Numbers\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in expansion_numbers.items())
        + "\n\n"
        if expansion
        else "## Expansion Checks\n\n- missing expansion claims\n\n"
    )
    frozenlake_checks = frozenlake.get("checks", {}) if frozenlake else {}
    frozenlake_numbers = frozenlake.get("key_numbers", {}) if frozenlake else {}
    frozenlake_block = (
        "## FrozenLake Checks\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in frozenlake_checks.items())
        + "\n\n## FrozenLake Key Numbers\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in frozenlake_numbers.items())
        + "\n\n"
        if frozenlake
        else "## FrozenLake Checks\n\n- missing FrozenLake claims\n\n"
    )
    out_md.write_text(
        "# Claim Audit\n\n"
        f"Version: `v4`. Baseline preset: `{args.preset}`. Baseline max N: `{max_n}`. "
        f"Expansion max N: `{expansion_numbers.get('max_n', 'missing')}`. "
        f"FrozenLake max N: `{frozenlake_numbers.get('max_n', 'missing')}`.\n\n"
        + expansion_block
        + frozenlake_block
        + "## Baseline Supported Checks\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in claims["supported"].items())
        + "\n\n## Baseline Key Numbers\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in claims["numbers"].items())
        + "\n\n## Unsupported\n\n"
        + "\n".join(f"- {item}" for item in claims["unsupported"])
        + "\n\n## Final PDF Targets\n\n"
        + f"- repository: `{REPO_PDF}`\n"
        + f"- desktop: `{DESKTOP_PDF}`\n"
        + "- minimum pages: 25\n",
        encoding="utf-8",
    )
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")

    if expansion is None:
        failures.append(f"missing expansion claims: {EXPANSION_CLAIMS}")
    else:
        if expansion.get("claim_pass") is not True:
            failures.append("expansion claim_pass is false")
        for name, value in expansion.get("checks", {}).items():
            if value is not True:
                failures.append(f"expansion check failed: {name}={value}")

    if frozenlake is None:
        failures.append(f"missing FrozenLake claims: {FROZENLAKE_CLAIMS}")
    else:
        if frozenlake.get("claim_pass") is not True:
            failures.append("FrozenLake claim_pass is false")
        for name, value in frozenlake.get("checks", {}).items():
            if value is not True:
                failures.append(f"FrozenLake check failed: {name}={value}")

    if PAPER.exists():
        paper_text = PAPER.read_text(encoding="utf-8").lower()
        for pattern in STALE_PATTERNS:
            if pattern.lower() in paper_text:
                failures.append(f"stale text found in paper: {pattern}")
    else:
        failures.append(f"missing paper source: {PAPER}")

    for pdf in [REPO_PDF, DESKTOP_PDF]:
        if not pdf.exists():
            failures.append(f"missing PDF: {pdf}")
            continue
        pages = _pdf_page_count(pdf)
        if pages < 25:
            failures.append(f"PDF has only {pages} pages: {pdf}")

    if failures:
        print("submission audit failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("submission audit complete: v4")


if __name__ == "__main__":
    main()
