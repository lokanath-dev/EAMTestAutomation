"""Sequential Playwright runner for one test case + one dataset."""

from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

from src.eam_automation.artifacts.manager import ArtifactManager
from src.eam_automation.storage.yaml_store import load_dataset, load_test_case


def run_test_case(root: Path, test_case_name: str, dataset_name: str) -> dict:
    artifacts = ArtifactManager(root)
    tc = load_test_case(root, test_case_name)
    ds = load_dataset(root, dataset_name)

    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    result = {
        "run_id": run_id,
        "test_case": test_case_name,
        "dataset": dataset_name,
        "status": "PASS",
        "steps": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            for step in tc.get("steps", []):
                result["steps"].append({"action": step.get("action"), "status": "TODO"})

            # Basic trace capture boilerplate
            context.tracing.start(screenshots=True, snapshots=True)
        except Exception as exc:
            result["status"] = "FAIL"
            screenshot_path = artifacts.screenshots / f"{run_id}.png"
            page.screenshot(path=str(screenshot_path))
            result["error"] = str(exc)
            result["screenshot"] = str(screenshot_path)
        finally:
            trace_path = artifacts.traces / f"{run_id}.zip"
            context.tracing.stop(path=str(trace_path))
            result["trace"] = str(trace_path)
            browser.close()

    # Keep temporary artifacts unless explicitly cleaned by caller/app exit.
    result["dataset_fields"] = ds.get("fields", {})
    return result
