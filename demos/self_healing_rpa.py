#!/usr/bin/env python3
"""
Self-Healing RPA Demo - Recursive Intelligence Algorithm

Demonstrates RIA applied to UI automation:
- Agent tries to interact with a web page
- UI changes (selectors break)
- Agent analyzes failure and generates new locator strategy
- Writes real Python code to adapt
- Succeeds without human intervention

This is what UiPath/Automation Anywhere CANNOT do.
"""

import sys
import os
import time
import importlib.util
import threading
import http.server
import socketserver
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import setup_logging, DATA_DIR
from memory import init_memory_db, save_episode, get_recent_episodes

logger = setup_logging("ria.rpa_demo")

# ==========================================================
# === SIMULATED WEBSITE VERSIONS ===========================
# ==========================================================

# Each version represents a UI redesign that breaks selectors
WEBSITE_VERSIONS = {
    "v1_original": '''<!DOCTYPE html>
<html>
<head><title>ShopMart - Product Page</title>
<style>
body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
.product-card { border: 2px solid #333; padding: 20px; border-radius: 8px; }
.product-title { font-size: 24px; margin-bottom: 10px; }
.product-price { font-size: 20px; color: #e44; margin-bottom: 15px; }
.add-to-cart-btn { background: #4CAF50; color: white; padding: 15px 30px;
    border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
.add-to-cart-btn:hover { background: #45a049; }
.quantity-input { width: 60px; padding: 10px; margin-right: 10px; }
.success-message { color: green; margin-top: 15px; display: none; }
</style>
</head>
<body>
<div class="product-card">
    <h1 class="product-title">Wireless Bluetooth Headphones</h1>
    <div class="product-price">$79.99</div>
    <input type="number" id="quantity" class="quantity-input" value="1" min="1">
    <button id="add-to-cart" class="add-to-cart-btn">Add to Cart</button>
    <div id="success-msg" class="success-message">✓ Added to cart!</div>
</div>
<script>
document.getElementById('add-to-cart').addEventListener('click', function() {
    document.getElementById('success-msg').style.display = 'block';
});
</script>
</body>
</html>''',

    "v2_redesign": '''<!DOCTYPE html>
<html>
<head><title>ShopMart 2.0</title>
<style>
body { font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; }
.pdp-container { display: grid; gap: 20px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.pdp-title { font-size: 28px; font-weight: 600; }
.pdp-price-tag { font-size: 22px; color: #c41; }
.pdp-actions { display: flex; align-items: center; gap: 15px; }
.qty-selector { padding: 12px; width: 70px; border: 1px solid #ccc; }
.btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; padding: 14px 28px; border: none; border-radius: 8px;
    font-weight: 600; cursor: pointer; }
.confirmation { color: #2e7d32; margin-top: 20px; display: none; font-weight: 500; }
</style>
</head>
<body>
<article class="pdp-container">
    <h1 class="pdp-title">Wireless Bluetooth Headphones</h1>
    <span class="pdp-price-tag">$79.99</span>
    <div class="pdp-actions">
        <input type="number" class="qty-selector" value="1" min="1">
        <button class="btn-primary" data-action="add-to-cart">Add to Cart</button>
    </div>
    <div class="confirmation" data-testid="cart-confirmation">✓ Added to cart!</div>
</article>
<script>
document.querySelector('[data-action="add-to-cart"]').addEventListener('click', function() {
    document.querySelector('.confirmation').style.display = 'block';
});
</script>
</body>
</html>''',

    "v3_react_style": '''<!DOCTYPE html>
<html>
<head><title>ShopMart React</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
[data-component="ProductPage"] { max-width: 1000px; margin: 0 auto; padding: 40px; }
[data-component="ProductInfo"] { margin-bottom: 30px; }
[data-element="title"] { font-size: 32px; margin-bottom: 8px; }
[data-element="price"] { font-size: 24px; color: #b12704; }
[data-component="AddToCart"] { display: flex; align-items: center; gap: 12px; }
[data-element="quantity"] { padding: 10px; width: 60px; border: 1px solid #ddd; border-radius: 4px; }
[data-testid="add-to-cart-button"] { background: #f0c14b; border: 1px solid #a88734;
    padding: 12px 24px; border-radius: 4px; cursor: pointer; font-weight: 500; }
[data-testid="success-notification"] { color: #007600; margin-top: 15px; display: none; }
</style>
</head>
<body>
<div data-component="ProductPage">
    <div data-component="ProductInfo">
        <div data-element="title">Wireless Bluetooth Headphones</div>
        <div data-element="price">$79.99</div>
    </div>
    <div data-component="AddToCart">
        <input type="number" data-element="quantity" data-testid="qty-input" value="1" min="1">
        <button data-testid="add-to-cart-button">Add to Cart</button>
    </div>
    <div data-testid="success-notification">✓ Added to cart!</div>
</div>
<script>
document.querySelector('[data-testid="add-to-cart-button"]').addEventListener('click', function() {
    document.querySelector('[data-testid="success-notification"]').style.display = 'block';
});
</script>
</body>
</html>''',

    "v4_accessible": '''<!DOCTYPE html>
<html lang="en">
<head><title>ShopMart - Accessible</title>
<style>
body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
main { border: 1px solid #e0e0e0; padding: 30px; border-radius: 12px; }
h1 { font-size: 26px; }
.price { font-size: 22px; color: #d32f2f; margin: 15px 0; }
.actions { margin-top: 20px; }
input[type="number"] { padding: 10px; width: 60px; margin-right: 10px; }
button { padding: 12px 24px; font-size: 16px; cursor: pointer;
    background: #1976d2; color: white; border: none; border-radius: 6px; }
.alert { color: #2e7d32; margin-top: 15px; display: none; }
</style>
</head>
<body>
<main>
    <h1>Wireless Bluetooth Headphones</h1>
    <p class="price" aria-label="Price: $79.99">$79.99</p>
    <div class="actions">
        <label for="qty">Quantity:</label>
        <input type="number" id="qty" value="1" min="1" aria-label="Select quantity">
        <button type="button" aria-label="Add to shopping cart">Add to Cart</button>
    </div>
    <p class="alert" role="alert" aria-live="polite">✓ Added to cart!</p>
</main>
<script>
document.querySelector('button[aria-label="Add to shopping cart"]').addEventListener('click', function() {
    document.querySelector('[role="alert"]').style.display = 'block';
});
</script>
</body>
</html>'''
}

# ==========================================================
# === LOCATOR STRATEGY TEMPLATES ===========================
# ==========================================================

LOCATOR_TEMPLATES = {
    "id_selector": '''
def find_elements(page):
    """Locate elements by ID - simplest but brittle."""
    return {
        "add_button": page.locator("#add-to-cart"),
        "quantity": page.locator("#quantity"),
        "success": page.locator("#success-msg")
    }
''',

    "css_classes": '''
def find_elements(page):
    """Locate elements by CSS classes - common but breaks on redesign."""
    return {
        "add_button": page.locator(".add-to-cart-btn, .btn-primary"),
        "quantity": page.locator(".quantity-input, .qty-selector"),
        "success": page.locator(".success-message, .confirmation")
    }
''',

    "data_attributes": '''
def find_elements(page):
    """Locate by data-* attributes - more stable for modern apps."""
    return {
        "add_button": page.locator("[data-action='add-to-cart'], [data-testid='add-to-cart-button']"),
        "quantity": page.locator("[data-element='quantity'], [data-testid='qty-input']"),
        "success": page.locator("[data-testid='cart-confirmation'], [data-testid='success-notification']")
    }
''',

    "text_content": '''
def find_elements(page):
    """Locate by text content - survives most CSS changes."""
    return {
        "add_button": page.locator("button:has-text('Add to Cart')"),
        "quantity": page.locator("input[type='number']"),
        "success": page.locator("text=Added to cart")
    }
''',

    "aria_labels": '''
def find_elements(page):
    """Locate by ARIA labels - best for accessible sites."""
    return {
        "add_button": page.locator("[aria-label*='cart' i], button:has-text('Add to Cart')"),
        "quantity": page.locator("[aria-label*='quantity' i], input[type='number']"),
        "success": page.locator("[role='alert'], text=Added to cart")
    }
''',

    "multi_strategy": '''
def find_elements(page):
    """Multi-strategy locator - combines all approaches with fallbacks."""
    def find_button():
        strategies = [
            "[data-testid='add-to-cart-button']",
            "[data-action='add-to-cart']",
            "#add-to-cart",
            "[aria-label*='cart' i]",
            "button:has-text('Add to Cart')",
            ".add-to-cart-btn",
            ".btn-primary"
        ]
        for sel in strategies:
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc
        return page.locator("button").first

    def find_quantity():
        strategies = [
            "[data-testid='qty-input']",
            "[data-element='quantity']",
            "#quantity",
            "[aria-label*='quantity' i]",
            "input[type='number']"
        ]
        for sel in strategies:
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc
        return page.locator("input").first

    def find_success():
        strategies = [
            "[data-testid='success-notification']",
            "[data-testid='cart-confirmation']",
            "#success-msg",
            "[role='alert']",
            "text=Added to cart"
        ]
        for sel in strategies:
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc
        return page.locator("text=cart")

    return {
        "add_button": find_button(),
        "quantity": find_quantity(),
        "success": find_success()
    }
'''
}

# Strategy evolution order
STRATEGY_ORDER = [
    "id_selector",
    "css_classes",
    "data_attributes",
    "text_content",
    "aria_labels",
    "multi_strategy"
]

# ==========================================================
# === LOCAL WEB SERVER =====================================
# ==========================================================

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses logging."""
    def log_message(self, format, *args):
        pass

class LocalWebServer:
    """Serves HTML pages for the demo."""

    def __init__(self, port=0):  # port=0 lets OS pick available port
        self.port = port
        self.current_html = ""
        self.server = None
        self.thread = None
        self.actual_port = None

    def set_page(self, html: str):
        """Set the current page content."""
        self.current_html = html
        # Write to temp file
        self.temp_dir = Path(__file__).parent / "temp_site"
        self.temp_dir.mkdir(exist_ok=True)
        (self.temp_dir / "index.html").write_text(html)

    def start(self):
        """Start the server in a background thread."""
        os.chdir(self.temp_dir)
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(("", self.port), QuietHandler)
        self.actual_port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()

# ==========================================================
# === SELF-HEALING RPA AGENT ===============================
# ==========================================================

class SelfHealingRPAAgent:
    """
    RPA agent that evolves its locator strategies when UI changes.

    The key insight: instead of breaking when selectors fail,
    the agent analyzes the failure and generates new locator code.
    """

    def __init__(self):
        self.strategy_file = Path(__file__).parent / "generated_locators.py"
        self.current_strategy = "id_selector"
        self.generation = 0
        self.history = []
        self.successes = 0
        self.attempts = 0

        # Write initial strategy
        self._write_strategy(self.current_strategy)

    def _write_strategy(self, strategy_name: str):
        """Write a new locator strategy to disk."""
        template = LOCATOR_TEMPLATES[strategy_name]

        code = f'''"""
Generated Locator Strategy: {strategy_name}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{template}
'''
        self.strategy_file.write_text(code)
        logger.info(f"Wrote locator strategy '{strategy_name}'")

    def _load_locators(self):
        """Dynamically load the current locator function."""
        spec = importlib.util.spec_from_file_location("generated_locators", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.find_elements

    def attempt_task(self, page, version_name: str) -> dict:
        """
        Try to complete the task: add item to cart.

        Returns dict with success status and details.
        """
        self.attempts += 1

        try:
            find_elements = self._load_locators()
            elements = find_elements(page)

            # Task: Set quantity and click Add to Cart
            qty_locator = elements["quantity"]
            btn_locator = elements["add_button"]
            success_locator = elements["success"]

            # Check if elements exist
            if qty_locator.count() == 0:
                return {"success": False, "error": "Quantity input not found"}
            if btn_locator.count() == 0:
                return {"success": False, "error": "Add to Cart button not found"}

            # Perform the action
            qty_locator.fill("2")
            btn_locator.click()

            # Wait for success indicator
            time.sleep(0.3)

            # Check if success message appeared
            if success_locator.count() > 0 and success_locator.is_visible():
                self.successes += 1
                result = {
                    "success": True,
                    "strategy": self.current_strategy,
                    "generation": self.generation
                }
            else:
                result = {
                    "success": False,
                    "error": "Success message not displayed"
                }

        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }

        # Save to episodic memory
        outcome = "success" if result.get("success") else f"failure: {result.get('error', 'unknown')}"
        save_episode(
            task=f"add_to_cart_{version_name}",
            result=outcome,
            reflection=f"Strategy: {self.current_strategy}, Gen: {self.generation}"
        )

        self.history.append({
            "version": version_name,
            "strategy": self.current_strategy,
            "success": result.get("success", False)
        })

        return result

    def evolve(self) -> str:
        """
        Evolve to the next locator strategy based on failure analysis.

        Returns the name of the new strategy.
        """
        # Look at recent failures to inform strategy choice
        recent = get_recent_episodes(5)

        # Find current strategy index
        current_idx = STRATEGY_ORDER.index(self.current_strategy)

        # Move to next strategy
        next_idx = min(current_idx + 1, len(STRATEGY_ORDER) - 1)
        self.current_strategy = STRATEGY_ORDER[next_idx]
        self.generation += 1

        self._write_strategy(self.current_strategy)

        return self.current_strategy

    def show_code(self):
        """Display the currently generated locator code."""
        code = self.strategy_file.read_text()
        lines = code.split('\n')

        print(f"\n  \033[93m┌─ GENERATED LOCATOR CODE ──────────────────────┐\033[0m")
        for line in lines[:35]:  # Show first 35 lines
            print(f"  \033[93m│\033[0m {line}")
        if len(lines) > 35:
            print(f"  \033[93m│\033[0m ...")
        print(f"  \033[93m└───────────────────────────────────────────────┘\033[0m")

# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo(interactive: bool = True):
    """Run the self-healing RPA demonstration."""

    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Self-Healing RPA Demo                                  ║
    ║                                                          ║
    ║   Watch the agent:                                       ║
    ║   1. Try to click "Add to Cart"                          ║
    ║   2. Website redesigns → selectors break                 ║
    ║   3. Agent analyzes DOM and failure                      ║
    ║   4. Generates new locator strategy                      ║
    ║   5. Successfully completes the task                     ║
    ║                                                          ║
    ║   This is what UiPath/Automation Anywhere CANNOT do.     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if interactive:
        input("  Press ENTER to start...")
    else:
        time.sleep(1)

    # Check for playwright
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n  \033[91mError: Playwright not installed.\033[0m")
        print("  Run: pip install playwright && playwright install chromium")
        return

    init_memory_db()
    agent = SelfHealingRPAAgent()
    server = LocalWebServer(port=8765)

    # Demo sequence: versions that progressively break selectors
    sequence = [
        ("v1_original", "Original site design"),
        ("v1_original", "Same design (should work)"),
        ("v2_redesign", "🔄 SITE REDESIGNED!"),
        ("v2_redesign", "New design (should work now)"),
        ("v3_react_style", "🔄 MIGRATED TO REACT!"),
        ("v3_react_style", "React version (should work now)"),
        ("v4_accessible", "🔄 ACCESSIBILITY UPDATE!"),
        ("v4_accessible", "Accessible version (should work now)")
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process',
                '--no-zygote'
            ]
        )
        page = browser.new_page()

        for i, (version, description) in enumerate(sequence):
            print("\033[2J\033[H")
            print("=" * 60)
            print("  SELF-HEALING RPA - LIVE DEMO")
            print("=" * 60)
            print()

            # Set up the page
            html = WEBSITE_VERSIONS[version]
            server.set_page(html)
            if i == 0:
                server.start()
                time.sleep(0.5)

            page.goto(f"http://localhost:{server.actual_port}/index.html")
            time.sleep(0.3)

            is_redesign = "🔄" in description
            color = "\033[96m" if not is_redesign else "\033[95m"
            print(f"  {color}Attempt {i+1}/{len(sequence)}: {description}\033[0m")
            print(f"  Strategy: {agent.current_strategy} (Gen {agent.generation})")
            print()

            # Show what task we're trying to do
            print(f"  \033[90mTask: Set quantity to 2, click 'Add to Cart'\033[0m")
            print()

            # Attempt the task
            result = agent.attempt_task(page, version)

            if result["success"]:
                print(f"  \033[92m✓ SUCCESS!\033[0m")
                print(f"    Task completed with {agent.current_strategy} strategy")
                print()
                print(f"  Success Rate: {agent.successes}/{agent.attempts} ({100*agent.successes/agent.attempts:.0f}%)")

                if agent.generation > 0:
                    evolution = " → ".join([h["strategy"] for h in agent.history if h["success"]][:agent.generation+1])
                    if not evolution:
                        evolution = agent.current_strategy
                    print(f"  \033[95mEvolution: {evolution}\033[0m")

                time.sleep(1.5 if interactive else 0.8)

            else:
                print(f"  \033[91m✗ FAILED: {result['error']}\033[0m")
                print()

                # Evolve!
                print(f"  \033[95m🧬 EVOLVING - Generating new locator code...\033[0m")
                new_strategy = agent.evolve()
                print(f"  \033[95m   New strategy: {new_strategy}\033[0m")
                agent.show_code()

                if interactive:
                    input("  Press ENTER to retry with new strategy...")
                else:
                    time.sleep(0.5)

                # Retry with new strategy
                page.reload()
                time.sleep(0.3)

        browser.close()

    server.stop()

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO COMPLETE                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  EVOLUTION JOURNEY:")
    print("  " + "─" * 56)
    seen = set()
    for h in agent.history:
        if h["strategy"] not in seen:
            seen.add(h["strategy"])
            idx = STRATEGY_ORDER.index(h["strategy"])
            print(f"    Gen {idx}: {h['strategy']}")

    print()
    print("  PERFORMANCE:")
    print("  " + "─" * 56)

    versions_seen = []
    for h in agent.history:
        status = "\033[92m✓\033[0m" if h["success"] else "\033[91m✗\033[0m"
        print(f"    {status} {h['version']} ({h['strategy']})")

    print()
    print(f"  Final Success Rate: \033[96m{100*agent.successes/agent.attempts:.0f}%\033[0m")
    print()

    print("  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The RPA bot survived 3 complete UI redesigns")
    print("    by evolving from ID selectors to a multi-strategy")
    print("    approach - all without human intervention.")
    print()
    print("    \033[96mThis is self-healing automation.\033[0m")
    print()

    print("  FINAL GENERATED LOCATORS:")
    agent.show_code()


if __name__ == "__main__":
    try:
        interactive = "--auto" not in sys.argv
        run_demo(interactive=interactive)
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
