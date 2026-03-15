#!/usr/bin/env python3
"""
Selenium tool for browser automation.
Opens Chrome (persistent mode) and allows interaction.
"""

import json
import sys
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

driver = None
screenshot_dir = Path("D:/workspace/open_code/screenshots")
screenshot_dir.mkdir(parents=True, exist_ok=True)
playback_thread = None


def get_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
    return driver


def open_chrome(url: str = "about:blank"):
    global driver
    try:
        driver = get_driver()
        driver.get(url)
        return {
            "status": "success",
            "message": f"Chrome opened and navigated to {url}",
            "title": driver.title,
            "url": driver.current_url
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def navigate(url: str):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        driver.get(url)
        return {
            "status": "success",
            "message": f"Navigated to {url}",
            "title": driver.title,
            "url": driver.current_url
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def click(selector: str, timeout: int = 10):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        return {"status": "success", "message": f"Clicked element: {selector}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to click {selector}: {str(e)}"}


def type_text(selector: str, text: str, clear_first: bool = True):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        if clear_first:
            element.clear()
        element.send_keys(text)
        return {"status": "success", "message": f"Typed text into {selector}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to type: {str(e)}"}


def get_text(selector: str):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        element = driver.find_element(By.CSS_SELECTOR, selector)
        text = element.text
        return {"status": "success", "text": text}
    except Exception as e:
        return {"status": "error", "message": f"Failed to get text: {str(e)}"}


def get_attribute(selector: str, attribute: str):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        element = driver.find_element(By.CSS_SELECTOR, selector)
        value = element.get_attribute(attribute)
        return {"status": "success", "attribute": attribute, "value": value}
    except Exception as e:
        return {"status": "error", "message": f"Failed to get attribute: {str(e)}"}


def get_title():
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        return {"status": "success", "title": driver.title, "url": driver.current_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def screenshot(filename: str | None = None):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        if filename is None:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        
        filepath = screenshot_dir / filename
        driver.save_screenshot(str(filepath))
        return {
            "status": "success",
            "message": f"Screenshot saved",
            "filepath": str(filepath),
            "filename": filename
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def execute_script(script: str):
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        result = driver.execute_script(script)
        return {"status": "success", "result": str(result)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_page_source():
    global driver
    try:
        if driver is None:
            return {"status": "error", "message": "Chrome not open. Use 'open' first."}
        
        return {"status": "success", "html": driver.page_source[:5000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def close_browser():
    global driver
    try:
        if driver:
            driver.quit()
            driver = None
        return {"status": "success", "message": "Chrome closed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def is_open():
    global driver
    try:
        if driver is None:
            return {"status": "success", "is_open": False}
        driver.current_url
        return {"status": "success", "is_open": True, "url": driver.current_url}
    except:
        driver = None
        return {"status": "success", "is_open": False}


def play_youtube_async(video_id: str):
    """Asynchronously open YouTube video and start playback."""
    global driver, playback_thread
    
    def playback_task():
        try:
            # Ensure driver is initialized
            current_driver = get_driver()
            url = f"https://www.youtube.com/watch?v={video_id}"
            current_driver.get(url)
            
            # Wait for page to load and attempt to start playback
            time.sleep(5)  # Wait for player to load
            
            # Try to click the play button or video area
            try:
                # Click on the video player to start playback
                player = current_driver.find_element(By.CSS_SELECTOR, "#movie_player")
                player.click()
            except:
                # Alternative: click anywhere on the page
                try:
                    body = current_driver.find_element(By.TAG_NAME, "body")
                    body.click()
                except:
                    pass
        except Exception as e:
            print(f"Error in playback thread: {e}")
    
    # Stop any existing playback thread
    if playback_thread and playback_thread.is_alive():
        playback_thread.join(timeout=1)
    
    # Start new playback thread (non-blocking)
    playback_thread = threading.Thread(target=playback_task, daemon=True)
    playback_thread.start()
    
    return {
        "status": "success",
        "message": f"Started YouTube playback in background",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    
    try:
        data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    except:
        data = {}
    
    action = data.get("action", "")
    
    if action == "open":
        url = data.get("url", "about:blank")
        result = open_chrome(url)
    elif action == "navigate":
        url = data.get("url", "about:blank")
        result = navigate(url)
    elif action == "click":
        selector = data.get("selector", "")
        timeout = data.get("timeout", 10)
        result = click(selector, timeout)
    elif action == "type":
        selector = data.get("selector", "")
        text = data.get("text", "")
        clear = data.get("clear", True)
        result = type_text(selector, text, clear)
    elif action == "get_text":
        selector = data.get("selector", "")
        result = get_text(selector)
    elif action == "get_attribute":
        selector = data.get("selector", "")
        attribute = data.get("attribute", "href")
        result = get_attribute(selector, attribute)
    elif action == "title":
        result = get_title()
    elif action == "screenshot":
        filename = data.get("filename", None)
        result = screenshot(filename)
    elif action == "script":
        script = data.get("script", "")
        result = execute_script(script)
    elif action == "html":
        result = get_page_source()
    elif action == "close":
        result = close_browser()
    elif action == "is_open":
        result = is_open()
    elif action == "play_youtube":
        video_id = data.get("video_id", "")
        result = play_youtube_async(video_id)
    else:
        result = {"status": "error", "message": f"Unknown action: {action}"}
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()
