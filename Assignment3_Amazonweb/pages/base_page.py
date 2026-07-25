class BasePage:
    def __init__(self, page, locators: dict, base_url: str):
        self.page = page
        self.locators = locators or {}
        self.base_url = base_url

    def get_selector(self, name: str):
        locators = self.locators.get("locators", []) if isinstance(self.locators, dict) else self.locators
        if isinstance(locators, list):
            for entry in locators:
                if entry.get("name") == name:
                    return entry.get("selector")
        if isinstance(self.locators, dict):
            return self.locators.get(name)
        return None

    def get_locator(self, name: str):
        selector = self.get_selector(name)
        if not selector:
            raise KeyError(f"Locator '{name}' was not found in the locator data")
        return self.page.locator(selector)
