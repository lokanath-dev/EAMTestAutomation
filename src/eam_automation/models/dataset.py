"""Dataset data model."""

from pydantic import BaseModel, Field


class Dataset(BaseModel):
    name: str
    fields: dict[str, str] = Field(default_factory=dict)
