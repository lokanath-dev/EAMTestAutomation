from pathlib import Path

from src.eam_automation.actions.library import ActionDefinition
from src.eam_automation.runner.playwright_runner import execute_steps_in_order


class DummyPage:
    pass


def test_execute_order(monkeypatch, tmp_path: Path):
    calls = []

    def mk(name):
        def _handler(**kwargs):
            calls.append(name)
            return {"ok": True}

        return _handler

    fake_registry = {
        "A": ActionDefinition(name="A", description="", handler=mk("A")),
        "B": ActionDefinition(name="B", description="", handler=mk("B")),
        "C": ActionDefinition(name="C", description="", handler=mk("C")),
    }

    monkeypatch.setattr("src.eam_automation.runner.playwright_runner.ACTION_REGISTRY", fake_registry)

    steps = [
        {"step_name": "1", "action_name": "A", "parameters": {}},
        {"step_name": "2", "action_name": "B", "parameters": {}},
        {"step_name": "3", "action_name": "C", "parameters": {}},
    ]
    result = {"steps": []}

    ok = execute_steps_in_order(
        steps,
        page=DummyPage(),
        dataset={"fields": {}},
        run_dir=tmp_path,
        shared_context={},
        result=result,
    )

    assert ok is True
    assert calls == ["A", "B", "C"]
    assert [s["status"] for s in result["steps"]] == ["PASS", "PASS", "PASS"]
