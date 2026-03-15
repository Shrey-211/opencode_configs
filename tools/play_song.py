from playwright.sync_api import sync_playwright
import sys

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})
        
        page.goto('https://www.youtube.com')
        page.wait_for_load_state('networkidle')
        print('Opened YouTube', file=sys.stderr)
        
        # Debug: print page content
        page.wait_for_timeout(3000)
        
        # Try different search selectors
        search_selectors = [
            'input#search',
            'input[name="search_query"]', 
            '#search-input',
            'input[aria-label="Search"]',
            'ytd-searchbox input'
        ]
        
        for sel in search_selectors:
            try:
                search_box = page.wait_for_selector(sel, timeout=2000)
                if search_box:
                    print(f'Found search with: {sel}', file=sys.stderr)
                    search_box.fill('lofi hip hop radio')
                    page.keyboard.press('Enter')
                    break
            except:
                continue
        else:
            # If none found, try clicking search button and using keyboard
            print('Trying alternative method...', file=sys.stderr)
            page.keyboard.press('/')
            page.wait_for_timeout(1000)
            page.keyboard.type('lofi hip hop radio')
            page.keyboard.press('Enter')
        
        page.wait_for_load_state('networkidle')
        print('Searched', file=sys.stderr)
        
        page.wait_for_timeout(2000)
        
        # Click first video
        page.keyboard.press('Tab')
        page.keyboard.press('Enter')
        
        print('Playing!', file=sys.stderr)
        page.wait_for_timeout(10000)
        browser.close()
        
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
