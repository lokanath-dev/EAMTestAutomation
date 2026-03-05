"""Reusable human-readable action library."""

from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ActionDefinition:
    name: str
    description: str
    handler: Callable[..., Any]
    ui_step: bool = True


def _not_implemented(**kwargs: Any) -> dict:
    raise NotImplementedError("Action handler not implemented yet.")


def _log(context: dict, message: str) -> None:
    logs = context.get("logs_text")
    if isinstance(logs, list):
        logs.append(message)
    print(message)


def open_eam(**kwargs: Any) -> dict:
    """Open the EAM UI using the configured environment base URL."""
    context = kwargs.get("context") or {}
    page = kwargs.get("page") or context.get("page")
    env = context.get("env") or {}
    wait_for_eam_ready = context.get("wait_for_eam_ready")

    if page is None:
        raise ValueError("Playwright page is missing from execution context.")

    url = env.get("base_url") or env.get("base_ui_url")
    if not url:
        raise ValueError("Environment base URL is missing. Expected 'base_url' or 'base_ui_url'.")

    _log(context, "Opening EAM URL")
    page.goto(url, wait_until="domcontentloaded")

    _log(context, "Waiting for EAM dashboard")
    if callable(wait_for_eam_ready):
        wait_for_eam_ready(page)
    else:
        page.wait_for_load_state("networkidle")
    _log(context, "EAM dashboard ready")

    return {"status": "success", "message": "EAM opened", "url": url}


ACTION_REGISTRY: dict[str, ActionDefinition] = {
    "open_eam": ActionDefinition(
        name="open_eam",
        description="Open the EAM application URL in browser.",
        handler=open_eam,
        ui_step=True,
    ),
    "Open Enrollment Application Manager": ActionDefinition(
        name="Open Enrollment Application Manager",
        description="Open the EAM application URL in browser.",
        handler=open_eam,
        ui_step=True,
    ),
    "Generate Enrollment Application File": ActionDefinition(
        name="Generate Enrollment Application File",
        description="Generate EAF file from dataset.",
        handler=_not_implemented,
        ui_step=False,
    ),
    "Generate BQN Response File": ActionDefinition(
        name="Generate BQN Response File",
        description="Generate BQN response file from dataset.",
        handler=_not_implemented,
        ui_step=False,
    ),
    "Generate TRR File": ActionDefinition(
        name="Generate TRR File",
        description="Generate TRR file from dataset.",
        handler=_not_implemented,
        ui_step=False,
    ),
    "Upload Enrollment Application File": ActionDefinition(
        name="Upload Enrollment Application File",
        description="Upload generated EAF via UI.",
        handler=_not_implemented,
        ui_step=True,
    ),
    "Upload BQN Response File": ActionDefinition(
        name="Upload BQN Response File",
        description="Upload generated BQN via UI.",
        handler=_not_implemented,
        ui_step=True,
    ),
    "Upload TRR File": ActionDefinition(
        name="Upload TRR File",
        description="Upload generated TRR via UI.",
        handler=_not_implemented,
        ui_step=True,
    ),
    "validate_graphql": ActionDefinition(
        name="validate_graphql",
        description="Execute GraphQL validation query.",
        handler=_not_implemented,
        ui_step=False,
    ),
    "Validate Backend State via GraphQL": ActionDefinition(
        name="Validate Backend State via GraphQL",
        description="Execute GraphQL validation query.",
        handler=_not_implemented,
        ui_step=False,
    ),
}
