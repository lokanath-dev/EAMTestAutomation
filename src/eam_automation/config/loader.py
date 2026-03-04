"""Environment configuration loader."""

from pathlib import Path
import yaml


def load_environments(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("environments", {})


def get_environment(path: Path, name: str) -> dict:
    envs = load_environments(path)
    if name not in envs:
        raise KeyError(f"Unknown environment: {name}")
    return envs[name]
