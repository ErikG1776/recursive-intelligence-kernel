#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - Production Self-Healing RPA

Real browser automation that heals itself when UI changes:
1. Attempts action with learned/preferred locator
2. If it fails, tries alternative strategies
3. When successful, records what worked
4. Builds persistent memory of reliable selectors

Usage:
    # Click a button on a real website
    python rpa_engine.py click --url "https://example.com" --target "Submit"

    # Fill a form field
    python rpa_engine.py fill --url "https://example.com" --target "Email" --value "test@example.com"

    # Run a workflow
    python rpa_engine.py workflow --config workflow.json
"""

import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import init_memory_db, save_episode, get_recent_episodes

# Playwright import with graceful fallback
try:
    from playwright.sync_api import sync_playwright, Page, Locator, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Run: pip install playwright && playwright install chromium")


class LocatorStrategy:
    """A strategy for finding elements on a page."""

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.success_count = 0
        self.failure_count = 0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5  # Unknown
        return self.success_count / total

    def record_success(self):
        self.success_count += 1

    def record_failure(self):
        self.failure_count += 1


class SelfHealingLocator:
    """Locator that tries multiple strategies and learns which work."""

    STRATEGIES = [
        "css_id",        # ID attribute (most reliable)
        "label",         # Form label association
        "placeholder",   # Placeholder text
        "text",          # Visible text content
        "role",          # ARIA role + name
        "test_id",       # data-testid attribute
        "css_combo",     # Combined attributes
        "xpath_text",    # XPath with text
        "css_class",     # Class-based selector
    ]

    def __init__(self, target: str, action: str):
        self.target = target  # What we're looking for (e.g., "Submit", "Email")
        self.action = action  # What we want to do (e.g., "click", "fill")
        self.strategies = {name: LocatorStrategy(name, i) for i, name in enumerate(self.STRATEGIES)}
        self.last_successful_strategy = None
        self.learned_selector = None

    def get_locator(self, page: Page, strategy_name: str) -> Optional[Locator]:
        """Get a Playwright locator for the given strategy."""
        target = self.target

        try:
            if strategy_name == "test_id":
                return page.get_by_test_id(target)

            elif strategy_name == "role":
                # Try common roles
                for role in ["button", "link", "textbox", "checkbox", "menuitem"]:
                    loc = page.get_by_role(role, name=target)
                    if loc.count() > 0:
                        return loc
                return None

            elif strategy_name == "text":
                return page.get_by_text(target, exact=False)

            elif strategy_name == "label":
                return page.get_by_label(target)

            elif strategy_name == "placeholder":
                return page.get_by_placeholder(target)

            elif strategy_name == "css_id":
                # Try variations of ID
                variations = [
                    target,
                    target.lower(),
                    target.replace(" ", "-"),
                    target.replace(" ", "_"),
                    target.lower().replace(" ", "-"),
                    target.lower().replace(" ", "_"),
                ]
                for variation in variations:
                    loc = page.locator(f"#{variation}")
                    if loc.count() > 0:
                        return loc
                # Also try partial match
                loc = page.locator(f"[id*='{target.lower()}']")
                if loc.count() > 0:
                    return loc
                return None

            elif strategy_name == "css_class":
                # Try class-based selectors
                for variation in [target.lower(), target.replace(" ", "-"), target.replace(" ", "_")]:
                    loc = page.locator(f".{variation}")
                    if loc.count() > 0:
                        return loc
                return None

            elif strategy_name == "xpath_text":
                return page.locator(f"//*[contains(text(), '{target}')]")

            elif strategy_name == "css_combo":
                # Try attribute combinations
                selectors = [
                    f"[name='{target}']",
                    f"[name='{target.lower()}']",
                    f"[value='{target}']",
                    f"[title='{target}']",
                    f"[aria-label='{target}']",
                ]
                for sel in selectors:
                    loc = page.locator(sel)
                    if loc.count() > 0:
                        return loc
                return None

            else:
                return None

        except Exception:
            return None

    def find_element(self, page: Page, timeout: int = 5000) -> Optional[Locator]:
        """Find element using self-healing strategy selection."""

        # Sort strategies by success rate (learned preference)
        sorted_strategies = sorted(
            self.strategies.values(),
            key=lambda s: (s.success_rate, -s.priority),
            reverse=True
        )

        # Try each strategy with short timeout
        per_strategy_timeout = max(500, timeout // len(sorted_strategies))

        for strategy in sorted_strategies:
            loc = self.get_locator(page, strategy.name)

            if loc is None:
                strategy.record_failure()
                continue

            try:
                # Check if element exists
                count = loc.count()
                if count > 0:
                    # Success! Record it
                    strategy.record_success()
                    self.last_successful_strategy = strategy.name
                    return loc.first
                else:
                    strategy.record_failure()

            except Exception as e:
                strategy.record_failure()

        return None


class RPAEngine:
    """Self-healing RPA engine powered by Recursive Intelligence."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.locators: Dict[str, SelfHealingLocator] = {}
        self.action_history = []

        # Setup logging
        self.logger = logging.getLogger("ria.rpa")

    def start(self):
        """Start the browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        self.page = self.context.new_page()
        self.logger.info("Browser started")

    def stop(self):
        """Stop the browser."""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        self.logger.info("Browser stopped")

    def navigate(self, url: str):
        """Navigate to a URL."""
        self.page.goto(url, wait_until="domcontentloaded")
        self.logger.info(f"Navigated to {url}")

        self.action_history.append({
            "action": "navigate",
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def _get_locator(self, target: str, action: str) -> SelfHealingLocator:
        """Get or create a self-healing locator."""
        key = f"{action}:{target}"
        if key not in self.locators:
            self.locators[key] = SelfHealingLocator(target, action)
        return self.locators[key]

    def click(self, target: str, timeout: int = 10000) -> bool:
        """Click an element with self-healing."""
        locator = self._get_locator(target, "click")
        element = locator.find_element(self.page, timeout)

        if element:
            try:
                element.click(timeout=timeout)

                self.action_history.append({
                    "action": "click",
                    "target": target,
                    "strategy": locator.last_successful_strategy,
                    "success": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

                self.logger.info(f"Clicked '{target}' using {locator.last_successful_strategy}")
                return True

            except Exception as e:
                self.logger.error(f"Click failed: {e}")

        self.action_history.append({
            "action": "click",
            "target": target,
            "success": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        self.logger.warning(f"Could not find element to click: {target}")
        return False

    def fill(self, target: str, value: str, timeout: int = 10000) -> bool:
        """Fill an input with self-healing."""
        locator = self._get_locator(target, "fill")
        element = locator.find_element(self.page, timeout)

        if element:
            try:
                element.fill(value, timeout=timeout)

                self.action_history.append({
                    "action": "fill",
                    "target": target,
                    "value": value[:20] + "..." if len(value) > 20 else value,
                    "strategy": locator.last_successful_strategy,
                    "success": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

                self.logger.info(f"Filled '{target}' using {locator.last_successful_strategy}")
                return True

            except Exception as e:
                self.logger.error(f"Fill failed: {e}")

        self.action_history.append({
            "action": "fill",
            "target": target,
            "success": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        self.logger.warning(f"Could not find element to fill: {target}")
        return False

    def get_text(self, target: str, timeout: int = 10000) -> Optional[str]:
        """Get text content with self-healing."""
        locator = self._get_locator(target, "text")
        element = locator.find_element(self.page, timeout)

        if element:
            try:
                text = element.text_content()
                self.logger.info(f"Got text from '{target}'")
                return text
            except Exception as e:
                self.logger.error(f"Get text failed: {e}")

        return None

    def wait_for(self, target: str, timeout: int = 30000) -> bool:
        """Wait for an element to appear."""
        locator = self._get_locator(target, "wait")
        element = locator.find_element(self.page, timeout)
        return element is not None

    def screenshot(self, path: str):
        """Take a screenshot."""
        self.page.screenshot(path=path)
        self.logger.info(f"Screenshot saved to {path}")

    def save_learning(self):
        """Save learned strategies to RIA memory."""
        for key, locator in self.locators.items():
            action, target = key.split(":", 1)

            # Get best strategies
            sorted_strategies = sorted(
                locator.strategies.values(),
                key=lambda s: s.success_rate,
                reverse=True
            )

            best = sorted_strategies[0] if sorted_strategies else None

            if best and best.success_count > 0:
                save_episode(
                    task=f"rpa_{action}_{target}",
                    result="learned",
                    reflection=f"Best strategy: {best.name} ({best.success_rate*100:.0f}% success)"
                )

    def get_stats(self) -> Dict:
        """Get statistics about actions and strategies."""
        total_actions = len(self.action_history)
        successful = sum(1 for a in self.action_history if a.get("success", False))

        strategy_stats = {}
        for key, locator in self.locators.items():
            for name, strategy in locator.strategies.items():
                if strategy.success_count + strategy.failure_count > 0:
                    if name not in strategy_stats:
                        strategy_stats[name] = {"success": 0, "failure": 0}
                    strategy_stats[name]["success"] += strategy.success_count
                    strategy_stats[name]["failure"] += strategy.failure_count

        return {
            "total_actions": total_actions,
            "successful_actions": successful,
            "success_rate": successful / total_actions if total_actions > 0 else 0,
            "strategy_stats": strategy_stats
        }


def run_workflow(config_path: str, headless: bool = True):
    """Run a workflow from a JSON config file."""
    with open(config_path) as f:
        workflow = json.load(f)

    engine = RPAEngine(headless=headless)

    try:
        engine.start()

        for step in workflow.get("steps", []):
            action = step.get("action")

            if action == "navigate":
                engine.navigate(step["url"])
            elif action == "click":
                engine.click(step["target"])
            elif action == "fill":
                engine.fill(step["target"], step["value"])
            elif action == "wait":
                engine.wait_for(step["target"], step.get("timeout", 30000))
            elif action == "screenshot":
                engine.screenshot(step["path"])

            # Optional delay between steps
            if "delay" in step:
                time.sleep(step["delay"] / 1000)

        # Save what we learned
        engine.save_learning()

        # Print stats
        stats = engine.get_stats()
        print(f"\nWorkflow complete: {stats['successful_actions']}/{stats['total_actions']} actions succeeded")

    finally:
        engine.stop()


def main():
    parser = argparse.ArgumentParser(description="Self-Healing RPA Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Click command
    click_parser = subparsers.add_parser("click", help="Click an element")
    click_parser.add_argument("--url", required=True, help="URL to navigate to")
    click_parser.add_argument("--target", required=True, help="Element to click")
    click_parser.add_argument("--headless", action="store_true", help="Run headless")

    # Fill command
    fill_parser = subparsers.add_parser("fill", help="Fill an input")
    fill_parser.add_argument("--url", required=True, help="URL to navigate to")
    fill_parser.add_argument("--target", required=True, help="Input to fill")
    fill_parser.add_argument("--value", required=True, help="Value to enter")
    fill_parser.add_argument("--headless", action="store_true", help="Run headless")

    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run a workflow")
    workflow_parser.add_argument("--config", required=True, help="Workflow JSON file")
    workflow_parser.add_argument("--headless", action="store_true", help="Run headless")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo on example site")
    demo_parser.add_argument("--headless", action="store_true", default=True, help="Run headless")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Initialize memory
    init_memory_db()

    if args.command == "click":
        engine = RPAEngine(headless=args.headless)
        try:
            engine.start()
            engine.navigate(args.url)
            success = engine.click(args.target)
            engine.save_learning()
            stats = engine.get_stats()
            print(f"\nClick {'succeeded' if success else 'failed'}")
            print(f"Strategy used: {engine.locators.get(f'click:{args.target}', {}).last_successful_strategy}")
        finally:
            engine.stop()

    elif args.command == "fill":
        engine = RPAEngine(headless=args.headless)
        try:
            engine.start()
            engine.navigate(args.url)
            success = engine.fill(args.target, args.value)
            engine.save_learning()
            print(f"\nFill {'succeeded' if success else 'failed'}")
        finally:
            engine.stop()

    elif args.command == "workflow":
        run_workflow(args.config, headless=args.headless)

    elif args.command == "demo":
        print("\n" + "="*60)
        print("  SELF-HEALING RPA DEMO")
        print("="*60 + "\n")

        engine = RPAEngine(headless=args.headless)
        try:
            engine.start()

            # Demo on local test file
            test_file = Path(__file__).parent / "test_login.html"
            print(f"Testing on local file: {test_file}\n")

            engine.navigate(f"file://{test_file}")
            time.sleep(1)

            # Fill username
            print("Filling username...")
            engine.fill("Username", "tomsmith")
            time.sleep(0.5)

            # Fill password
            print("Filling password...")
            engine.fill("Password", "SuperSecretPassword!")
            time.sleep(0.5)

            # Click login
            print("Clicking login...")
            engine.click("Login")
            time.sleep(1)

            # Check for success message
            if engine.wait_for("Login successful", timeout=5000):
                print("\n✓ Login successful!")
            else:
                print("\n✗ Login may have failed")

            # Save learning
            engine.save_learning()

            # Print stats
            stats = engine.get_stats()
            print(f"\nResults: {stats['successful_actions']}/{stats['total_actions']} actions succeeded")
            print(f"Success rate: {stats['success_rate']*100:.0f}%")

            if stats['strategy_stats']:
                print("\nStrategy effectiveness:")
                for name, data in stats['strategy_stats'].items():
                    total = data['success'] + data['failure']
                    rate = data['success'] / total if total > 0 else 0
                    print(f"  {name}: {rate*100:.0f}% ({data['success']}/{total})")

        finally:
            engine.stop()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
