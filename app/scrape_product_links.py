from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import selenium.common.exceptions
import time
import json
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as se

BASE_URL = "https://www.madewithnestle.ca"

def dismiss_cookies(driver):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button, a")
        for btn in buttons:
            text = btn.text.strip().lower()
            if text in ("accept all cookies", "accept all", "i accept", "agree", "accept"):
                if btn.is_displayed():
                    btn.click()
                    print("Cookie banner dismissed.")
                    time.sleep(1.5)
                    return
        consent_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        if consent_btn.is_displayed():
            consent_btn.click()
            print("Cookie banner dismissed (OneTrust button).")
            time.sleep(1.5)
    except selenium.common.exceptions.NoSuchElementException:
        print("No cookie consent banner found.")
    except Exception as e:
        print("Error dismissing cookie banner:", e)

def get_all_brand_links(driver):
    brand_links = []
    seen = set()

    nav = driver.find_element(
        By.CSS_SELECTOR,
        "div.coh-container.menu-container.coh-ce-85526d0c-d6c221d7 nav > ul"
    )
    brand_dropdown = nav.find_element(By.CSS_SELECTOR, "li:nth-child(1) > span")
    ActionChains(driver).move_to_element(brand_dropdown).perform()
    time.sleep(1)

    # Only select first-level brand categories
    category_lis = nav.find_elements(
        By.CSS_SELECTOR,
        "li.coh-menu-list-item.js-coh-menu-item.has-children.is-expanded > div > div > ul > li.coh-menu-list-item.js-coh-menu-item.has-children"
    )
    print(f"Found {len(category_lis)} visible brand categories")

    for cat_idx, cat_li in enumerate(category_lis, 1):
        try:
            # Always re-hover Brand and this category
            ActionChains(driver).move_to_element(brand_dropdown).perform()
            time.sleep(0.5)
            cat_span = cat_li.find_element(By.TAG_NAME, "span")
            cat_name = cat_span.text.strip()
            print(f"Category {cat_idx}: {cat_name}")

            ActionChains(driver).move_to_element(cat_span).perform()
            time.sleep(1.2)

            # Now find brands in this category
            brand_li_elements = cat_li.find_elements(
                By.CSS_SELECTOR,
                "li.coh-menu-list-item.js-coh-menu-item.has-children.is-expanded > div > ul > li > a"
            )
            if not brand_li_elements:
                # Try fallback: get all a's in any ul beneath this cat_li
                brand_li_elements = cat_li.find_elements(By.CSS_SELECTOR, "div > ul > li > a")

            found_any = False
            for a in brand_li_elements:
                href = a.get_attribute("href")
                text = a.text.strip()
                if href and text and href not in seen:
                    brand_links.append({"name": text, "url": href})
                    seen.add(href)
                    print(f"    Brand: {text} - {href}")
                    found_any = True
            if not found_any:
                print("  No brands found in this category (may be empty).")

        except Exception as e:
            print(f"Error processing category {cat_idx}: {e}")
            continue

    return brand_links

def norm(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href.split("?", 1)[0]
    if href.startswith("/"):
        return f"{BASE_URL}{href}".split("?", 1)[0]
    return ""

def open_products_tab(driver):
    try:
        tab = driver.find_element(
            By.CSS_SELECTOR,
            "#block-nestlebrandsubmenu nav ul li:first-child a"
        )
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(0.5)
    except selenium.common.exceptions.NoSuchElementException:
        pass

def safe_click(driver, element, timeout=3):
    """Try three ways to click; return True on success."""
    try:                              # 1 ‑ regular click after scroll
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        element.click()
        return True
    except Exception:
        pass
    try:                              # 2 ‑ JS click
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        pass
    try:                              # 3 ‑ ActionChains click
        ActionChains(driver).move_to_element(element).click().perform()
        return True
    except Exception:
        return False                  # all methods failed

def expand_grid(driver, pause=0.7, max_rounds=25):
    """
    Click every 'More' / pager link inside #products until no new
    rows appear.  Works for /aero, /easter‑holiday, etc.
    """
    rounds = 0
    while rounds < max_rounds:
        rounds += 1

        # (re‑)locate any pager link on the current DOM
        pager_candidates = driver.find_elements(
            By.CSS_SELECTOR,
            "#products a.views-load-more__button, "
            "#products div.views-pagination a, "
            "#products ul.pager__items a.pager__link"
        )
        if not pager_candidates:        # fallback: text = 'More'
            pager_candidates = driver.find_elements(
                By.XPATH,
                "//div[@id='products']//a[normalize-space(text())='More']"
            )

        pager = next((el for el in pager_candidates if el.is_displayed()), None)
        if not pager:
            print("DEBUG: no visible pager → grid complete")
            break

        # current row count
        grid = driver.find_element(By.ID, "products")
        rows_before = len(grid.find_elements(By.CSS_SELECTOR, "div.views-row"))

        # centre‑scroll and JS‑click (avoids intercept problems)
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", pager)
        driver.execute_script("arguments[0].click();", pager)

        # wait (≤10s) until new rows appear
        t0 = time.time()
        while time.time() - t0 < 10:
            rows_after = len(
                grid.find_elements(By.CSS_SELECTOR, "div.views-row"))
            if rows_after > rows_before:
                print(f"   More click {rounds}: {rows_before} ▶ {rows_after}")
                break
            time.sleep(0.3)
        else:
            print("DEBUG: pager click timed‑out – continuing")
            # do NOT break; allow the outer loop to search again
            continue

        # small nudge so the next pager becomes visible
        # keep scrolling until a new visible pager appears or we hit bottom
        for _ in range(10):  # at most 10 × 400px = 4000px
            driver.execute_script("window.scrollBy(0, 400);")
            print("scrolling")
            time.sleep(0.15)
            try:
                next_pager = driver.find_element(
                    By.CSS_SELECTOR,
                    "#products a.views-load-more__button, "
                    "#products div.views-pagination a, "
                    "#products ul.pager__items a.pager__link"
                )
                if next_pager.is_displayed():
                    break  # pager now in view → ready for next loop
            except se.NoSuchElementException:
                break  # no more pager in DOM → grid done


def get_product_links_from_brand(driver, brand_url):
    if not brand_url.startswith(BASE_URL):
        print(f"[external] {brand_url} – skipped")
        return {"brand_url": brand_url, "products": []}

    driver.get(brand_url)
    time.sleep(1.2)
    open_products_tab(driver)

    try:
        container = driver.find_element(By.ID, "products")
    except selenium.common.exceptions.NoSuchElementException:
        print(f"[{brand_url}] – no #products")
        return {"brand_url": brand_url, "products": []}

    # nudge once so first pager is visible
    driver.execute_script("arguments[0].scrollIntoView();", container)
    driver.execute_script("window.scrollBy(0, 200);")
    time.sleep(0.4)

    expand_grid(driver)

    anchors = container.find_elements(By.TAG_NAME, "a")
    root = brand_url.rstrip("/")
    links = set()

    for a in anchors:
        try:  # skip if DOM replaced
            href = norm(a.get_attribute("href"))
        except se.StaleElementReferenceException:
            continue
        if not href.startswith(BASE_URL):
            continue
        if href.rstrip("/") == root:  # self‑link
            continue
        links.add(href)

    print(f"[{brand_url}] – total products: {len(links)}")
    return {"brand_url": brand_url, "products": sorted(links)}



options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(BASE_URL)
dismiss_cookies(driver)

brand_links = get_all_brand_links(driver)
print(f"Total unique brands: {len(brand_links)}")

# loop over all brand dictionaries you already collected
all_brand_data = []
for brand in brand_links:
    data = get_product_links_from_brand(driver, brand["url"])
    all_brand_data.append(data)
    print(data)

driver.quit()

# ── NEW: persist to a file ────────────────
out_dir  = Path("../data/raw_pages")
out_dir.mkdir(exist_ok=True)            # create ./data if it doesn’t exist
out_file = out_dir / "brand_products.json"

with out_file.open("w", encoding="utf‑8") as f:
    json.dump(all_brand_data, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(all_brand_data)} brand records → {out_file.resolve()}")