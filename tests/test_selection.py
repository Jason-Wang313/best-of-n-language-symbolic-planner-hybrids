from bon_symbolic.generator import generate_pool
from bon_symbolic.selection import select_plan
from bon_symbolic.theory import TwoTypeLaw


def test_generation_and_selection_are_deterministic():
    pool_a = generate_pool("lab_delivery", 32, seed=123)
    pool_b = generate_pool("lab_delivery", 32, seed=123)
    assert [p.mode for p in pool_a] == [p.mode for p in pool_b]
    sel_a = select_plan(pool_a, "symbolic_bon", seed=9)
    sel_b = select_plan(pool_b, "symbolic_bon", seed=9)
    assert sel_a.selected_index == sel_b.selected_index
    assert sel_a.plan.text == sel_b.plan.text


def test_two_type_law_monotone_loophole_probability():
    law = TwoTypeLaw(p_loophole=0.1, utility_good=90.0, utility_loophole=10.0)
    assert law.loophole_selected_probability(8) > law.loophole_selected_probability(1)
    assert law.expected_true_utility(16) < law.expected_true_utility(2)
