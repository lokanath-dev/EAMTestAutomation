"""Sequential Playwright runner for one test case + one dataset."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.sync_api import sync_playwright

from src.eam_automation.actions.library import ACTION_REGISTRY
from src.eam_automation.storage.yaml_store import load_dataset, load_test_case


def execute_steps_in_order(
    steps: list[dict],
    *,
    page,
    dataset: dict,
    run_dir: Path,
    shared_context: dict,
    result: dict,
) -> bool:
    """Execute test steps in listed order.

    Returns True if all steps pass, False on first failure.
    """
    for idx, step in enumerate(steps, start=1):
        step_name = step.get("step_name") or f"Step {idx}"
        action_name = step.get("action_name") or step.get("action")
        parameters = step.get("parameters") or step.get("params") or {}

        step_result = {
            "index": idx,
            "step_name": step_name,
            "action_name": action_name,
            "status": "PASS",
            "error": None,
        }

        try:
            action = ACTION_REGISTRY[action_name]
            # Generic kwargs payload keeps handlers easy to evolve.
            action.handler(
                page=page,
                dataset=dataset,
                params=parameters,
                run_dir=run_dir,
                context=shared_context,
            )
        except Exception as exc:
            step_result["status"] = "FAIL"
            step_result["error"] = str(exc)
            result["steps"].append(step_result)
            return False

        result["steps"].append(step_result)

    return True


def run_test_case(root: Path, test_case_name: str, dataset_name: str) -> dict:
    tc = load_test_case(root, test_case_name)
    ds = load_dataset(root, dataset_name)

    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    run_dir = root / ".tmp" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    logs_path = run_dir / "run.log"
    trace_path = run_dir / "trace.zip"
    screenshot_path = run_dir / "failure.png"

    result = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "test_case": test_case_name,
        "dataset": dataset_name,
        "status": "PASS",
        "steps": [],
        "logs": str(logs_path),
        "trace": str(trace_path),
        "screenshot": None,
    }

    logs_path.write_text("", encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        try:
            ok = execute_steps_in_order(
                tc.get("steps", []),
                page=page,
                dataset=ds,
                run_dir=run_dir,
                shared_context={},
                result=result,
            )
            if not ok:
                result["status"] = "FAIL"
                page.screenshot(path=str(screenshot_path), full_page=True)
                result["screenshot"] = str(screenshot_path)
        except Exception as exc:
            result["status"] = "FAIL"
            result["error"] = str(exc)
            page.screenshot(path=str(screenshot_path), full_page=True)
            result["screenshot"] = str(screenshot_path)
        finally:
            context.tracing.stop(path=str(trace_path))
            browser.close()

    logs_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
