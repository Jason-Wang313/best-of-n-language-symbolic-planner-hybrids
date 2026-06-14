from pathlib import Path

import pandas as pd

from experiments.run_expansion_suite import (
    generate_custom_pool,
    run_suite,
    select_expansion,
    suite_config,
)


def test_custom_pool_can_raise_loophole_prior():
    pool = generate_custom_pool("lab_delivery", 256, seed=3, loophole_prior=0.40)
    loopholes = [p for p in pool if p.mode in {"paperwork_loophole", "elevator_loophole", "simulator_lure"}]
    assert len(loopholes) > 70


def test_strict_boundary_proxy_avoids_visible_boundary_loophole():
    pool = generate_custom_pool("lab_delivery", 512, seed=13, loophole_prior=0.28)
    _, plan, _, _ = select_expansion(pool, "strict_boundary_proxy", seed=1)
    assert plan.mode in {"robust_grounded", "redundant_safe"}


def test_quick_expansion_writes_claim_file(tmp_path: Path):
    out = tmp_path / "expansion"
    claims = run_suite("quick", out)
    assert (out / "expanded_summary.csv").exists()
    assert (out / "claims.json").exists()
    summary = pd.read_csv(out / "expanded_summary.csv")
    assert int(summary["n"].max()) == suite_config("quick").max_n
    assert "symbolic_proxy_collapses_at_512" in claims["checks"]
