"""Test case data model."""

from pydantic import BaseModel, Field


class TestStep(BaseModel):
    action: str
    params: dict[str, str] = Field(default_factory=dict)


class TestCase(BaseModel):
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    steps: list[TestStep] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
