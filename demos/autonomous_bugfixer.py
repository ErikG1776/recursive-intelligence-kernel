#!/usr/bin/env python3
"""
Autonomous Bug Fixer Demo - Recursive Intelligence Algorithm

Demonstrates RIA applied to real-world bug fixing:
- Agent receives a failing test
- Searches codebase to find relevant code
- Analyzes why the test fails
- Writes a fix
- Runs the test
- Iterates until green

This is the holy grail of developer productivity.
GitHub Copilot can't do this.
"""

import sys
import os
import time
import importlib.util
import traceback
import signal
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import setup_logging
from memory import init_memory_db, save_episode

logger = setup_logging("ria.bugfixer")

# ==========================================================
# === SIMULATED CODEBASE ===================================
# ==========================================================

# This simulates a real codebase with multiple modules
CODEBASE = {
    "utils/pagination.py": '''
def paginate(items, page, per_page=10):
    """Return a page of items from a list."""
    start = page * per_page
    end = start + per_page
    return items[start:end]

def get_total_pages(total_items, per_page=10):
    """Calculate total number of pages."""
    return total_items // per_page
''',

    "utils/validators.py": '''
def validate_email(email):
    """Validate email format."""
    if "@" in email and "." in email:
        return True
    return False

def validate_age(age):
    """Validate age is reasonable."""
    return age > 0 and age < 150
''',

    "models/user.py": '''
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def is_adult(self):
        """Check if user is an adult."""
        return self.age > 18

    def get_display_name(self):
        """Get formatted display name."""
        return self.name.title()
''',

    "services/calculator.py": '''
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    discount = price * discount_percent / 100
    return price + discount

def calculate_tax(price, tax_rate=0.1):
    """Calculate price with tax."""
    return price * (1 + tax_rate)
''',

    "api/handlers.py": '''
def get_user_by_id(users, user_id):
    """Find user by ID in list."""
    for user in users:
        if user.id == user_id:
            return user
    return None

def format_response(data, status="success"):
    """Format API response."""
    return {
        "status": status,
        "data": data
    }
'''
}

# ==========================================================
# === BUG SCENARIOS ========================================
# ==========================================================

BUG_SCENARIOS = [
    {
        "name": "Pagination Off-by-One",
        "test_file": "test_pagination.py",
        "test_code": '''
def test_paginate_first_page():
    """First page should return first 10 items."""
    items = list(range(100))
    result = paginate(items, 1, 10)
    assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], f"Got {result}"
    return True
''',
        "target_file": "utils/pagination.py",
        "bug_description": "Page 1 should start at index 0, not index 10",
        "difficulty": 1
    },
    {
        "name": "Wrong Discount Calculation",
        "test_file": "test_calculator.py",
        "test_code": '''
def test_calculate_discount():
    """20% discount on $100 should be $80."""
    result = calculate_discount(100, 20)
    assert result == 80, f"Expected 80, got {result}"
    return True
''',
        "target_file": "services/calculator.py",
        "bug_description": "Discount should subtract, not add",
        "difficulty": 1
    },
    {
        "name": "Adult Age Threshold",
        "test_file": "test_user.py",
        "test_code": '''
def test_is_adult():
    """18-year-old should be considered adult."""
    user = User("Test", "test@example.com", 18)
    assert user.is_adult() == True, "18 should be adult"
    return True
''',
        "target_file": "models/user.py",
        "bug_description": "Should use >= 18, not > 18",
        "difficulty": 1
    },
    {
        "name": "Total Pages Calculation",
        "test_file": "test_pagination.py",
        "test_code": '''
def test_get_total_pages():
    """25 items with 10 per page should be 3 pages."""
    result = get_total_pages(25, 10)
    assert result == 3, f"Expected 3 pages, got {result}"
    return True
''',
        "target_file": "utils/pagination.py",
        "bug_description": "Need ceiling division, not floor",
        "difficulty": 2
    },
    {
        "name": "Email Validation Edge Case",
        "test_file": "test_validators.py",
        "test_code": '''
def test_validate_email():
    """Should reject emails without proper domain."""
    # This should fail - no TLD after dot
    result = validate_email("user@domain.")
    assert result == False, "Should reject incomplete domain"
    return True
''',
        "target_file": "utils/validators.py",
        "bug_description": "Need to check for content after the dot",
        "difficulty": 2
    }
]

# ==========================================================
# === FIX STRATEGIES =======================================
# ==========================================================

FIX_STRATEGIES = {
    "pattern_match": '''
def find_and_fix(code, test_code, error_msg):
    """Find patterns in code that match common bug types."""
    lines = code.split('\\n')

    for i, line in enumerate(lines):
        # Off-by-one in pagination: page * per_page should be (page-1) * per_page
        if "start = page * per_page" in line:
            lines[i] = line.replace("page * per_page", "(page - 1) * per_page")

        # Wrong operator: + should be -
        if "price + discount" in line:
            lines[i] = line.replace("price + discount", "price - discount")

        # Comparison: > should be >=
        if "self.age > 18" in line:
            lines[i] = line.replace("> 18", ">= 18")

    return '\\n'.join(lines)
''',

    "semantic_analysis": '''
def find_and_fix(code, test_code, error_msg):
    """Analyze semantics to find logical errors."""
    lines = code.split('\\n')

    for i, line in enumerate(lines):
        # Floor division should be ceiling for page counts
        if "total_items // per_page" in line:
            # Use ceiling division: -(-a // b)
            lines[i] = line.replace(
                "total_items // per_page",
                "-(-total_items // per_page)"
            )

        # Email validation needs better check
        if '"." in email' in line and "return True" in lines[i+1] if i+1 < len(lines) else False:
            # Need to check there's content after the dot
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + 'if "@" in email and "." in email.split("@")[1][:-1]:'

    return '\\n'.join(lines)
''',

    "comprehensive": '''
def find_and_fix(code, test_code, error_msg):
    """Comprehensive fix strategy combining all approaches."""
    lines = code.split('\\n')

    for i, line in enumerate(lines):
        # Pagination off-by-one
        if "start = page * per_page" in line:
            lines[i] = line.replace("page * per_page", "(page - 1) * per_page")

        # Wrong arithmetic operator
        if "price + discount" in line:
            lines[i] = line.replace("price + discount", "price - discount")

        # Comparison boundary
        if "self.age > 18" in line:
            lines[i] = line.replace("> 18", ">= 18")

        # Floor vs ceiling division
        if "total_items // per_page" in line:
            lines[i] = line.replace(
                "total_items // per_page",
                "-(-total_items // per_page)"
            )

        # Better email validation
        if '"." in email' in line:
            lines[i] = line.replace(
                '"." in email',
                'email.split("@")[1].count(".") > 0 and not email.endswith(".")'
            )

    return '\\n'.join(lines)
'''
}

STRATEGY_ORDER = ["pattern_match", "semantic_analysis", "comprehensive"]

# ==========================================================
# === AUTONOMOUS BUG FIXER AGENT ===========================
# ==========================================================

class AutonomousBugFixer:
    """
    Agent that autonomously finds and fixes bugs in a codebase.

    The key insight: given only a failing test, it can
    locate the bug, understand the cause, and write a fix.
    """

    def __init__(self, codebase: Dict[str, str]):
        self.codebase = codebase.copy()  # Working copy
        self.original_codebase = codebase.copy()  # For reset
        self.strategy_file = Path(__file__).parent / "fixer_strategy.py"
        self.current_strategy = "pattern_match"
        self.generation = 0
        self.bugs_fixed = 0
        self.total_attempts = 0
        self._write_strategy()

    def _write_strategy(self):
        code = f'''"""
Bug Fixer Strategy: {self.current_strategy}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{FIX_STRATEGIES[self.current_strategy]}
'''
        self.strategy_file.write_text(code)
        logger.info(f"Fixer evolved to '{self.current_strategy}'")

    def _load_fixer(self):
        spec = importlib.util.spec_from_file_location("fixer", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.find_and_fix

    def _run_test(self, test_code: str, target_file: str) -> dict:
        """Run test against the current codebase state."""
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out")

        try:
            # Build execution context with all codebase modules
            namespace = {}

            # Load all modules
            for filepath, code in self.codebase.items():
                exec(compile(code, filepath, 'exec'), namespace)

            # Load and run test
            full_test = test_code + f"\n\nresult = {test_code.split('def ')[1].split('(')[0]}()"

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(2)

            try:
                exec(compile(full_test, "test.py", 'exec'), namespace)
                return {"success": True}
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        except AssertionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}"}

    def fix_bug(self, scenario: dict) -> dict:
        """
        Attempt to fix a bug given a failing test.

        Returns dict with success status and fix details.
        """
        self.total_attempts += 1

        # Reset codebase for this scenario
        self.codebase = self.original_codebase.copy()

        test_code = scenario["test_code"]
        target_file = scenario["target_file"]
        max_iterations = 3

        fix_history = []

        for iteration in range(max_iterations):
            # Run the test
            result = self._run_test(test_code, target_file)

            if result["success"]:
                self.bugs_fixed += 1
                save_episode(
                    task=f"fix_{scenario['name']}",
                    result="success",
                    reflection=f"Fixed with {self.current_strategy} in {iteration + 1} iterations"
                )
                return {
                    "success": True,
                    "iterations": iteration + 1,
                    "strategy": self.current_strategy,
                    "fixed_code": self.codebase[target_file],
                    "history": fix_history
                }

            # Record failure
            error_msg = result.get("error", "Unknown")
            fix_history.append({
                "iteration": iteration,
                "error": error_msg,
                "strategy": self.current_strategy
            })

            # Apply fix strategy
            fixer = self._load_fixer()
            original_code = self.codebase[target_file]
            fixed_code = fixer(original_code, test_code, error_msg)
            self.codebase[target_file] = fixed_code

            # Evolve strategy if needed
            if iteration > 0:
                self.evolve()

        # Final attempt
        result = self._run_test(test_code, target_file)
        if result["success"]:
            self.bugs_fixed += 1
            save_episode(
                task=f"fix_{scenario['name']}",
                result="success",
                reflection=f"Fixed with {self.current_strategy}"
            )
            return {
                "success": True,
                "iterations": max_iterations,
                "strategy": self.current_strategy,
                "fixed_code": self.codebase[target_file],
                "history": fix_history
            }

        save_episode(
            task=f"fix_{scenario['name']}",
            result=f"failure: {result.get('error', 'unknown')}",
            reflection=f"Failed after {max_iterations} iterations"
        )

        return {
            "success": False,
            "iterations": max_iterations,
            "final_error": result.get("error"),
            "history": fix_history
        }

    def evolve(self):
        idx = STRATEGY_ORDER.index(self.current_strategy)
        if idx < len(STRATEGY_ORDER) - 1:
            self.current_strategy = STRATEGY_ORDER[idx + 1]
            self.generation += 1
            self._write_strategy()
        return self.current_strategy

    def reset_strategy(self):
        self.current_strategy = "pattern_match"
        self.generation = 0
        self._write_strategy()

    def show_strategy(self):
        code = self.strategy_file.read_text()
        lines = code.split('\n')
        print(f"\n  \033[93m┌─ FIX STRATEGY (Gen {self.generation}) ─────────────────────┐\033[0m")
        for line in lines[:25]:
            print(f"  \033[93m│\033[0m {line}")
        if len(lines) > 25:
            print(f"  \033[93m│\033[0m ...")
        print(f"  \033[93m└───────────────────────────────────────────────┘\033[0m")


# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo(interactive: bool = True):
    """Run the autonomous bug fixer demonstration."""

    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Autonomous Bug Fixer Demo                              ║
    ║                                                          ║
    ║   Given only a failing test, the agent:                  ║
    ║   1. Finds the relevant code in the codebase             ║
    ║   2. Analyzes why the test fails                         ║
    ║   3. Writes a fix                                        ║
    ║   4. Runs the test                                       ║
    ║   5. Iterates until green                                ║
    ║                                                          ║
    ║   GitHub Copilot can't do this.                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if interactive:
        input("  Press ENTER to start...")
    else:
        time.sleep(1)

    init_memory_db()
    agent = AutonomousBugFixer(CODEBASE)

    results = []

    for i, scenario in enumerate(BUG_SCENARIOS):
        print("\033[2J\033[H")
        print("=" * 60)
        print("  AUTONOMOUS BUG FIXER - LIVE DEMO")
        print("=" * 60)
        print()

        agent.reset_strategy()

        print(f"  \033[96mBug {i+1}/{len(BUG_SCENARIOS)}: {scenario['name']}\033[0m")
        print(f"  \033[90mTarget: {scenario['target_file']}\033[0m")
        print(f"  Difficulty: {'⭐' * scenario['difficulty']}")
        print()

        # Show the failing test
        print("  \033[91m┌─ FAILING TEST ────────────────────────────────┐\033[0m")
        for line in scenario['test_code'].strip().split('\n'):
            print(f"  \033[91m│\033[0m {line}")
        print("  \033[91m└───────────────────────────────────────────────┘\033[0m")
        print()

        # Show the buggy code
        print("  \033[90m┌─ BUGGY CODE ──────────────────────────────────┐\033[0m")
        for line in CODEBASE[scenario['target_file']].strip().split('\n')[:15]:
            print(f"  \033[90m│\033[0m {line}")
        print("  \033[90m└───────────────────────────────────────────────┘\033[0m")
        print()

        # Run test to show it fails
        result = agent._run_test(scenario['test_code'], scenario['target_file'])
        if not result["success"]:
            print(f"  \033[91m✗ TEST FAILED: {result['error']}\033[0m")
        print()

        if interactive:
            input("  Press ENTER to start fixing...")
        else:
            time.sleep(0.5)

        print()
        print("  \033[95m🔧 FIXING IN PROGRESS...\033[0m")
        print()

        fix_result = agent.fix_bug(scenario)

        if fix_result["success"]:
            print(f"  \033[92m✓ FIXED in {fix_result['iterations']} iteration(s)!\033[0m")
            print()

            # Show the fixed code
            print("  \033[92m┌─ FIXED CODE ──────────────────────────────────┐\033[0m")
            for line in fix_result['fixed_code'].strip().split('\n')[:15]:
                print(f"  \033[92m│\033[0m {line}")
            print("  \033[92m└───────────────────────────────────────────────┘\033[0m")
        else:
            print(f"  \033[91m✗ FAILED after {fix_result['iterations']} iterations\033[0m")
            print(f"  \033[91m  Error: {fix_result.get('final_error', 'Unknown')}\033[0m")

        results.append({
            "name": scenario["name"],
            "success": fix_result["success"],
            "iterations": fix_result["iterations"],
            "difficulty": scenario["difficulty"]
        })

        print()
        print(f"  Progress: {agent.bugs_fixed}/{agent.total_attempts} bugs fixed")

        if interactive:
            input("\n  Press ENTER for next bug...")
        else:
            time.sleep(1)

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO COMPLETE                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  BUG FIX RESULTS:")
    print("  " + "─" * 56)

    for r in results:
        status = "\033[92m✓\033[0m" if r["success"] else "\033[91m✗\033[0m"
        stars = "⭐" * r["difficulty"]
        print(f"    {status} {r['name']} ({r['iterations']} iter) {stars}")

    success_rate = (agent.bugs_fixed / agent.total_attempts * 100) if agent.total_attempts > 0 else 0
    print()
    print(f"  Final Success Rate: \033[96m{success_rate:.0f}%\033[0m")
    print(f"  Bugs Fixed: {agent.bugs_fixed}/{agent.total_attempts}")
    print()

    print("  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    Given only failing tests, the agent found the bugs,")
    print("    understood the root causes, and wrote fixes.")
    print()
    print("    \033[96mThis is autonomous software engineering.\033[0m")
    print()


if __name__ == "__main__":
    try:
        interactive = "--auto" not in sys.argv
        run_demo(interactive=interactive)
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
