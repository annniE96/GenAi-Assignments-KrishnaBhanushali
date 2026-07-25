from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).parent
LOCATORS_FILE = ROOT / "amazon_homepage_locators.json"
BASE_URL = "https://www.amazon.com"


def load_locators() -> dict:
    if LOCATORS_FILE.exists():
        import json

        return json.loads(LOCATORS_FILE.read_text(encoding="utf-8"))
    return {}


def get_selector(locators: dict, name: str) -> str:
    locator_list = locators.get("locators", []) if isinstance(locators, dict) else locators
    if isinstance(locator_list, list):
        for entry in locator_list:
            if entry.get("name") == name:
                selector = entry.get("selector")
                if selector:
                    return selector
    raise KeyError(f"Locator '{name}' was not found in the locator data")


def main() -> int:
    locators = load_locators()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        try:
            page.goto(BASE_URL, wait_until="load")
            page.wait_for_load_state("networkidle")

            title = page.title()
            if "amazon" not in title.lower():
                raise AssertionError(f"Unexpected page title: {title}")

            search_input = page.locator(get_selector(locators, "search_input"))
            if not search_input.is_visible():
                raise AssertionError("Amazon search box is not visible")

            search_input.fill("amazon basics charger")
            page.locator(get_selector(locators, "search_submit")).click()
            page.wait_for_load_state("domcontentloaded")

            if "amazon basics charger" not in page.url.lower():
                raise AssertionError(f"Search results URL did not update as expected: {page.url}")

            print("Amazon homepage automation completed successfully.")
            print(f"Title: {title}")
            print(f"Results URL: {page.url}")
            return 0
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())