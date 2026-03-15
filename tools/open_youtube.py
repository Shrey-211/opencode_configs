from playwright.sync_api import sync_playwright
import sys

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.youtube.com')
        page.wait_for_timeout(3000)
        title = page.title()
        print(f'SUCCESS: YouTube opened - {title}')
        browser.close()
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
