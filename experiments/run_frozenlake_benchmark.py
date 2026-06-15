"""Run the FrozenLake boundary benchmark tier."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from boundary_planner.frozenlake_benchmark import run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Run a reduced benchmark for tests.")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "frozenlake_benchmark")
    parser.add_argument("--figure", type=Path, default=ROOT / "figures" / "figure10_frozenlake_benchmark.png")
    args = parser.parse_args()

    if args.quick:
        claims = run_benchmark(
            output_dir=args.output,
            figure_path=args.figure,
            seeds=32,
            budgets=(1, 4, 16, 64),
        )
    else:
        claims = run_benchmark(output_dir=args.output, figure_path=args.figure)

    numbers = claims["key_numbers"]
    print(
        "FrozenLake benchmark: "
        f"symbolic utility {numbers['n1_symbolic_utility']} -> {numbers['symbolic_utility']}, "
        f"hole rate {numbers['symbolic_enters_hole']}, "
        f"gate success {numbers['hazard_gate_success']}."
    )
    print(f"claim_pass={claims['claim_pass']}")


if __name__ == "__main__":
    main()
