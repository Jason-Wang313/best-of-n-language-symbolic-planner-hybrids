from pathlib import Path

from boundary_planner.frozenlake_benchmark import run_benchmark


def test_frozenlake_quick_claims_pass(tmp_path: Path):
    claims = run_benchmark(
        output_dir=tmp_path / "frozenlake",
        figure_path=tmp_path / "frozenlake.png",
        seeds=16,
        budgets=(1, 4, 16, 64),
    )
    assert claims["claim_pass"] is True
    assert claims["checks"]["frozenlake_symbolic_enters_holes"] is True
    assert claims["checks"]["frozenlake_hazard_gate_recovers"] is True
