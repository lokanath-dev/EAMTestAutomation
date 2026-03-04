"""YAML/JSON persistence for test cases and datasets + SQLite metadata sync."""

from __future__ import annotations

from pathlib import Path
import json
import yaml

from src.eam_automation.db.database import MetadataDB
from src.eam_automation.models.dataset import Dataset
from src.eam_automation.models.test_case import TestCase

SUPPORTED_EXTS = (".yaml", ".yml", ".json")


def _tc_dir(root: Path) -> Path:
    path = root / "storage" / "test_cases"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ds_dir(root: Path) -> Path:
    path = root / "storage" / "datasets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _db(root: Path) -> MetadataDB:
    db = MetadataDB(root / "storage" / "metadata.db")
    db.init_schema()
    return db


def _write_struct(path: Path, data: dict) -> None:
    if path.suffix == ".json":
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _read_struct(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text) or {}


def _find_by_stem(folder: Path, name: str) -> Path:
    for ext in SUPPORTED_EXTS:
        candidate = folder / f"{name}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No file found for '{name}' in {folder}")


def _normalize_step(step: dict) -> dict:
    """Backward compatibility for old step shape."""
    if "action_name" in step:
        return {
            "step_name": step.get("step_name", step["action_name"]),
            "action_name": step["action_name"],
            "parameters": step.get("parameters", {}),
        }

    action = step.get("action", "")
    params = step.get("params", {})
    return {
        "step_name": step.get("step_name", action or "Step"),
        "action_name": action,
        "parameters": params,
    }


def _normalize_test_case_payload(payload: dict) -> dict:
    payload = dict(payload)
    payload["steps"] = [_normalize_step(s) for s in payload.get("steps", [])]
    return payload


def save_test_case(root: Path, tc: TestCase, ext: str = ".yaml") -> Path:
    out = _tc_dir(root) / f"{tc.name}{ext}"
    payload = _normalize_test_case_payload(tc.model_dump())
    _write_struct(out, payload)
    _db(root).upsert_test_case(tc.name, payload)
    return out


def save_dataset(root: Path, ds: Dataset, ext: str = ".yaml") -> Path:
    out = _ds_dir(root) / f"{ds.name}{ext}"
    _write_struct(out, ds.model_dump())
    return out


def load_test_case(root: Path, name: str) -> dict:
    path = _find_by_stem(_tc_dir(root), name)
    payload = _normalize_test_case_payload(_read_struct(path))
    _db(root).upsert_test_case(name, payload)
    return payload


def load_dataset(root: Path, name: str) -> dict:
    return _read_struct(_find_by_stem(_ds_dir(root), name))


def _list_stems(folder: Path) -> list[str]:
    names = set()
    for ext in SUPPORTED_EXTS:
        for p in folder.glob(f"*{ext}"):
            names.add(p.stem)
    return sorted(names)


def list_test_cases(root: Path) -> list[str]:
    return _list_stems(_tc_dir(root))


def list_datasets(root: Path) -> list[str]:
    return _list_stems(_ds_dir(root))
