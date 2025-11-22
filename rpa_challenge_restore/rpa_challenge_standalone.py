"""
rpa_challenge_standalone.py
------------------------------------------------
Reliable version for the current https://www.rpachallenge.com/
Uses JavaScript to enter data so Angular registers the input.
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

URL = "https://www.rpachallenge.com/"

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------
def setup_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("detach", True)
    service = Service()
    driver = webdriver.Chrome(service=service, options=opts)
    driver.implicitly_wait(5)
    return driver


# ------------------------------------------------------------
# Excel helpers
# ------------------------------------------------------------
def download_excel(driver):
    print("[⬇️] Downloading Excel sample…")
    link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'.xlsx')]"))
    )
    link.click()
    time.sleep(3)


def load_excel_from_downloads():
    downloads = os.path.expanduser("~/Downloads")
    for f in os.listdir(downloads):
        if f.lower().endswith(".xlsx") and "challenge" in f.lower():
            path = os.path.join(downloads, f)
            print(f"[📊] Using Excel file: {path}")
            return pd.read_excel(path)
    raise FileNotFoundError("❌ Excel file not found in Downloads.")


# ------------------------------------------------------------
# Fill form using JS
# ------------------------------------------------------------
def fill_record(driver, record):
    """Fill form fields with JavaScript so Angular updates them."""
    mapping = {
        "labelFirstName": "First Name",
        "labelLastName": "Last Name",
        "labelCompanyName": "Company Name",
        "labelRole": "Role in Company",
        "labelAddress": "Address",
        "labelEmail": "Email",
        "labelPhone": "Phone Number",
    }

    for reflect, col in mapping.items():
        try:
            elem = driver.find_element(By.XPATH, f"//input[@ng-reflect-name='{reflect}']")
            value = str(record[col])
            driver.execute_script("arguments[0].value = arguments[1];", elem, value)
        except Exception as e:
            print(f"[⚠️] Could not fill {col}: {e}")

    # trigger Angular change detection via JS
    driver.execute_script(
        "for(const e of document.querySelectorAll('input')){e.dispatchEvent(new Event('input',{bubbles:true}))}"
    )

    # click Submit
    try:
        driver.find_element(By.XPATH, "//input[@type='submit' or @value='Submit']").click()
    except Exception as e:
        print("[⚠️] Submit click failed:", e)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print("[🧭] Launching browser…")
    driver = setup_driver()
    driver.get(URL)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Start']"))
    )
    print("[✅] Page loaded successfully.")

    download_excel(driver)
    df = load_excel_from_downloads()
    print(f"[✅] Loaded {len(df)} rows from Excel.")

    driver.find_element(By.XPATH, "//button[text()='Start']").click()
    print("[▶️] Challenge started — filling in data…")

    for i, r in df.iterrows():
        fill_record(driver, r)
        print(f"[✅] Submitted record {i+1}/{len(df)}")
        time.sleep(0.3)

    print("[🎯] Challenge completed successfully!")
    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()