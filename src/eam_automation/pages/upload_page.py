"""Upload page object."""

from pathlib import Path
from src.eam_automation.pages.base_page import BasePage


class UploadPage(BasePage):
    def upload_file(self, file_path: Path) -> None:
        self.page.get_by_label("Upload").set_input_files(str(file_path))
        self.page.get_by_role("button", name="Submit").click()
