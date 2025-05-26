from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as se

# Paths to your saved url lists
REC_ART_URLS_PATH = "../data/raw_pages/recipes_articles_urls.json"
BRAND_PROD_URLS_PATH = "../data/raw_pages/brand_products.json"
OUTPUT_PATH = "../data/raw_pages/processed.json"

BASE_URL = "https://www.madewithnestle.ca"

def dismiss_cookies(driver):
    try:
        buttons = driver.find_elements("css selector", "button, a")
        for btn in buttons:
            text = btn.text.strip().lower()
            if text in ("accept all cookies", "accept all", "i accept", "agree", "accept"):
                if btn.is_displayed():
                    btn.click()
                    print("Cookie banner dismissed.")
                    time.sleep(1.5)
                    return
        consent_btn = driver.find_element("id", "onetrust-accept-btn-handler")
        if consent_btn.is_displayed():
            consent_btn.click()
            print("Cookie banner dismissed (OneTrust button).")
            time.sleep(1.5)
    except Exception:
        pass

def extract_recipe_content(driver, url):
    driver.get(url)
    dismiss_cookies(driver)
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
    dismiss_cookies(driver)
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

def safe_click(driver, element, timeout=5):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        element.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False

def extract_product_content(driver, url):
    driver.get(url)
    time.sleep(2)
    dismiss_cookies(driver)
    result = {"url": url, "type": "product", "title": "", "content": ""}

    # Title
    try:
        h1 = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//h1"))
        )
        result["title"] = h1.text.strip()
        print(f"Title: {result['title']}")
    except se.TimeoutException:
        print(f"[{url}] No title found")
        result["title"] = ""

    # Description
    try:
        desc_elem = driver.find_element(By.CSS_SELECTOR, "div.field.field--name-field-description")
        description = desc_elem.text.strip()
    except Exception:
        # Fallback: get first <p> after title in same container
        try:
            desc_elem = driver.find_element(By.XPATH, "//h1/../following-sibling::div//p[1]")
            description = desc_elem.text.strip()
        except Exception:
            description = ""
    print(f"Description: {description}")

    # Features & Benefits (tab is open by default)
    features = []
    try:
        features_list = driver.find_elements(
            By.XPATH,
            "//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'feature')]/following-sibling::ul[1]/li"
        )
        features = [li.text.strip() for li in features_list if li.text.strip()]
        print(f"Features: {features}")
    except Exception:
        features = []

    # Nutrition tab (must be clicked)
    nutrition_rows = []
    try:
        nutrition_tab = driver.find_element(By.XPATH, "//a[contains(@href, '#') and contains(., 'Nutrition')]")
        safe_click(driver, nutrition_tab)
        print("Clicked Nutrition tab")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nutrition_tab)
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'nutrition')]")
            )
        )
        time.sleep(2)
        # Try to find all rows by searching all relevant divs under the main nutrition container
        nutrition_panel = driver.find_element(By.XPATH, "//div[contains(@class, 'nutrients-container')]")
        row_candidates = nutrition_panel.find_elements(By.XPATH, ".//div[contains(@class,'coh-row-inner')]")
        for row in row_candidates:
            columns = row.find_elements(By.XPATH, ".//div[contains(@class, 'views-field')]")
            if not columns:
                columns = row.find_elements(By.XPATH, "./div")
            row_texts = [col.text.strip() for col in columns if col.text.strip()]
            if len(row_texts) == 1:  # Some rows are just a header
                nutrition_rows.append([row_texts[0], "", ""])
            elif len(row_texts) == 2:
                nutrition_rows.append([row_texts[0], row_texts[1], ""])
            elif len(row_texts) >= 3:
                nutrition_rows.append(row_texts[:3])
    except Exception as e:
        print(f"Could not parse nutrition info: {e}")
    print(f"Nutrition: {nutrition_rows}")

    # Ingredients
    try:
        ingredients_tab = driver.find_element(By.XPATH, "//a[contains(@href, '#') and contains(., 'Ingredients')]")
        safe_click(driver, ingredients_tab)
        WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ingredients')]")
            )
        )
        time.sleep(2)
    except Exception:
        print("Ingredients tab click failed")

    # After clicking the Ingredients tab and waiting for it to load
    try:
        # 1. Find the Ingredients heading
        ingredients_h2 = driver.find_element(
            By.XPATH,
            "//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ingredients')]"
        )
        # 2. Find the *first* following sibling that's a container for ingredients (could be div/span)
        # This will grab div/span containers that hold the ingredient text
        sibling = ingredients_h2.find_element(By.XPATH, "following-sibling::*[1]")
        # 3. Gather all text from all elements under this sibling
        blocks = sibling.find_elements(By.XPATH, ".//*")
        texts = []
        if sibling.text.strip():
            texts.append(sibling.text.strip())
        for block in blocks:
            text = block.text.strip()
            if text and text not in texts:
                texts.append(text)
        ingredients = "\n".join(texts)
    except Exception:
        ingredients = ""

    print(f"Ingredients: {ingredients}")

    # Build "content" text (matches your recipes/articles logic)
    content_parts = []

    if description:
        content_parts.append(description)

    if features:
        content_parts.append("Features and Benefits:\n" + "\n".join(f"- {f}" for f in features))

    if nutrition_rows:
        nutrition_text = ["Nutrition Information:"]
        for row in nutrition_rows:
            # row is [label, amount, percent] (percent may be empty)
            if len(row) == 3 and row[2]:
                nutrition_text.append(f"{row[0]}: {row[1]} ({row[2]})")
            else:
                nutrition_text.append(f"{row[0]}: {row[1]}")
        content_parts.append("\n".join(nutrition_text))

    if ingredients:
        content_parts.append("Ingredients:\n" + ingredients)

    result["content"] = "\n\n".join(content_parts)
    return result

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Load url lists
    with open(REC_ART_URLS_PATH, "r", encoding="utf-8") as f:
        url_data = json.load(f)
    with open(BRAND_PROD_URLS_PATH, "r", encoding="utf-8") as f:
        brand_products = json.load(f)

    recipe_urls = url_data.get("recipes", [])
    article_urls = url_data.get("articles", [])
    product_urls = []
    for entry in brand_products:
        product_urls.extend(entry.get("products", []))
    product_urls = list(set(product_urls))  # deduplicate

    all_data = []

    # Scrape products
    for i, url in enumerate(product_urls):
        print(f"[Product {i+1}/{len(product_urls)}] {url}")
        try:
            product = extract_product_content(driver, url)
            print(product)
            all_data.append(product)
        except Exception as e:
            print(f"Failed to scrape product {url}: {e}")

    # Scrape recipes
    for i, url in enumerate(recipe_urls):
        print(f"[Recipe {i+1}/{len(recipe_urls)}] {url}")
        try:
            all_data.append(extract_recipe_content(driver, url))
        except Exception as e:
            print(f"Failed to scrape recipe {url}: {e}")

    # Scrape articles
    for i, url in enumerate(article_urls):
        print(f"[Article {i+1}/{len(article_urls)}] {url}")
        try:
            all_data.append(extract_article_content(driver, url))
        except Exception as e:
            print(f"Failed to scrape article {url}: {e}")

    driver.quit()

    # Save all data
    out_path = Path(OUTPUT_PATH)
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_data)} records to {out_path.resolve()}")

if __name__ == "__main__":
    main()
