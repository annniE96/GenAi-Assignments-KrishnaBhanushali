from pages.home_page import HomePage


def test_homepage_loads_and_search_box_is_visible(page, base_url, locators):
    home = HomePage(page, locators, base_url)

    home.go_to()
    home.wait_for_load()

    assert "amazon" in page.title().lower()
    assert home.get_locator("search_input").is_visible()


def test_homepage_loads_with_expected_url(page, base_url, locators):
    home = HomePage(page, locators, base_url)

    home.go_to()
    home.wait_for_load()

    assert page.url.startswith("https://www.amazon.com")
    assert "Amazon" in page.title()
