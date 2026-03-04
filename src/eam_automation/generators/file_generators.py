"""File generators for EAF, BQN, TRR using template + dataset fields."""

from pathlib import Path


class BaseGenerator:
    extension = ".txt"

    def __init__(self, template_path: Path):
        self.template_path = template_path

    def generate(self, out_dir: Path, name: str, fields: dict[str, str]) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        template = self.template_path.read_text(encoding="utf-8") if self.template_path.exists() else ""
        rendered = template.format(**fields) if template else "\n".join(f"{k}={v}" for k, v in fields.items())
        out = out_dir / f"{name}{self.extension}"
        out.write_text(rendered, encoding="utf-8")
        return out


class EAFGenerator(BaseGenerator):
    extension = ".eaf"


class BQNGenerator(BaseGenerator):
    extension = ".bqn"


class TRRGenerator(BaseGenerator):
    extension = ".trr"
