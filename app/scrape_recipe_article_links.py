from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import selenium.common.exceptions
import json
import time
from pathlib import Path

BASE_URL = "https://www.madewithnestle.ca"
RECIPE_START_URL = f"{BASE_URL}/recipes"
ARTICLE_START_URL = f"{BASE_URL}/articles"

def dismiss_cookies(driver):
    # Try common OneTrust button selectors
    try:
        # Try the Accept All cookies button (text/cases may vary)
        buttons = driver.find_elements("css selector", "button, a")
        for btn in buttons:
            text = btn.text.strip().lower()
            if text in ("accept all cookies", "accept all", "i accept", "agree", "accept"):
                if btn.is_displayed():
                    btn.click()
                    print("Cookie banner dismissed.")
                    time.sleep(1.5)
                    return
        # If not found by text, try OneTrust-specific class
        consent_btn = driver.find_element("id", "onetrust-accept-btn-handler")
        if consent_btn.is_displayed():
            consent_btn.click()
            print("Cookie banner dismissed (OneTrust button).")
            time.sleep(1.5)
    except selenium.common.exceptions.NoSuchElementException:
        print("No cookie consent banner found.")
    except Exception as e:
        print("Error dismissing cookie banner:", e)

def close_survey_iframe(driver):
    try:
        # Wait a moment for iframe to appear
        time.sleep(1)
        # Find all iframes
        iframes = driver.find_elements("tag name", "iframe")
        for iframe in iframes:
            # Heuristically: only target big visible iframes with no src or named "survey"
            if iframe.is_displayed():
                # Option 1: Try to click the close button inside the iframe
                driver.switch_to.frame(iframe)
                try:
                    # Look for a close button (you may need to adjust selector/text)
                    close_btns = driver.find_elements("css selector", "button, .close, .close-button, [aria-label='close']")
                    for btn in close_btns:
                        if btn.is_displayed() and ("close" in btn.get_attribute("class").lower() or btn.text.strip().lower() in ("close", "×", "no thanks")):
                            btn.click()
                            print("Closed survey popup.")
                            time.sleep(1)
                            break
                except Exception:
                    pass
                driver.switch_to.default_content()
                # Option 2: If can't close, hide the iframe
                driver.execute_script("arguments[0].style.display = 'none';", iframe)
                print("Survey iframe hidden.")
    except selenium.common.exceptions.NoSuchElementException:
        pass
    except Exception as e:
        print("Error handling survey iframe:", e)

def close_qualtrics_survey(driver):
    try:
        # Find all visible survey overlays
        overlays = driver.find_elements("css selector", 'div[class^="QSIWebResponsive-creative-container"]')
        for overlay in overlays:
            if overlay.is_displayed():
                # Try to find the close button inside the overlay
                try:
                    close_btn = overlay.find_element("css selector", 'div[role="button"], button, .QSIWebResponsiveDialog-Icon')
                    # Try by aria-label
                    if close_btn.is_displayed() and (
                        close_btn.get_attribute("aria-label") in ("Close", "close") or
                        close_btn.text.strip() in ("✕", "X", "Close")
                    ):
                        close_btn.click()
                        print("Qualtrics survey closed (X button).")
                        time.sleep(1)
                        return
                except Exception:
                    # Fallback: click any close-looking button in overlay
                    buttons = overlay.find_elements("css selector", 'div[role="button"], button')
                    for btn in buttons:
                        if btn.is_displayed() and (
                            "close" in btn.get_attribute("class").lower() or
                            btn.text.strip() in ("✕", "X", "Close")
                        ):
                            btn.click()
                            print("Qualtrics survey closed (fallback).")
                            time.sleep(1)
                            return
                # If can't find, hide overlay as fallback
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
                print("Qualtrics overlay hidden as fallback.")
    except selenium.common.exceptions.NoSuchElementException:
        pass
    except Exception as e:
        print("Error handling Qualtrics survey overlay:", e)



def load_all_items_with_more_button(driver, max_clicks=100):

    clicks = 0
    while clicks < max_clicks:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Count current recipe cards
            prev_count = len(driver.find_elements(By.CSS_SELECTOR, "div.card--recipe"))

            # Find and click "More"
            buttons = driver.find_elements(By.CSS_SELECTOR, "div.views-pagination ul > li > a")
            more_found = False
            for button in buttons:
                if button.is_displayed() and button.text.strip().lower() == "more":
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5)
                    close_survey_iframe(driver)
                    close_qualtrics_survey(driver)
                    button.click()
                    clicks += 1
                    more_found = True
                    print(f"Clicked More button ({clicks})")
                    break

            if not more_found:
                print("No More button found in pagination.")
                break

            # Wait for new cards to load
            for _ in range(30):
                time.sleep(1)
                new_count = len(driver.find_elements(By.CSS_SELECTOR, "div.card--recipe"))
                if new_count > prev_count:
                    break

        except (TimeoutException, StaleElementReferenceException) as e:
            print(f"No More button found or not clickable: {e}")
            break

def load_all_items_with_more_button_articles(driver, max_clicks=100):

    clicks = 0
    while clicks < max_clicks:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Count current article cards
            prev_count = len(driver.find_elements(By.CSS_SELECTOR, "div.card--article"))

            # Find and click "More" (articles)
            buttons = driver.find_elements(By.CSS_SELECTOR, "body > div.dialog-off-canvas-main-canvas > main > div > div.views-element-container > div > ul > li > a")
            more_found = False
            for button in buttons:
                if button.is_displayed() and button.text.strip().lower() == "more":
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5)
                    close_survey_iframe(driver)
                    close_qualtrics_survey(driver)
                    button.click()
                    clicks += 1
                    more_found = True
                    print(f"Clicked More button ({clicks})")
                    break

            if not more_found:
                print("No More button found in pagination (articles).")
                break

            # Wait for new articles to load
            for _ in range(30):
                time.sleep(1)
                new_count = len(driver.find_elements(By.CSS_SELECTOR, "div.card--article"))
                if new_count > prev_count:
                    break

        except (TimeoutException, StaleElementReferenceException) as e:
            print(f"No More button found or not clickable (articles): {e}")
            break

def get_recipe_links(driver):
    # Go to the recipe page and load all recipes
    driver.get(RECIPE_START_URL)
    dismiss_cookies(driver)
    load_all_items_with_more_button(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/recipe/"):
            href = BASE_URL + href
            links.add(href)
        elif href.startswith(BASE_URL + "/recipe/"):
            links.add(href)
    return list(links)

def get_article_links(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/blog/" in href or "/news/" in href:
            if href.startswith("/"):
                href = BASE_URL + href
            links.add(href)
    return list(links)


def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # --- Recipes ---
    print("Loading recipes page and dismissing cookies...")
    driver.get(RECIPE_START_URL)
    dismiss_cookies(driver)
    load_all_items_with_more_button(driver)
    recipe_links = get_recipe_links(driver)
    print(f"Found {len(recipe_links)} recipes")

    # --- Articles ---
    print("Loading articles page and dismissing cookies...")
    driver.get(ARTICLE_START_URL)
    dismiss_cookies(driver)
    load_all_items_with_more_button_articles(driver)
    article_links = get_article_links(driver)
    print(f"Found {len(article_links)} articles")


    driver.quit()

    # Save to a file for later scraping
    out_dir = Path("../data/raw_pages")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "recipes_articles_urls.json"

    urls_data = {
        "recipes": recipe_links,
        "articles": article_links
    }

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(urls_data, f, ensure_ascii=False, indent=2)

    print(f"Saved URLs for {len(recipe_links)} recipes and {len(article_links)} articles → {out_file.resolve()}")


if __name__ == "__main__":
    main()