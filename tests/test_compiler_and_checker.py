from boundary_planner.checking import symbolic_check
from boundary_planner.domain import compile_plan
from boundary_planner.execution import execute_true


def test_robust_plan_is_symbolically_and_truly_valid():
    text = """
    Go to the permit desk
    Take the permit
    Go to the toolroom
    Take the key
    Go to the prep room
    Take PPE
    Take the cold carrier
    Go to the lab door
    Unlock the lab
    Go to the lab
    Take the sample
    Pack the sample in the cold carrier
    Go to the receiving dock
    Deliver the sample
    """
    actions = compile_plan(text)
    assert actions[:2] == ["go:office", "take:permit"]
    assert symbolic_check(actions).valid
    result = execute_true(actions)
    assert result.success
    assert not result.semantic_bad


def test_paperwork_loophole_passes_checker_but_fails_execution():
    actions = compile_plan(
        """
        Go to the permit desk
        Take the permit
        Submit the delivery form in the database
        """
    )
    assert symbolic_check(actions).valid
    result = execute_true(actions)
    assert not result.success
    assert result.semantic_bad
    assert result.loophole
