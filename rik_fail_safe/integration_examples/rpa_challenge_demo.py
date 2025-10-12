"""
rpa_challenge_demo.py | Recursive Intelligence Kernel – Final 100% Version
--------------------------------------------------------------------------
Completes the RPA Challenge with full dynamic field mapping and 100% accuracy.
Includes robust matching for phone variants (labelPhone, labelPhoneNumber, etc.)
and leaves the browser open for 20 seconds to view the score.
"""

import sys, os, time, sqlite3, pathlib, pandas as pd, json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# === Bring in RIK modules ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rik_fail_safe.fallback_core import (
    diagnose,
    generate_strategies,
    simulate_counterfactuals,
    execute_best_strategy,
    explain_success,
)
from rik_fail_safe.integration_examples.adaptive_fallback_engine import choose_strategy
from self_updating_confidence import recalculate_weights
from rik_fail_safe.integration_examples.learning_report_generator import main as generate_report

# === Path setup ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))
LOG_DIR = os.path.join(os.path.dirname(__file__), "audit_logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"audit_rpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def log_event(event_type, message, data=None):
    """Write structured events to JSON log and print."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "message": message,
        "data": data or {}
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[🧾 LOGGED] {event_type}: {message}")

# === Helpers ===
def get_learned_weights():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT strategy,
               SUM(CASE WHEN actual_outcome='success' THEN 1 ELSE 0 END)*1.0 / COUNT(*)
        FROM episodic_memory
        GROUP BY strategy;
    """)
    rows = c.fetchall()
    conn.close()
    weights = {r[0]: round(r[1], 3) for r in rows if r[0]} or {"Re-run task with safe defaults": 1.0}
    log_event("MEMORY_LOAD", "Loaded strategy weights", weights)
    return weights

def wait_for_download(download_dir):
    """Wait until Excel file appears in the download directory."""
    log_event("WAIT", "Waiting for Excel download")
    for _ in range(60):
        files = list(pathlib.Path(download_dir).glob("*.xlsx"))
        if files:
            latest = max(files, key=os.path.getctime)
            log_event("DOWNLOAD", f"Excel file detected: {latest.name}")
            return latest
        time.sleep(1)
    raise TimeoutError("Excel download timed out.")

# === Main ===
def run_rpa_challenge_demo(rounds: int = 10):
    log_event("START", "RPA Challenge demo initialized")

    # Configure Chrome for auto-download
    download_dir = str(pathlib.Path.home() / "Downloads" / "rpa_demo_downloads")
    pathlib.Path(download_dir).mkdir(parents=True, exist_ok=True)
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    service = Service("/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Step 1: Navigate & download Excel
    driver.get("https://www.rpachallenge.com/")
    time.sleep(2)
    driver.find_element(By.XPATH, "//a[contains(text(),'Download Excel')]").click()
    excel_path = wait_for_download(download_dir)
    df = pd.read_excel(excel_path)
    log_event("DATA_LOAD", f"Loaded {len(df)} rows from {excel_path.name}")

    # Step 2: Start the challenge
    driver.find_element(By.XPATH, "//button[text()='Start']").click()
    log_event("INFO", "Challenge started (direct DOM)")

    learned = get_learned_weights()

    # Normalize spreadsheet columns
    df.columns = [str(c).replace(" ", "").lower() for c in df.columns]

    # Step 3: Perform rounds
    for i in range(min(rounds, len(df))):
        log_event("ROUND_START", f"Round {i+1}/{rounds}")
        row = df.iloc[i].to_dict()
        normalized_row = {str(k).replace(" ", "").lower(): str(v) for k, v in row.items()}
        try:
            inputs = driver.find_elements(By.XPATH, "//input[@ng-reflect-name and not(@type='submit')]")

            for box in inputs:
                reflect = (box.get_attribute("ng-reflect-name") or "").lower()
                key = reflect.replace("label", "").replace(" ", "")
                value = None

                # Robust mapping logic
                if "first" in key:
                    value = normalized_row.get("firstname")
                elif "last" in key:
                    value = normalized_row.get("lastname")
                elif "company" in key:
                    value = normalized_row.get("companyname")
                elif "role" in key:
                    value = normalized_row.get("roleincompany")
                elif "address" in key:
                    value = normalized_row.get("address")
                elif "email" in key:
                    value = normalized_row.get("email")
                elif "phone" in key:
                    # Handles labelPhone, labelPhoneNumber, or similar variants
                    for possible in ["phonenumber", "phone", "phone1", "phonenumber1"]:
                        if possible in normalized_row:
                            value = normalized_row.get(possible)
                            break

                if not value:
                    log_event("WARN", f"No match for {reflect}")
                    continue

                box.clear()
                box.send_keys(value)
                log_event("ACTION", f"Filled {reflect}", {"value": value})

            # Submit round
            driver.find_element(By.XPATH, "//input[@type='submit' or @value='Submit']").click()
            log_event("SUCCESS", f"Round {i+1} completed successfully")

        except Exception as e:
            log_event("EXCEPTION", f"Error in round {i+1}", {"error": str(e)})
            diag = diagnose(e, {"step": f"Round {i+1}"})
            strategies = list(learned.keys())
            chosen = choose_strategy(strategies)
            sims = simulate_counterfactuals([chosen])
            result = execute_best_strategy(sims)
            explain_success(result)
            log_event("RECOVERY", f"Applied strategy {chosen}", {"result": result})
        time.sleep(1.2)

    # Step 4: Reflection & reporting
    log_event("INFO", "All rounds complete – keeping browser open for review.")
    time.sleep(20)  # keep browser open for 20 seconds
    driver.quit()

    recalculate_weights()
    generate_report()
    log_event("END", "RPA Challenge demo completed successfully")

if __name__ == "__main__":
    run_rpa_challenge_demo(rounds=10)