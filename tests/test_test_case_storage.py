from pathlib import Path

from src.eam_automation.models.test_case import TestCase, TestStep
from src.eam_automation.storage.yaml_store import load_test_case, save_test_case


def test_create_test_case_with_three_steps_and_save_load(tmp_path: Path):
    root = tmp_path
    tc = TestCase(
        name="tc_three_steps",
        description="three steps",
        tags=["smoke"],
        steps=[
            TestStep(step_name="s1", action_name="Open Enrollment Application Manager", parameters={}),
            TestStep(step_name="s2", action_name="Generate Enrollment Application File", parameters={"a": 1}),
            TestStep(step_name="s3", action_name="Validate Backend State via GraphQL", parameters={"q": "x"}),
        ],
    )

    save_test_case(root, tc, ext=".yaml")
    loaded = load_test_case(root, "tc_three_steps")

    assert len(loaded["steps"]) == 3
    assert loaded["steps"][0]["step_name"] == "s1"
    assert loaded["steps"][1]["action_name"] == "Generate Enrollment Application File"
    assert loaded["steps"][2]["parameters"]["q"] == "x"


def test_reorder_steps_and_persist_order(tmp_path: Path):
    root = tmp_path
    tc = TestCase(
        name="tc_reorder",
        steps=[
            TestStep(step_name="first", action_name="Open Enrollment Application Manager"),
            TestStep(step_name="second", action_name="Generate Enrollment Application File"),
            TestStep(step_name="third", action_name="Validate Backend State via GraphQL"),
        ],
    )

    # move third to first
    reordered = [tc.steps[2], tc.steps[0], tc.steps[1]]
    tc.steps = reordered

    save_test_case(root, tc, ext=".json")
    loaded = load_test_case(root, "tc_reorder")

    assert [s["step_name"] for s in loaded["steps"]] == ["third", "first", "second"]
