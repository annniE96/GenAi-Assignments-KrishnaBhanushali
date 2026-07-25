from .base_page import BasePage


class HomePage(BasePage):
    def go_to(self):
        self.page.goto(self.base_url, wait_until="load")

    def wait_for_load(self):
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(3000)

    def set_search_category(self, category: str):
        locator = self.get_locator("search_department_dropdown")
        locator.select_option(label=category)

    def search(self, term: str):
        self.get_locator("search_input").fill(term)
        self.get_locator("search_submit").click()

    def open_deliver_to(self):
        self.get_locator("deliver_to_button").click()

    def set_delivery_location(self, location: str):
        self.page.locator("input[type='text']").first.fill(location)
        self.page.locator("text=Done").click()

    def open_account(self):
        self.get_locator("account_lists").hover()

    def click_returns_orders(self):
        self.get_locator("returns_orders").click()

    def open_cart(self):
        self.get_locator("cart").click()

    def open_category_menu(self):
        self.get_locator("all_categories_menu").click()

    def advance_hero_carousel(self):
        self.get_locator("hero_carousel_next").click()

    def click_collection_tile(self):
        self.page.locator("a").first.click()

    def click_footer_link(self, label: str):
        self.page.get_by_text(label).click()

    def back_to_top(self):
        self.get_locator("back_to_top").click()
