"""Build the anonymous paper PDF and copy it to the visible Desktop."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DESKTOP = Path.home() / "OneDrive" / "Desktop"
if not DESKTOP.exists():
    DESKTOP = Path.home() / "Desktop"
FINAL_PDF = DESKTOP / "best-of-n-language-symbolic-planner-hybrids-v2.pdf"


def macro(name: str, value: str) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}\n"


def write_result_macros() -> None:
    summary_path = ROOT / "results" / "full" / "summary.csv"
    if not summary_path.exists():
        summary_path = ROOT / "results" / "smoke" / "summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError("missing experiment summary; run scripts/run_smoke.ps1 or scripts/run_all.ps1 first")

    summary = pd.read_csv(summary_path)
    max_n = int(summary["n"].max())
    at_max = summary[summary["n"] == max_n].set_index("strategy")
    symbolic_n1 = summary[(summary["strategy"] == "symbolic_proxy") & (summary["n"] == 1)].iloc[0]
    symbolic = at_max.loc["symbolic_proxy"]
    simulator = at_max.loc["simulator_proxy"]
    calibrated = at_max.loc["calibrated_boundary"]
    adversarial = at_max.loc["adversarial_gate"]
    lcb = at_max.loc["uncertainty_lcb"]
    best_repair_name = (
        at_max.loc[["calibrated_boundary", "adversarial_gate", "uncertainty_lcb"], "mean_true_utility"].idxmax()
    )
    best_repair = at_max.loc[best_repair_name]

    text = ""
    text += macro("ResultPreset", summary_path.parent.name)
    text += macro("MaxN", str(max_n))
    text += macro("SymbolicNOneUtility", f"{float(symbolic_n1['mean_true_utility']):.1f}")
    text += macro("SymbolicMaxUtility", f"{float(symbolic['mean_true_utility']):.1f}")
    text += macro("SymbolicMaxLoophole", f"{100.0 * float(symbolic['loophole_rate']):.1f}\\%")
    text += macro("SymbolicGap", f"{float(symbolic['mean_proxy_true_gap']):.1f}")
    text += macro("SimulatorMaxUtility", f"{float(simulator['mean_true_utility']):.1f}")
    text += macro("SimulatorMaxLoophole", f"{100.0 * float(simulator['loophole_rate']):.1f}\\%")
    text += macro("CalibratedUtility", f"{float(calibrated['mean_true_utility']):.1f}")
    text += macro("AdversarialUtility", f"{float(adversarial['mean_true_utility']):.1f}")
    text += macro("LCBUtility", f"{float(lcb['mean_true_utility']):.1f}")
    text += macro("BestRepairName", best_repair_name.replace("_", "\\_"))
    text += macro("BestRepairUtility", f"{float(best_repair['mean_true_utility']):.1f}")
    text += macro("BestRepairSuccess", f"{100.0 * float(best_repair['success_rate']):.1f}\\%")
    text += macro("BestRepairLoophole", f"{100.0 * float(best_repair['loophole_rate']):.1f}\\%")
    (PAPER / "results_macros.tex").write_text(text, encoding="utf-8")


def run_latex() -> Path:
    PAPER.mkdir(exist_ok=True)
    for pattern in ["main.aux", "main.out", "main.log", "main.bbl", "main.blg", "main.fls", "main.fdb_latexmk"]:
        path = PAPER / pattern
        if path.exists():
            path.unlink()
    commands = [
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    ]
    errors = []
    for command in commands:
        exe = shutil.which(command[0])
        if exe is None:
            errors.append(f"{command[0]} not found")
            continue
        try:
            subprocess.run(command, cwd=PAPER, check=True, text=True, capture_output=True)
            if command[0] == "pdflatex":
                subprocess.run(command, cwd=PAPER, check=True, text=True, capture_output=True)
            pdf = PAPER / "main.pdf"
            if pdf.exists():
                local_pdf = PAPER / "best-of-n-language-symbolic-planner-hybrids.pdf"
                shutil.copy2(pdf, local_pdf)
                shutil.copy2(pdf, FINAL_PDF)
                return FINAL_PDF
        except subprocess.CalledProcessError as exc:
            errors.append(f"{' '.join(command)}\nSTDOUT:\n{exc.stdout}\nSTDERR:\n{exc.stderr}")
    failure = ROOT / "docs" / "paper_build_failure.md"
    failure.write_text("# Paper Build Failure\n\n" + "\n\n".join(errors), encoding="utf-8")
    raise RuntimeError(f"paper build failed; see {failure}")


def main() -> None:
    write_result_macros()
    pdf = run_latex()
    print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
