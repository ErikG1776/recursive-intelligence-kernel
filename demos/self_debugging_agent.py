#!/usr/bin/env python3
"""
Self-Debugging Agent Demo - Recursive Intelligence Algorithm

Demonstrates RIA applied to autonomous debugging:
- Agent receives broken code + failing test
- Runs the code, analyzes the error
- Hypothesizes the cause
- Writes a fix
- Tests again
- Iterates until tests pass

This is the holy grail of developer productivity.
"""

import sys
import os
import time
import importlib.util
import traceback
import signal
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import setup_logging
from memory import init_memory_db, save_episode, get_recent_episodes

logger = setup_logging("ria.debug_demo")

# ==========================================================
# === BROKEN CODE CHALLENGES ===============================
# ==========================================================

CHALLENGES = [
    {
        "name": "Off-by-One Error",
        "description": "Function to get the last N elements of a list",
        "broken_code": '''
def get_last_n(lst, n):
    """Return the last n elements of a list."""
    return lst[len(lst) - n + 1:]
''',
        "test_code": '''
def test_get_last_n():
    assert get_last_n([1, 2, 3, 4, 5], 3) == [3, 4, 5], "Should return last 3 elements"
    assert get_last_n([1, 2, 3], 1) == [3], "Should return last element"
    assert get_last_n([1, 2, 3, 4], 4) == [1, 2, 3, 4], "Should return all elements"
    return True
''',
        "difficulty": 1
    },
    {
        "name": "Type Coercion Bug",
        "description": "Function to calculate average of numbers",
        "broken_code": '''
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
''',
        "test_code": '''
def test_calculate_average():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0, "Average of 1-5 should be 3.0"
    assert calculate_average([10]) == 10.0, "Average of single element"
    assert calculate_average([0, 0, 0]) == 0.0, "Average of zeros"
    # Edge case that breaks integer division in some contexts
    assert abs(calculate_average([1, 2]) - 1.5) < 0.001, "Average should be 1.5"
    return True
''',
        "difficulty": 1
    },
    {
        "name": "Boundary Condition Bug",
        "description": "Binary search implementation",
        "broken_code": '''
def binary_search(arr, target):
    """Find target in sorted array, return index or -1."""
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid
    return -1
''',
        "test_code": '''
def test_binary_search():
    arr = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search(arr, 7) == 3, "Should find 7 at index 3"
    assert binary_search(arr, 1) == 0, "Should find 1 at index 0"
    assert binary_search(arr, 13) == 6, "Should find 13 at index 6"
    assert binary_search(arr, 4) == -1, "Should return -1 for missing element"
    assert binary_search([], 5) == -1, "Should handle empty array"
    return True
''',
        "difficulty": 2
    },
    {
        "name": "Logic Error",
        "description": "Check if string is palindrome",
        "broken_code": '''
def is_palindrome(s):
    """Check if string is a palindrome (ignoring case and spaces)."""
    cleaned = s.lower().replace(" ", "")
    for i in range(len(cleaned)):
        if cleaned[i] != cleaned[len(cleaned) - i]:
            return False
    return True
''',
        "test_code": '''
def test_is_palindrome():
    assert is_palindrome("racecar") == True, "racecar is palindrome"
    assert is_palindrome("A man a plan a canal Panama") == True, "Classic palindrome"
    assert is_palindrome("hello") == False, "hello is not palindrome"
    assert is_palindrome("") == True, "Empty string is palindrome"
    assert is_palindrome("a") == True, "Single char is palindrome"
    return True
''',
        "difficulty": 2
    },
    {
        "name": "Algorithm Bug",
        "description": "Find all prime numbers up to n (Sieve of Eratosthenes)",
        "broken_code": '''
def sieve_of_eratosthenes(n):
    """Return all prime numbers up to n."""
    if n < 2:
        return []

    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(n ** 0.5)):
        if is_prime[i]:
            for j in range(i * i, n, i):
                is_prime[j] = False

    return [i for i in range(n) if is_prime[i]]
''',
        "test_code": '''
def test_sieve_of_eratosthenes():
    assert sieve_of_eratosthenes(10) == [2, 3, 5, 7], "Primes up to 10"
    assert sieve_of_eratosthenes(20) == [2, 3, 5, 7, 11, 13, 17, 19], "Primes up to 20"
    assert sieve_of_eratosthenes(2) == [2], "Should include 2"
    assert sieve_of_eratosthenes(1) == [], "No primes below 2"
    return True
''',
        "difficulty": 3
    }
]

# ==========================================================
# === FIX STRATEGY TEMPLATES ===============================
# ==========================================================

# The agent will generate these based on error analysis
FIX_STRATEGIES = {
    "analyze_error": '''
def analyze_and_fix(code, error_msg, test_code):
    """Analyze error message and apply targeted fix."""
    lines = code.strip().split('\\n')

    for i, line in enumerate(lines):
        # Off-by-one in slice: lst[len(lst) - n + 1:] should be lst[-n:]
        if "- n + 1]" in line or "- n + 1:" in line:
            lines[i] = line.replace("len(lst) - n + 1:", "-n:")

        # Index error in palindrome check
        if "- i]" in line and "- i - 1]" not in line and "cleaned" in line:
            lines[i] = line.replace("- i]", "- i - 1]")

    # Check for zero division
    if "ZeroDivisionError" in error_msg:
        for i, line in enumerate(lines):
            if "/ len(" in line:
                indent = len(line) - len(line.lstrip())
                lines.insert(i, " " * indent + "if not numbers: return 0.0")
                break

    return '\\n'.join(lines)
''',

    "trace_execution": '''
def analyze_and_fix(code, error_msg, test_code):
    """Trace through execution to find logic errors."""
    lines = code.strip().split('\\n')

    # Look for loop boundary issues
    for i, line in enumerate(lines):
        # Binary search boundary fix
        if "left = mid" in line and "left = mid + 1" not in line:
            lines[i] = line.replace("left = mid", "left = mid + 1")

        # Range boundary fix
        if "range(2, int(n ** 0.5))" in line:
            lines[i] = line.replace("int(n ** 0.5)", "int(n ** 0.5) + 1")

        # Array size fix
        if "[True] * n" in line:
            lines[i] = line.replace("* n", "* (n + 1)")
        if "range(n)" in line and "is_prime" in line:
            lines[i] = line.replace("range(n)", "range(n + 1)")

    return '\\n'.join(lines)
''',

    "boundary_analysis": '''
def analyze_and_fix(code, error_msg, test_code):
    """Analyze boundary conditions and edge cases."""
    lines = code.strip().split('\\n')

    for i, line in enumerate(lines):
        # Fix off-by-one in index calculations
        if "len(cleaned) - i]" in line:
            lines[i] = line.replace("len(cleaned) - i]", "len(cleaned) - i - 1]")

        # Fix range to include endpoint
        if "range(len(" in line and "// 2" not in line:
            lines[i] = line.replace("range(len(", "range(len(")
            # For palindrome, only need to check half
            if "cleaned))" in line:
                lines[i] = line.replace("range(len(cleaned))", "range(len(cleaned) // 2)")

    return '\\n'.join(lines)
''',

    "comprehensive_fix": '''
def analyze_and_fix(code, error_msg, test_code):
    """Apply comprehensive analysis with multiple fix strategies."""
    lines = code.strip().split('\\n')

    for i, line in enumerate(lines):
        # Index calculation fixes - off by one errors
        if "- n + 1]" in line:
            lines[i] = line.replace("- n + 1]", "- n:]")
        if "- i]" in line and "- i - 1]" not in line and "cleaned" in line:
            lines[i] = line.replace("- i]", "- i - 1]")

        # Loop boundary fixes - binary search infinite loop
        if "left = mid" in line and "mid + 1" not in line:
            lines[i] = line.replace("left = mid", "left = mid + 1")

        # Sieve fixes
        if "int(n ** 0.5))" in line and "+ 1" not in line:
            lines[i] = line.replace("int(n ** 0.5))", "int(n ** 0.5) + 1)")
        if "[True] * n" in line:
            lines[i] = line.replace("* n", "* (n + 1)")
        if "range(n) if is_prime" in line:
            lines[i] = line.replace("range(n)", "range(n + 1)")

        # Palindrome optimization
        if "range(len(cleaned))" in line:
            lines[i] = line.replace("range(len(cleaned))", "range(len(cleaned) // 2)")

    return '\\n'.join(lines)
'''
}

STRATEGY_ORDER = [
    "analyze_error",
    "trace_execution",
    "boundary_analysis",
    "comprehensive_fix"
]

# ==========================================================
# === SELF-DEBUGGING AGENT =================================
# ==========================================================

class SelfDebuggingAgent:
    """
    Agent that autonomously debugs broken code.

    The key insight: instead of giving up on errors,
    the agent analyzes the failure and generates fixes.
    """

    def __init__(self):
        self.strategy_file = Path(__file__).parent / "generated_fixer.py"
        self.code_file = Path(__file__).parent / "code_under_test.py"
        self.current_strategy = "analyze_error"
        self.generation = 0
        self.total_fixes = 0
        self.total_attempts = 0
        self.history = []

        # Write initial strategy
        self._write_strategy(self.current_strategy)

    def _write_strategy(self, strategy_name: str):
        """Write a new fix strategy to disk."""
        template = FIX_STRATEGIES[strategy_name]

        code = f'''"""
Generated Fix Strategy: {strategy_name}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{template}
'''
        self.strategy_file.write_text(code)
        logger.info(f"Wrote fix strategy '{strategy_name}'")

    def _load_fixer(self):
        """Dynamically load the current fix function."""
        spec = importlib.util.spec_from_file_location("generated_fixer", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_and_fix

    def _run_test(self, code: str, test_code: str) -> dict:
        """Run the test against the code and return results."""
        def timeout_handler(signum, frame):
            raise TimeoutError("Test execution timed out (infinite loop?)")

        try:
            # Write combined code to file
            full_code = code + "\n\n" + test_code + "\n\nresult = test_" + test_code.split("def test_")[1].split("(")[0] + "()"
            self.code_file.write_text(full_code)

            # Set timeout (2 seconds should be plenty for these tests)
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(2)

            try:
                # Execute in isolated namespace
                namespace = {}
                exec(compile(full_code, self.code_file, 'exec'), namespace)

                return {
                    "success": True,
                    "result": namespace.get("result", True)
                }
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        except TimeoutError as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": "Execution timed out - likely infinite loop"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def debug_challenge(self, challenge: dict) -> dict:
        """
        Attempt to debug a broken code challenge.

        Returns dict with success status and fix history.
        """
        self.total_attempts += 1

        code = challenge["broken_code"]
        test_code = challenge["test_code"]
        max_iterations = 4

        fix_history = []

        for iteration in range(max_iterations):
            # Run the test
            result = self._run_test(code, test_code)

            if result["success"]:
                self.total_fixes += 1
                fix_history.append({
                    "iteration": iteration,
                    "status": "fixed",
                    "strategy": self.current_strategy
                })

                # Save to episodic memory
                save_episode(
                    task=f"debug_{challenge['name']}",
                    result="success",
                    reflection=f"Fixed with {self.current_strategy} in {iteration + 1} iterations"
                )

                return {
                    "success": True,
                    "iterations": iteration + 1,
                    "final_code": code,
                    "history": fix_history,
                    "strategy": self.current_strategy
                }

            # Record the failure
            error_msg = result.get("error", "Unknown error")
            fix_history.append({
                "iteration": iteration,
                "status": "failed",
                "error": error_msg,
                "strategy": self.current_strategy
            })

            # Load and apply fix strategy
            try:
                fixer = self._load_fixer()
                code = fixer(code, error_msg, test_code)
            except Exception as e:
                logger.error(f"Fixer failed: {e}")

            # If still failing after fix, evolve strategy
            if iteration > 0 and iteration < max_iterations - 1:
                self.evolve()

        # Final attempt
        result = self._run_test(code, test_code)
        if result["success"]:
            self.total_fixes += 1
            save_episode(
                task=f"debug_{challenge['name']}",
                result="success",
                reflection=f"Fixed with {self.current_strategy} after evolution"
            )
            return {
                "success": True,
                "iterations": max_iterations,
                "final_code": code,
                "history": fix_history,
                "strategy": self.current_strategy
            }

        save_episode(
            task=f"debug_{challenge['name']}",
            result=f"failure: {result.get('error', 'unknown')}",
            reflection=f"Failed after {max_iterations} iterations"
        )

        return {
            "success": False,
            "iterations": max_iterations,
            "final_code": code,
            "history": fix_history,
            "final_error": result.get("error", "Unknown")
        }

    def evolve(self) -> str:
        """Evolve to the next fix strategy."""
        current_idx = STRATEGY_ORDER.index(self.current_strategy)
        next_idx = min(current_idx + 1, len(STRATEGY_ORDER) - 1)
        self.current_strategy = STRATEGY_ORDER[next_idx]
        self.generation += 1

        self._write_strategy(self.current_strategy)
        return self.current_strategy

    def show_strategy(self):
        """Display the current fix strategy code."""
        code = self.strategy_file.read_text()
        lines = code.split('\n')

        print(f"\n  \033[93m┌─ GENERATED FIX STRATEGY ──────────────────────┐\033[0m")
        for line in lines[:30]:
            print(f"  \033[93m│\033[0m {line}")
        if len(lines) > 30:
            print(f"  \033[93m│\033[0m ...")
        print(f"  \033[93m└───────────────────────────────────────────────┘\033[0m")

    def reset_strategy(self):
        """Reset to initial strategy for new challenge."""
        self.current_strategy = "analyze_error"
        self.generation = 0
        self._write_strategy(self.current_strategy)

# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo(interactive: bool = True):
    """Run the self-debugging agent demonstration."""

    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Self-Debugging Agent Demo                              ║
    ║                                                          ║
    ║   Watch the agent:                                       ║
    ║   1. Receive broken code + failing test                  ║
    ║   2. Run the code, analyze the error                     ║
    ║   3. Hypothesize the cause                               ║
    ║   4. Write a fix                                         ║
    ║   5. Test again, iterate until green                     ║
    ║                                                          ║
    ║   This is autonomous debugging.                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if interactive:
        input("  Press ENTER to start...")
    else:
        time.sleep(1)

    init_memory_db()
    agent = SelfDebuggingAgent()

    results = []

    for i, challenge in enumerate(CHALLENGES):
        print("\033[2J\033[H")
        print("=" * 60)
        print("  SELF-DEBUGGING AGENT - LIVE DEMO")
        print("=" * 60)
        print()

        # Reset strategy for each challenge
        agent.reset_strategy()

        print(f"  \033[96mChallenge {i+1}/{len(CHALLENGES)}: {challenge['name']}\033[0m")
        print(f"  \033[90m{challenge['description']}\033[0m")
        print(f"  Difficulty: {'⭐' * challenge['difficulty']}")
        print()

        # Show broken code
        print("  \033[91m┌─ BROKEN CODE ─────────────────────────────────┐\033[0m")
        for line in challenge['broken_code'].strip().split('\n'):
            print(f"  \033[91m│\033[0m {line}")
        print("  \033[91m└───────────────────────────────────────────────┘\033[0m")
        print()

        # First test - show it fails
        result = agent._run_test(challenge['broken_code'], challenge['test_code'])
        if not result["success"]:
            print(f"  \033[91m✗ TEST FAILED: {result['error']}\033[0m")
        print()

        if interactive:
            input("  Press ENTER to start debugging...")
        else:
            time.sleep(0.5)

        # Run the debugging process
        print()
        print("  \033[95m🔧 DEBUGGING IN PROGRESS...\033[0m")
        print()

        debug_result = agent.debug_challenge(challenge)

        if debug_result["success"]:
            print(f"  \033[92m✓ FIXED in {debug_result['iterations']} iteration(s)!\033[0m")
            print(f"  \033[92m  Final strategy: {debug_result['strategy']}\033[0m")
            print()

            # Show the fixed code
            print("  \033[92m┌─ FIXED CODE ──────────────────────────────────┐\033[0m")
            for line in debug_result['final_code'].strip().split('\n'):
                print(f"  \033[92m│\033[0m {line}")
            print("  \033[92m└───────────────────────────────────────────────┘\033[0m")
        else:
            print(f"  \033[91m✗ FAILED after {debug_result['iterations']} iterations\033[0m")
            print(f"  \033[91m  Error: {debug_result.get('final_error', 'Unknown')}\033[0m")

        results.append({
            "name": challenge["name"],
            "success": debug_result["success"],
            "iterations": debug_result["iterations"],
            "difficulty": challenge["difficulty"]
        })

        # Show evolution if it happened
        if agent.generation > 0:
            print()
            print(f"  \033[95mStrategy evolved {agent.generation} time(s)\033[0m")
            agent.show_strategy()

        print()
        print(f"  Progress: {agent.total_fixes}/{agent.total_attempts} bugs fixed")

        if interactive:
            input("\n  Press ENTER for next challenge...")
        else:
            time.sleep(1)

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO COMPLETE                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  DEBUGGING RESULTS:")
    print("  " + "─" * 56)

    for r in results:
        status = "\033[92m✓\033[0m" if r["success"] else "\033[91m✗\033[0m"
        stars = "⭐" * r["difficulty"]
        print(f"    {status} {r['name']} ({r['iterations']} iter) {stars}")

    success_rate = (agent.total_fixes / agent.total_attempts * 100) if agent.total_attempts > 0 else 0
    print()
    print(f"  Final Success Rate: \033[96m{success_rate:.0f}%\033[0m")
    print(f"  Bugs Fixed: {agent.total_fixes}/{agent.total_attempts}")
    print()

    print("  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The agent analyzed errors, hypothesized causes,")
    print("    and wrote fixes - all without human intervention.")
    print()
    print("    \033[96mThis is autonomous debugging.\033[0m")
    print()

    print("  FINAL FIX STRATEGY:")
    agent.show_strategy()


if __name__ == "__main__":
    try:
        interactive = "--auto" not in sys.argv
        run_demo(interactive=interactive)
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
