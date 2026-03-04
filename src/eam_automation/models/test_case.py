"""Test case data model."""

from pydantic import BaseModel, Field
from typing import Any


class TestStep(BaseModel):
    step_name: str
    action_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    steps: list[TestStep] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
