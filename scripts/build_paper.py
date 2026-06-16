"""Build the anonymous paper PDF and copy it to the visible Desktop."""

from __future__ import annotations

import shutil
import subprocess
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DESKTOP = Path.home() / "OneDrive" / "Desktop"
if not DESKTOP.exists():
    DESKTOP = Path.home() / "Desktop"
DESKTOP_PDF = DESKTOP / "best-of-n-language-symbolic-planner-hybrids-v4.pdf"
REPO_FINAL = PAPER / "final" / "best-of-n-language-symbolic-planner-hybrids-v4.pdf"


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
    expansion_claims = ROOT / "results" / "expansion" / "claims.json"
    if expansion_claims.exists():
        claims = json.loads(expansion_claims.read_text(encoding="utf-8"))
        numbers = claims["key_numbers"]
        text += macro("StressMaxN", str(numbers["max_n"]))
        text += macro("StressSymbolicUtility", f"{float(numbers['symbolic_proxy_utility']):.1f}")
        text += macro("StressSymbolicLoophole", f"{100.0 * float(numbers['symbolic_proxy_loophole']):.1f}\\%")
        text += macro("StressSymbolicSuccess", f"{100.0 * float(numbers['symbolic_proxy_success']):.1f}\\%")
        text += macro("StressSimulatorUtility", f"{float(numbers['simulator_proxy_utility']):.1f}")
        text += macro("StressAdversarialUtility", f"{float(numbers['adversarial_gate_utility']):.1f}")
        text += macro("StressLCBUtility", f"{float(numbers['uncertainty_lcb_utility']):.1f}")
        text += macro("StressRarePriorLoophole", f"{100.0 * float(numbers['rare_prior_symbolic_loophole']):.1f}\\%")
        text += macro("StressStrictSuccess", f"{100.0 * float(numbers['strict_boundary_success']):.1f}\\%")
        text += macro("StressProxyAdvantage", f"{float(numbers['loophole_proxy_advantage']):.1f}")
        text += macro("StressGroundedAdvantage", f"{float(numbers['grounded_utility_advantage']):.1f}")
    frozenlake_claims = ROOT / "results" / "frozenlake_benchmark" / "claims.json"
    if frozenlake_claims.exists():
        claims = json.loads(frozenlake_claims.read_text(encoding="utf-8"))
        numbers = claims["key_numbers"]
        text += macro("FrozenMaxN", str(numbers["max_n"]))
        text += macro("FrozenNOneUtility", f"{float(numbers['n1_symbolic_utility']):.1f}")
        text += macro("FrozenSymbolicUtility", f"{float(numbers['symbolic_utility']):.1f}")
        text += macro("FrozenSymbolicSuccess", f"{100.0 * float(numbers['symbolic_success']):.1f}\\%")
        text += macro("FrozenSymbolicHole", f"{100.0 * float(numbers['symbolic_enters_hole']):.1f}\\%")
        text += macro("FrozenSimulatorUtility", f"{float(numbers['simulator_utility']):.1f}")
        text += macro("FrozenHazardGateUtility", f"{float(numbers['hazard_gate_utility']):.1f}")
        text += macro("FrozenHazardGateSuccess", f"{100.0 * float(numbers['hazard_gate_success']):.1f}\\%")
        text += macro("FrozenLCBUtility", f"{float(numbers['uncertainty_lcb_utility']):.1f}")
        text += macro("FrozenLCBSuccess", f"{100.0 * float(numbers['uncertainty_lcb_success']):.1f}\\%")
        text += macro("FrozenHazardProxyAdvantage", f"{float(numbers['hazard_proxy_advantage']):.1f}")
        text += macro("FrozenSafeUtilityAdvantage", f"{float(numbers['safe_utility_advantage']):.1f}")
    (PAPER / "results_macros.tex").write_text(text, encoding="utf-8")


def run_latex() -> Path:
    PAPER.mkdir(exist_ok=True)
    for pattern in ["main.aux", "main.out", "main.log", "main.bbl", "main.blg", "main.fls", "main.fdb_latexmk"]:
        path = PAPER / pattern
        if path.exists():
            path.unlink()

    def run_command(command: list[str]) -> None:
        subprocess.run(command, cwd=PAPER, check=True, text=True, capture_output=True)

    def format_error(exc: subprocess.CalledProcessError) -> str:
        return f"{' '.join(exc.cmd)}\nSTDOUT:\n{exc.stdout}\nSTDERR:\n{exc.stderr}"

    def run_pdflatex_cycle() -> None:
        if shutil.which("pdflatex") is None:
            raise FileNotFoundError("pdflatex not found")
        run_command(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"])
        aux = PAPER / "main.aux"
        needs_bibtex = aux.exists() and "\\bibdata" in aux.read_text(encoding="utf-8", errors="ignore")
        if needs_bibtex and shutil.which("bibtex") is not None:
            run_command(["bibtex", "main"])
        run_command(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"])
        run_command(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"])

    errors = []
    try:
        if shutil.which("latexmk") is not None:
            try:
                run_command(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"])
            except subprocess.CalledProcessError as exc:
                errors.append(format_error(exc))
                run_pdflatex_cycle()
        else:
            run_pdflatex_cycle()
        pdf = PAPER / "main.pdf"
        if pdf.exists():
            local_pdf = PAPER / "best-of-n-language-symbolic-planner-hybrids.pdf"
            shutil.copy2(pdf, local_pdf)
            REPO_FINAL.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, REPO_FINAL)
            shutil.copy2(pdf, DESKTOP_PDF)
            pdf.unlink(missing_ok=True)
            (ROOT / "docs" / "paper_build_failure.md").unlink(missing_ok=True)
            return DESKTOP_PDF
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            errors.append(format_error(exc))
        else:
            errors.append(str(exc))

    failure = ROOT / "docs" / "paper_build_failure.md"
    failure.write_text("# Paper Build Failure\n\n" + "\n\n".join(errors), encoding="utf-8")
    raise RuntimeError(f"paper build failed; see {failure}")


def main() -> None:
    write_result_macros()
    pdf = run_latex()
    print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
