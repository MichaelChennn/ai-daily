"""Screenshots a diagram page to PNG, in day or night mode.

    uv run --no-project --with playwright python docs/diagrams/screenshot.py \\
        docs/diagrams/daily-flow.en.html daily-flow-en-dark.png --theme dark

The Chromium that playwright downloads may not match the playwright version uv installs,
and launch() then fails. Point CHROMIUM at a browser that exists, e.g.
~/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome.
"""

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

p = argparse.ArgumentParser()
p.add_argument("page")
p.add_argument("png")
p.add_argument("--theme", choices=["light", "dark"], default="light")
a = p.parse_args()
chromium = os.environ.get("CHROMIUM")

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=os.path.expanduser(chromium) if chromium else None)
    page = browser.new_page(
        viewport={"width": 1400, "height": 1100}, device_scale_factor=1.5, color_scheme=a.theme
    )
    page.goto(Path(a.page).resolve().as_uri())
    page.wait_for_timeout(2500)  # web fonts
    page.screenshot(path=a.png, full_page=True)
    browser.close()
