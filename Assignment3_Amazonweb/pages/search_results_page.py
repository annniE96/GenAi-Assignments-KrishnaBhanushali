from .base_page import BasePage


class SearchResultsPage(BasePage):
    def get_results_heading(self):
        # Common pattern: Amazon shows a heading with the search term
        try:
            return self.page.text_content("h1") or ""
        except Exception:
            return ""
