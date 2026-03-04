"""Temporary artifact manager (screenshots, logs, traces)."""

from pathlib import Path
import shutil


class ArtifactManager:
    def __init__(self, root: Path):
        self.root = root
        self.screenshots = root / "tmp" / "screenshots"
        self.logs = root / "tmp" / "logs"
        self.traces = root / "tmp" / "traces"
        for d in (self.screenshots, self.logs, self.traces):
            d.mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> None:
        for d in (self.screenshots, self.logs, self.traces):
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)
