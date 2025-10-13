"""
selenium_real_test.py | RIK-Fail-Safe Full Visual Demo with Audit Logging
---------------------------------------------------------------------------
Logs each step, error, and recovery to a JSON file in the 'audit_logs/' folder.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from rik_fail_safe.fallback_core import (
    diagnose,
    generate_strategies,
    simulate_counterfactuals,
    execute_best_strategy,
    explain_success,
)
import os, json, time, datetime

# === Create audit folder ===
LOG_DIR = os.path.join(os.path.dirname(__file__), "audit_logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def log_event(event_type, message, data=None):
    """Append a structured log entry to the JSON audit file."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "message": message,
        "data": data or {}
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[🧾 LOGGED] {event_type}: {message}")


def safe_action(description, action_fn):
    """Run a browser action and let RIK-Fail-Safe reason about any failure."""
    try:
        log_event("ACTION", description)
        action_fn()
    except Exception as e:
        log_event("EXCEPTION", f"{description} failed", {"error": str(e)})
        diag = diagnose(e, {"step": description})
        strats = generate_strategies(diag)
        sims = simulate_counterfactuals(strats)
        result = execute_best_strategy(sims)
        explain_success(result)
        log_event("RECOVERY", f"{description} recovered", {"strategy": result})


def run_real_selenium_test():
    print("\n🧩 Running RIK-Fail-Safe Full Visual Demo (with Audit Logging)...\n")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    service = Service("/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        log_event("START", "Launching browser and navigating to form")
        driver.get("https://www.selenium.dev/selenium/web/web-form.html")
        time.sleep(1)

        # === Fill out all fields ===
        safe_action("Typing into text box", lambda: driver.find_element(By.NAME, "my-text").send_keys("Recursive Intelligence"))
        safe_action("Entering password", lambda: driver.find_element(By.NAME, "my-password").send_keys("secret123"))
        safe_action("Writing message", lambda: driver.find_element(By.NAME, "my-textarea").send_keys("RIK-Fail-Safe live demo"))
        safe_action("Selecting Option 2", lambda: driver.find_element(By.NAME, "my-select").send_keys("Option 2"))
        safe_action("Toggling checkbox", lambda: driver.find_element(By.NAME, "my-check-1").click())
        safe_action("Selecting radio button", lambda: driver.find_element(By.NAME, "my-radio").click())
        safe_action("Picking color", lambda: driver.find_element(By.NAME, "my-color").send_keys("#00ffcc"))
        safe_action("Choosing date", lambda: driver.find_element(By.NAME, "my-date").send_keys("2025-10-10"))
        safe_action("Choosing file (simulate)", lambda: driver.find_element(By.NAME, "my-file").send_keys("/etc/hosts"))

        # === Intentional failure for recovery demonstration ===
        safe_action("Clicking missing field (intentional error)", lambda: driver.find_element(By.ID, "missing-field").click())

        # === Submit ===
        def submit_with_failure_then_success():
            try:
                driver.find_element(By.ID, "submit-not-real").click()
            except Exception:
                log_event("FALLBACK", "Using correct submit button selector")
                driver.find_element(By.CSS_SELECTOR, "button").click()

        safe_action("Submitting form", submit_with_failure_then_success)
        log_event("SUCCESS", "Form submitted successfully")

    finally:
        time.sleep(3)
        driver.quit()
        log_event("END", "Browser closed and session complete")
        print(f"\n[🧠] Demo complete — audit log saved to:\n{LOG_FILE}\n")


if __name__ == "__main__":
    run_real_selenium_test()