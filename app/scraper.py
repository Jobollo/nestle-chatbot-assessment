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


def extract_recipe_content(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.find("h1").text.strip() if soup.find("h1") else ""

    description = ""
    h1 = soup.find("h1")
    if h1:
        p = h1.find_next("p")
        if p:
            description = p.get_text(strip=True)

    ingredients = []
    for div in soup.find_all("div", class_=lambda x: x and "field--name-field-ingredient-fullname" in x):
        text = div.get_text(separator=" ", strip=True)
        if text:
            ingredients.append(text)
    ingredients_block = "\n".join(ingredients)

    instructions = []
    section_with_instructions = None
    for section in soup.find_all("div", class_=lambda x: x and "recipe__content-box" in x):
        h2 = section.find("h2", string=lambda s: s and "how to prepare" in s.lower())
        if h2:
            section_with_instructions = section
            for article in section.find_all("article"):
                step_num = article.find("span", class_="coh-inline-element step-number")
                step_text = article.find("p", class_="coh-paragraph")
                if step_num and step_text:
                    instructions.append(f"{step_num.text.strip()}. {step_text.text.strip()}")
            break

    instructions_block = "\n".join(instructions)

    tips = []
    if section_with_instructions:
        for col in section_with_instructions.find_all("div", class_="coh-column content-half coh-col-xl"):
            h3 = col.find("h3")
            if h3 and "tips" in h3.get_text(strip=True).lower():
                for para in col.find_all("p", class_="coh-paragraph"):
                    text = para.get_text(separator=" ", strip=True)
                    if text:
                        tips.append(text)
                break

    tips_block = "\n".join(tips)

    content = "\n\n".join(filter(None, [
        description,
        "Ingredients:\n" + ingredients_block if ingredients_block else "",
        "Instructions:\n" + instructions_block if instructions_block else "",
        "Tips:\n" + tips_block if tips_block else ""
    ]))
    return {
        "url": url,
        "type": "recipe",
        "title": title,
        "content": content
    }

def extract_article_content(driver, url):
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.find("h1").text.strip() if soup.find("h1") else ""
    content_div = soup.find("div", class_="coh-container coh-ce-0c411d4b")
    if not content_div:
        article = soup.find("article")
        if article:
            divs = article.find_all("div", class_="coh-container")
            if divs:
                content_div = max(divs, key=lambda d: len(d.text))
    content_blocks = []
    if content_div:
        for elem in content_div.find_all(["p", "li"], recursive=True):
            text = elem.get_text(separator=" ", strip=True)
            if text:
                content_blocks.append(text)
    body = "\n".join(content_blocks)
    return {
        "url": url,
        "type": "article",
        "title": title,
        "content": body
    }

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

    data = []

    # --- Scrape recipes ---
    for i, url in enumerate(recipe_links):
        print(f"[Recipe {i+1}/{len(recipe_links)}] {url}")
        try:
            data.append(extract_recipe_content(driver, url))
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    # --- Scrape articles ---
    for i, url in enumerate(article_links):
        print(f"[Article {i+1}/{len(article_links)}] {url}")
        try:
            data.append(extract_article_content(driver, url))
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    driver.quit()

    # --- Save data ---
    with open("../data/raw_pages/processed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
