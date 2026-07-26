# Playwright + pytest automation framework (POM)

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install
```

3. Run the tests:

```bash
pytest tests/test_homepage.py -k homepage_loads -q
```

4. If Playwright reports missing browser binaries, install them:

```bash
playwright install chromium
```

Notes
- Locators are read from `amazon_homepage_locators.json` at the repository root. Update selectors there to match the live site.
- Page objects are in the `pages` package. Tests are in `tests/`.

Azure DevOps integration

- The repository includes [`azure-pipelines.yml`](azure-pipelines.yml) for Azure DevOps CI.
- The pipeline uses `ubuntu-latest`, installs Python dependencies from `requirements.txt`, installs the Playwright Chromium browser, and runs `pytest tests/test_homepage.py -q`.
- In Azure DevOps, create a new pipeline from this YAML file, then run it on `main` or `master` to validate the framework automatically.
