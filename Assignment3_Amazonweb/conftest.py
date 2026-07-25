import json
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).parent
LOCATORS_FILE = ROOT / "amazon_homepage_locators.json"


@pytest.fixture(scope="session")
def base_url():
    return "https://www.amazon.com"


@pytest.fixture(scope="session")
def locators():
    if LOCATORS_FILE.exists():
        return json.loads(LOCATORS_FILE.read_text(encoding="utf-8"))
    return {}


@pytest.fixture()
def page(base_url, locators):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()
        yield page
        context.close()
        browser.close()
