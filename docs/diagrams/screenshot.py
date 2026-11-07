"""Screenshots a diagram page to PNG.

    uv run --no-project --with playwright python docs/diagrams/screenshot.py \\
        docs/diagrams/daily-flow.html daily-flow.png

The Chromium that playwright downloads may not match the playwright version uv installs,
and launch() then fails. Point CHROMIUM at a browser that exists, e.g.
~/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome.
"""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

page_path, png_path = sys.argv[1], sys.argv[2]
chromium = os.environ.get("CHROMIUM")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.path.expanduser(chromium) if chromium else None)
    page = browser.new_page(viewport={"width": 1400, "height": 1100}, device_scale_factor=1.5)
    page.goto(Path(page_path).resolve().as_uri())
    page.wait_for_timeout(2500)  # web fonts
    page.screenshot(path=png_path, full_page=True)
    browser.close()
