"""PDF report exporter."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_pdf_report(root: Path, run_result: dict) -> Path:
    out_dir = root / "storage" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"run_result_{run_result.get('run_id', 'latest')}.pdf"

    c = canvas.Canvas(str(out_path), pagesize=letter)
    y = 750
    c.drawString(50, y, "EAM Test Automation Run Report")
    y -= 20

    for k, v in run_result.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 16
        if y < 60:
            c.showPage()
            y = 750

    c.save()
    return out_path
