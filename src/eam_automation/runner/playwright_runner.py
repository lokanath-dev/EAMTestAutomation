"""Sequential Playwright runner for one test case + one dataset."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import sys
import asyncio
import re
import time

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.sync_api import sync_playwright

from src.eam_automation.actions.library import ACTION_REGISTRY
from src.eam_automation.storage.yaml_store import load_dataset, load_test_case
from src.eam_automation.config.loader import get_environment


def _log(result: dict, message: str) -> None:
    result.setdefault("logs_text", []).append(message)
    print(message)


def wait_for_eam_ready(page, *, root: Path, timeout_ms: int = 60000) -> None:
    """Wait until FACETS EAM dashboard header text is visible in page or any frame."""
    header_pattern = re.compile(r"Enrollment\s*Administration\s*Manager", re.IGNORECASE)

    try:
        current_url = page.url
    except Exception:
        current_url = "<unavailable>"

    try:
        current_title = page.title()
    except Exception:
        current_title = "<unavailable>"

    print(
        "EAM readiness diagnostics (before wait): "
        f"url={current_url}, title={current_title!r}"
    )

    deadline = time.monotonic() + (timeout_ms / 1000)
    last_diag: tuple[str, int, bool] = ("main", -1, False)

    while time.monotonic() < deadline:
        contexts = [("main", page)] + [
            (f"frame:{idx}:{frame.url}", frame) for idx, frame in enumerate(page.frames)
        ]

        for ctx_name, ctx in contexts:
            try:
                header = ctx.get_by_text(header_pattern)
                count = header.count()
                vis = header.first.is_visible() if count > 0 else False

                last_diag = (ctx_name, count, vis)

                if vis:
                    print(
                        "EAM readiness diagnostics (success): "
                        f"context={ctx_name}, eam_header_count={count}"
                    )
                    return
            except Exception:
                continue

        time.sleep(0.25)

    try:
        fail_url = page.url
    except Exception:
        fail_url = "<unavailable>"

    try:
        fail_title = page.title()
    except Exception:
        fail_title = "<unavailable>"

    ctx_name, count, vis = last_diag
    print(
        "EAM readiness diagnostics (timeout): "
        f"url={fail_url}, title={fail_title!r}, context={ctx_name}, "
        f"eam_header_count={count}, eam_header_visible={vis}"
    )

    timeout_dir = root / "tmp"
    timeout_dir.mkdir(parents=True, exist_ok=True)

    timeout_shot = timeout_dir / "eam_ready_timeout.png"
    page.screenshot(path=str(timeout_shot), full_page=True)

    timeout_dom = timeout_dir / "eam_ready_dom.html"
    timeout_dom.write_text(page.content(), encoding="utf-8")

    print("EAM dashboard did not appear within 60 seconds")
    raise TimeoutError(
        "EAM dashboard not detected (Enrollment Administration Manager not visible) within 60 seconds"
    )


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
            if action_name not in ACTION_REGISTRY:
                raise ValueError(f"Unknown step action: {action_name}")

            action = ACTION_REGISTRY[action_name]
            _log(result, f"Running step {idx}: {action_name}")

            # Generic kwargs payload keeps handlers easy to evolve.
            action.handler(
                page=page,
                dataset=dataset,
                params=parameters,
                run_dir=run_dir,
                context=shared_context,
            )

            if action.ui_step and hasattr(page, "get_by_text"):
                wait_for_eam_ready(page, root=shared_context["repo_root"], timeout_ms=60000)
                _log(result, "UI ready – proceeding to next step")

            _log(result, f"Step completed successfully: {action_name}")
        except Exception as exc:
            step_result["status"] = "FAIL"
            step_result["error"] = str(exc)

            if page is not None and hasattr(page, "screenshot"):
                step_failure_shot = shared_context["repo_root"] / "tmp" / f"step_failure_{idx}.png"
                step_failure_shot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(step_failure_shot), full_page=True)
                step_result["screenshot"] = str(step_failure_shot)

            result["steps"].append(step_result)
            return False

        result["steps"].append(step_result)

    return True


def run_test_case(
    root: Path,
    test_case_name: str,
    dataset_name: str,
    env_name: str | None = None,
    use_persistent_profile: bool = True,
) -> dict:
    tc = load_test_case(root, test_case_name)
    ds = load_dataset(root, dataset_name)

    if not env_name:
        env_name = "DEV1"
    env_path = root / "config" / "environments.yaml"
    env = get_environment(env_path, env_name)

    # Optional environment-level override, defaults to True.
    if "use_persistent_profile" in env:
        use_persistent_profile = bool(env["use_persistent_profile"])

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
        "environment": env_name,
        "status": "PASS",
        "steps": [],
        "logs": str(logs_path),
        "trace": str(trace_path),
        "screenshot": None,
        "logs_text": [],
    }

    logs_path.write_text("", encoding="utf-8")

    with sync_playwright() as p:
        browser = None
        profile_dir = root / "storage" / "chrome_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        if use_persistent_profile:
            _log(result, "Launching Chrome with persistent profile at storage/chrome_profile")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=False,
                slow_mo=250,
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=250)
            context = browser.new_context()
            page = context.new_page()

        shared_context = {
            "browser_context": context,
            "page": page,
            "env": env,
            "repo_root": root,
            "logs_text": result["logs_text"],
            "wait_for_eam_ready": lambda p: wait_for_eam_ready(p, root=root, timeout_ms=60000),
        }

        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        try:
            ok = execute_steps_in_order(
                tc.get("steps", []),
                page=page,
                dataset=ds,
                run_dir=run_dir,
                shared_context=shared_context,
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
            context.close()
            if browser is not None:
                browser.close()

    logs_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
