#!/usr/bin/env python3
"""
adaptive_scraper.py | Recursive Intelligence Algorithm Demo
------------------------------------------------------------
Self-modifying web scraper that adapts when websites change.

This demo shows:
1. Agent tries to scrape product data
2. Website "redesigns" (HTML structure changes)
3. Selectors break → Agent fails
4. Agent analyzes failure → generates new selector code
5. Successfully scrapes the changed site

Real-world application: Price monitoring, data collection, etc.

Run: python demos/adaptive_scraper.py
"""

import os
import sys
import time
import random
import importlib.util
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import setup_logging
from memory import save_episode, get_recent_episodes, init_memory_db

logger = setup_logging("ria.scraper_demo")


# ==========================================================
# === SIMULATED WEBSITE VERSIONS ===========================
# ==========================================================

WEBSITE_VERSIONS = {
    "v1_simple": '''
    <html>
    <body>
        <div class="product">
            <h1 class="title">Wireless Headphones</h1>
            <span class="price">$79.99</span>
            <p class="stock">In Stock</p>
        </div>
    </body>
    </html>
    ''',

    "v2_redesign": '''
    <html>
    <body>
        <article data-product="true">
            <div class="product-header">
                <h2 class="product-name">Wireless Headphones</h2>
            </div>
            <div class="product-info">
                <span data-price="79.99">$79.99</span>
                <div class="availability in-stock">Available</div>
            </div>
        </article>
    </body>
    </html>
    ''',

    "v3_spa_style": '''
    <html>
    <body>
        <div id="app">
            <section class="pdp-container">
                <div class="pdp-title" data-testid="product-title">Wireless Headphones</div>
                <div class="pdp-price-wrapper">
                    <span class="pdp-price" data-testid="price">$79.99</span>
                </div>
                <span class="pdp-stock" data-testid="stock-status">In Stock</span>
            </section>
        </div>
    </body>
    </html>
    ''',

    "v4_minimal": '''
    <html>
    <body>
        <main>
            <h1>Wireless Headphones</h1>
            <p><strong>Price:</strong> $79.99</p>
            <p><em>Status: In Stock</em></p>
        </main>
    </body>
    </html>
    '''
}


# ==========================================================
# === SCRAPER STRATEGIES ===================================
# ==========================================================

SCRAPER_TEMPLATES = {
    "basic_classes": '''
def scrape(html):
    """Basic class-based selectors."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = soup.select_one('.title, .product-title, h1').text.strip()
        price = soup.select_one('.price').text.strip()
        stock = soup.select_one('.stock').text.strip()
        return {"title": title, "price": price, "stock": stock, "success": True}
    except:
        return {"success": False, "error": "Selectors not found"}
''',

    "data_attributes": '''
def scrape(html):
    """Use data attributes for more stable selection."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # Try data attributes first, then fall back
        title_el = soup.select_one('[data-testid="product-title"], .product-name, h1, h2')
        price_el = soup.select_one('[data-price], [data-testid="price"], .price, .pdp-price')
        stock_el = soup.select_one('[data-testid="stock-status"], .availability, .stock')

        title = title_el.text.strip() if title_el else "Not found"
        price = price_el.text.strip() if price_el else "Not found"
        stock = stock_el.text.strip() if stock_el else "Not found"

        if "Not found" in [title, price, stock]:
            return {"success": False, "error": "Some fields not found"}
        return {"title": title, "price": price, "stock": stock, "success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
''',

    "semantic_search": '''
def scrape(html):
    """Semantic search - find by content patterns, not structure."""
    from bs4 import BeautifulSoup
    import re
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find price by pattern ($XX.XX)
        price_pattern = re.compile(r'\\$\\d+\\.\\d{2}')
        price_el = soup.find(string=price_pattern)
        price = price_el.strip() if price_el else None

        # Find title - usually the first h1/h2 or largest text
        title_el = soup.select_one('h1, h2, [class*="title"], [class*="name"]')
        title = title_el.text.strip() if title_el else None

        # Find stock - look for keywords
        stock_keywords = ['stock', 'available', 'availability']
        stock = None
        for el in soup.find_all(['span', 'div', 'p', 'em']):
            text = el.text.lower()
            if any(kw in text for kw in stock_keywords):
                stock = el.text.strip()
                break

        if not all([title, price, stock]):
            return {"success": False, "error": f"Missing: title={title}, price={price}, stock={stock}"}
        return {"title": title, "price": price, "stock": stock, "success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
''',

    "universal_extractor": '''
def scrape(html):
    """Universal extractor - combines all strategies with fallbacks."""
    from bs4 import BeautifulSoup
    import re
    soup = BeautifulSoup(html, 'html.parser')

    def find_title():
        # Priority order of selectors
        selectors = [
            '[data-testid="product-title"]',
            '.product-name', '.pdp-title', '.title',
            'h1', 'h2'
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el and len(el.text.strip()) > 0:
                return el.text.strip()
        return None

    def find_price():
        # First try data attributes
        el = soup.select_one('[data-price]')
        if el:
            return el.get('data-price', el.text.strip())

        # Then try pattern matching
        pattern = re.compile(r'\\$\\d+\\.\\d{2}')
        for el in soup.find_all(['span', 'p', 'div', 'strong']):
            if pattern.search(el.text):
                match = pattern.search(el.text)
                return match.group() if match else el.text.strip()
        return None

    def find_stock():
        # Check multiple patterns
        patterns = [
            ('in.stock', True), ('available', True),
            ('out.of.stock', False), ('unavailable', False)
        ]

        for el in soup.find_all(['span', 'div', 'p', 'em']):
            text = el.text.lower()
            for pattern, _ in patterns:
                if re.search(pattern, text):
                    return el.text.strip()
        return None

    try:
        title = find_title()
        price = find_price()
        stock = find_stock()

        if all([title, price, stock]):
            return {"title": title, "price": price, "stock": stock, "success": True}
        return {"success": False, "error": f"Missing fields"}
    except Exception as e:
        return {"success": False, "error": str(e)}
'''
}


# ==========================================================
# === ADAPTIVE SCRAPER AGENT ===============================
# ==========================================================

class AdaptiveScraperAgent:
    """Self-modifying web scraper that evolves its selectors."""

    def __init__(self):
        self.strategy_file = os.path.join(
            os.path.dirname(__file__),
            "generated_scraper.py"
        )
        self.current_strategy = "basic_classes"
        self.generation = 0
        self.successes = 0
        self.attempts = 0
        self.evolution_log = []

        self._write_strategy(SCRAPER_TEMPLATES["basic_classes"], "basic_classes")

    def _write_strategy(self, code: str, name: str):
        """Write scraper code to file."""
        full_code = f'''"""
Generated Scraper Strategy: {name}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{code}
'''
        with open(self.strategy_file, 'w') as f:
            f.write(full_code)
        self.current_strategy = name
        logger.info(f"Wrote strategy '{name}'")

    def _load_strategy(self):
        """Load current strategy."""
        spec = importlib.util.spec_from_file_location("scraper", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.scrape

    def scrape(self, html: str, site_version: str) -> dict:
        """Attempt to scrape HTML."""
        self.attempts += 1

        try:
            scrape_func = self._load_strategy()
            result = scrape_func(html)
            result["site_version"] = site_version
            result["strategy"] = self.current_strategy
            result["generation"] = self.generation

            if result.get("success"):
                self.successes += 1

            # Save to memory
            save_episode(
                task=f"Scrape {site_version}",
                result="success" if result.get("success") else "failure",
                reflection=self._reflect(result)
            )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _reflect(self, result: dict) -> str:
        """Generate reflection on scrape attempt."""
        if result.get("success"):
            return (f"Strategy '{result['strategy']}' successfully scraped {result['site_version']}. "
                   f"Found: {result.get('title', 'N/A')}")
        else:
            return (f"Strategy '{result['strategy']}' FAILED on {result['site_version']}. "
                   f"Error: {result.get('error', 'Unknown')}. Need more robust selectors.")

    def evolve(self) -> str:
        """Evolve to a more robust scraping strategy."""
        self.generation += 1

        # Get recent failures
        episodes = get_recent_episodes(limit=10)
        failures = [e for e in episodes if e.get("result") == "failure"]

        # Evolution logic
        progression = ["basic_classes", "data_attributes", "semantic_search", "universal_extractor"]

        try:
            idx = progression.index(self.current_strategy)
            new_strategy = progression[min(idx + 1, len(progression) - 1)]
        except ValueError:
            new_strategy = "universal_extractor"

        self.evolution_log.append({
            "generation": self.generation,
            "from": self.current_strategy,
            "to": new_strategy,
            "reason": f"Failed on {len(failures)} recent attempts"
        })

        self._write_strategy(SCRAPER_TEMPLATES[new_strategy], new_strategy)
        return new_strategy

    def show_code(self):
        """Display current scraper code."""
        print("\n  \033[93m┌─ GENERATED SCRAPER CODE ─────────────────────┐\033[0m")
        with open(self.strategy_file, 'r') as f:
            for i, line in enumerate(f.readlines()):
                if i < 30:
                    print(f"  \033[93m│\033[0m {line.rstrip()}")
        print("  \033[93m└──────────────────────────────────────────────┘\033[0m\n")


# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo():
    print("\033[2J\033[H")

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Adaptive Web Scraper Demo                              ║
    ║                                                          ║
    ║   Watch the agent:                                       ║
    ║   1. Try to scrape product data                          ║
    ║   2. Website "redesigns" → selectors break               ║
    ║   3. Agent analyzes failure                              ║
    ║   4. Generates new scraper code                          ║
    ║   5. Successfully scrapes the changed site               ║
    ║                                                          ║
    ║   Real-world use: Price monitoring that survives         ║
    ║   website updates without manual intervention.           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    input("  Press ENTER to start...")

    init_memory_db()
    agent = AdaptiveScraperAgent()

    # Simulate website versions over time
    versions = [
        ("v1_simple", "Original site design"),
        ("v1_simple", "Same design (should work)"),
        ("v2_redesign", "🔄 SITE REDESIGNED!"),
        ("v2_redesign", "New design (should work now)"),
        ("v3_spa_style", "🔄 MIGRATED TO SPA!"),
        ("v3_spa_style", "SPA version (should work now)"),
        ("v4_minimal", "🔄 MINIMALIST REDESIGN!"),
        ("v4_minimal", "Minimal version (should work now)"),
    ]

    results = []

    for i, (version, description) in enumerate(versions):
        print("\033[2J\033[H")
        print("=" * 60)
        print("  ADAPTIVE WEB SCRAPER - LIVE DEMO")
        print("=" * 60)
        print()

        print(f"  \033[96mAttempt {i+1}/8: {description}\033[0m")
        print(f"  Strategy: {agent.current_strategy} (Gen {agent.generation})")
        print()

        # Show HTML snippet
        html = WEBSITE_VERSIONS[version]
        print("  \033[90m┌─ Website HTML (snippet) ─────────────────────┐\033[0m")
        for line in html.strip().split('\n')[:10]:
            print(f"  \033[90m│\033[0m {line}")
        print("  \033[90m└──────────────────────────────────────────────┘\033[0m")
        print()

        # Scrape
        result = agent.scrape(html, version)
        results.append(result)

        if result.get("success"):
            print(f"  \033[92m✓ SUCCESS!\033[0m")
            print(f"    Title: {result.get('title')}")
            print(f"    Price: {result.get('price')}")
            print(f"    Stock: {result.get('stock')}")
        else:
            print(f"  \033[91m✗ FAILED: {result.get('error')}\033[0m")

            # Evolve
            print("\n  \033[95m🧬 EVOLVING - Generating new scraper code...\033[0m")
            time.sleep(1)

            new_strategy = agent.evolve()
            print(f"  \033[95m   New strategy: {new_strategy}\033[0m")
            agent.show_code()

            input("  Press ENTER to test new strategy...")
            continue

        print()
        print(f"  Success Rate: {agent.successes}/{agent.attempts} ({100*agent.successes/agent.attempts:.0f}%)")

        if agent.evolution_log:
            evolutions = " → ".join([agent.evolution_log[0]["from"]] +
                                    [e["to"] for e in agent.evolution_log])
            print(f"  \033[95mEvolution: {evolutions}\033[0m")

        time.sleep(1.5)

    # Summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO COMPLETE                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  EVOLUTION JOURNEY:")
    print("  " + "─" * 56)
    if agent.evolution_log:
        print(f"    Gen 0: {agent.evolution_log[0]['from']}")
        for evo in agent.evolution_log:
            print(f"    Gen {evo['generation']}: {evo['to']}")

    print("\n  PERFORMANCE:")
    print("  " + "─" * 56)
    for i, r in enumerate(results):
        status = "\033[92m✓\033[0m" if r.get("success") else "\033[91m✗\033[0m"
        print(f"    Attempt {i+1}: {status} {r.get('site_version')} ({r.get('strategy')})")

    print(f"\n  Final Success Rate: \033[96m{100*agent.successes/agent.attempts:.0f}%\033[0m")

    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The scraper survived 3 complete website redesigns")
    print("    by evolving from basic class selectors to a universal")
    print("    pattern-matching extractor - all without human intervention.")
    print()
    print("    \033[96mSame code pattern as the maze: Fail → Reflect → Evolve\033[0m")
    print()

    print("  FINAL GENERATED SCRAPER:")
    agent.show_code()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
