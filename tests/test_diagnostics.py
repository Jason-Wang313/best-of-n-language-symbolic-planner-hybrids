from boundary_planner.generator import generate_pool
from boundary_planner.metrics import pool_diagnostics
from boundary_planner.selection import select_plan


def test_pool_diagnostics_detect_valid_semantic_mismatch():
    pool = generate_pool("archival_handoff", 128, seed=7)
    diag = pool_diagnostics(pool)
    assert diag["pool_checker_pass_rate"] > diag["pool_execution_success_rate"]
    assert diag["pool_valid_semantic_bad_rate"] > 0.25


def test_repair_avoids_symbolic_loophole_when_available():
    pool = generate_pool("lab_delivery", 128, seed=15)
    symbolic = select_plan(pool, "symbolic_proxy", seed=1)
    repaired = select_plan(pool, "adversarial_gate", seed=1)
    assert symbolic.plan.mode == "paperwork_loophole"
    assert repaired.plan.mode in {"robust_grounded", "redundant_safe"}
