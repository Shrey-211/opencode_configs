from playwright.sync_api import sync_playwright
import sys

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()
    page.set_viewport_size({'width': 1280, 'height': 720})
    
    page.goto('https://www.youtube.com')
    page.wait_for_load_state('networkidle')
    print('Opened YouTube')
    
    page.wait_for_timeout(2000)
    search_box = page.wait_for_selector('input[name="search_query"]')
    search_box.fill('Taylor Swift best songs')
    page.keyboard.press('Enter')
    page.wait_for_load_state('networkidle')
    print('Searching Taylor Swift...')
    
    page.wait_for_timeout(2000)
    page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    
    print('Playing Taylor Swift!')
    page.wait_for_timeout(10000)
    browser.close()
