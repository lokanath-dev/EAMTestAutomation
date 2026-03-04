"""EAM home page object."""

from src.eam_automation.pages.base_page import BasePage


class EamHomePage(BasePage):
    def open(self, base_url: str) -> None:
        self.page.goto(base_url)

    def search_member(self, member_id: str) -> None:
        self.page.get_by_label("Member ID").fill(member_id)
        self.page.get_by_role("button", name="Search").click()
