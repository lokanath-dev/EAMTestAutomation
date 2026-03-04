"""YAML persistence for test cases and datasets."""

from pathlib import Path
import yaml

from src.eam_automation.models.dataset import Dataset
from src.eam_automation.models.test_case import TestCase


def _tc_dir(root: Path) -> Path:
    path = root / "storage" / "test_cases"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ds_dir(root: Path) -> Path:
    path = root / "storage" / "datasets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_test_case(root: Path, tc: TestCase) -> Path:
    out = _tc_dir(root) / f"{tc.name}.yaml"
    out.write_text(yaml.safe_dump(tc.model_dump(), sort_keys=False), encoding="utf-8")
    return out


def save_dataset(root: Path, ds: Dataset) -> Path:
    out = _ds_dir(root) / f"{ds.name}.yaml"
    out.write_text(yaml.safe_dump(ds.model_dump(), sort_keys=False), encoding="utf-8")
    return out


def load_test_case(root: Path, name: str) -> dict:
    return yaml.safe_load((_tc_dir(root) / f"{name}.yaml").read_text(encoding="utf-8"))


def load_dataset(root: Path, name: str) -> dict:
    return yaml.safe_load((_ds_dir(root) / f"{name}.yaml").read_text(encoding="utf-8"))


def list_test_cases(root: Path) -> list[str]:
    return sorted([p.stem for p in _tc_dir(root).glob("*.yaml")])


def list_datasets(root: Path) -> list[str]:
    return sorted([p.stem for p in _ds_dir(root).glob("*.yaml")])
