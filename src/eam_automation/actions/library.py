"""Reusable human-readable action library."""

from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ActionDefinition:
    name: str
    description: str
    handler: Callable[..., Any]


def _not_implemented(**kwargs: Any) -> dict:
    return {"status": "TODO", "details": kwargs}


ACTION_REGISTRY: dict[str, ActionDefinition] = {
    "Open Enrollment Application Manager": ActionDefinition(
        name="Open Enrollment Application Manager",
        description="Open the EAM application URL in browser.",
        handler=_not_implemented,
    ),
    "Generate Enrollment Application File": ActionDefinition(
        name="Generate Enrollment Application File",
        description="Generate EAF file from dataset.",
        handler=_not_implemented,
    ),
    "Generate BQN Response File": ActionDefinition(
        name="Generate BQN Response File",
        description="Generate BQN response file from dataset.",
        handler=_not_implemented,
    ),
    "Generate TRR File": ActionDefinition(
        name="Generate TRR File",
        description="Generate TRR file from dataset.",
        handler=_not_implemented,
    ),
    "Upload Enrollment Application File": ActionDefinition(
        name="Upload Enrollment Application File",
        description="Upload generated EAF via UI.",
        handler=_not_implemented,
    ),
    "Upload BQN Response File": ActionDefinition(
        name="Upload BQN Response File",
        description="Upload generated BQN via UI.",
        handler=_not_implemented,
    ),
    "Upload TRR File": ActionDefinition(
        name="Upload TRR File",
        description="Upload generated TRR via UI.",
        handler=_not_implemented,
    ),
    "Validate Backend State via GraphQL": ActionDefinition(
        name="Validate Backend State via GraphQL",
        description="Execute GraphQL validation query.",
        handler=_not_implemented,
    ),
}
