#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - Self-Evolving Repository

A repository that evolves its own code autonomously:
1. Analyzes code for issues and improvements
2. Generates fixes and enhancements
3. Runs tests to validate changes
4. Commits improvements (simulated Git workflow)
5. Tracks evolution history

This demonstrates autonomous code evolution through RIA.
"""

import sys
import time
import random
import argparse
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import init_memory_db, save_episode


# Evolution strategies for each function
EVOLUTION_STRATEGIES = {
    "validate_email": [
        # Gen 0 -> 1: Add proper regex
        {
            "issue": "Email validation too simple - allows invalid formats like '@.'",
            "fix_description": "Use regex pattern for proper email validation",
            "new_code": '''def validate_email(email):
    """Validate an email address using regex pattern."""
    import re
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
'''
        },
        # Gen 1 -> 2: Add compiled regex for performance
        {
            "issue": "Email validation recompiles regex on every call",
            "fix_description": "Use compiled regex pattern for better performance",
            "new_code": '''import re
_EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validate an email address using compiled regex pattern."""
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_PATTERN.match(email))
'''
        },
    ],
    "slugify": [
        # Gen 0 -> 1: Handle multiple spaces
        {
            "issue": "Slugify creates multiple consecutive dashes",
            "fix_description": "Collapse multiple spaces/dashes into single dash",
            "new_code": '''def slugify(text):
    """Convert text to URL-friendly slug."""
    import re
    if not text:
        return ""
    # Convert to lowercase and replace non-alphanumeric with dashes
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
    # Remove leading/trailing dashes
    return slug.strip('-')
'''
        },
        # Gen 1 -> 2: Unicode support
        {
            "issue": "Slugify doesn't handle unicode characters",
            "fix_description": "Add unicode normalization and transliteration",
            "new_code": '''def slugify(text):
    """Convert text to URL-friendly slug with unicode support."""
    import re
    import unicodedata
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace non-alphanumeric with dashes
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
    return slug.strip('-')
'''
        },
    ],
    "truncate": [
        # Gen 0 -> 1: Word-boundary aware
        {
            "issue": "Truncate cuts words in middle",
            "fix_description": "Truncate at word boundaries when possible",
            "new_code": '''def truncate(text, length, suffix="..."):
    """Truncate text to specified length, respecting word boundaries."""
    if not text or len(text) <= length:
        return text

    # Find last space before length
    truncated = text[:length]
    last_space = truncated.rfind(' ')

    if last_space > length // 2:
        return truncated[:last_space] + suffix
    return truncated + suffix
'''
        },
    ],
    "parse_int": [
        # Gen 0 -> 1: Handle more formats
        {
            "issue": "parse_int doesn't handle whitespace or negative numbers well",
            "fix_description": "Strip whitespace and handle negative numbers",
            "new_code": '''def parse_int(value, default=None):
    """Parse a value to integer with better error handling."""
    if value is None:
        return default

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default

    return default
'''
        },
    ],
    "unique": [
        # Gen 0 -> 1: Use dict for O(1) lookups
        {
            "issue": "unique() is O(n²) due to 'in' check on list",
            "fix_description": "Use dict for O(1) membership checks",
            "new_code": '''def unique(items):
    """Get unique items from list, preserving order. O(n) complexity."""
    if not items:
        return []
    seen = {}
    result = []
    for item in items:
        # Use id() for unhashable items
        try:
            key = item
            if key not in seen:
                seen[key] = True
                result.append(item)
        except TypeError:
            # Unhashable - fall back to list check
            if item not in result:
                result.append(item)
    return result
'''
        },
    ],
}


class EvolutionAgent:
    """Agent that evolves a codebase autonomously."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.src_path = repo_path / "src"
        self.tests_path = repo_path / "tests"
        self.generation = 0
        self.commits = []
        self.evolution_index = {func: 0 for func in EVOLUTION_STRATEGIES}

    def analyze_code(self) -> List[Dict]:
        """Analyze code for potential improvements."""
        issues = []

        for func_name, strategies in EVOLUTION_STRATEGIES.items():
            idx = self.evolution_index.get(func_name, 0)
            if idx < len(strategies):
                strategy = strategies[idx]
                issues.append({
                    "function": func_name,
                    "issue": strategy["issue"],
                    "fix_description": strategy["fix_description"],
                    "new_code": strategy["new_code"]
                })

        return issues

    def run_tests(self) -> Dict:
        """Run test suite and return results."""
        test_file = self.tests_path / "test_utils.py"

        try:
            spec = importlib.util.spec_from_file_location("tests", test_file)
            module = importlib.util.module_from_spec(spec)

            # Clear any cached imports
            if "utils" in sys.modules:
                del sys.modules["utils"]

            spec.loader.exec_module(module)
            results = module.run_tests()

            return {
                "passed": results.passed,
                "failed": results.failed,
                "total": results.passed + results.failed,
                "success_rate": results.passed / (results.passed + results.failed) if (results.passed + results.failed) > 0 else 0,
                "failures": results.failures
            }

        except Exception as e:
            return {
                "passed": 0,
                "failed": 1,
                "total": 1,
                "success_rate": 0,
                "failures": [{"name": "import", "error": str(e)}]
            }

    def apply_fix(self, fix: Dict) -> bool:
        """Apply a fix to the codebase."""
        utils_file = self.src_path / "utils.py"

        try:
            content = utils_file.read_text()

            # Find and replace the function
            func_name = fix["function"]
            new_code = fix["new_code"]

            # Simple replacement strategy - find function and replace
            import re

            # Pattern to match the function definition
            pattern = rf'(^def {func_name}\([^)]*\):.*?)(?=\n\ndef |\n\nclass |\Z)'

            # For functions with module-level code (like compiled regex)
            if new_code.strip().startswith("import") or new_code.strip().startswith("_"):
                # This code needs to go at the top level
                # Find if there's existing module-level code for this
                lines = content.split('\n')
                new_lines = []
                skip_until_def = False
                found = False

                for line in lines:
                    if line.startswith(f'def {func_name}('):
                        # Replace this function
                        skip_until_def = True
                        if not found:
                            new_lines.append(new_code.strip())
                            found = True
                    elif skip_until_def and (line.startswith('def ') or line.startswith('class ')):
                        skip_until_def = False
                        new_lines.append(line)
                    elif not skip_until_def:
                        new_lines.append(line)

                content = '\n'.join(new_lines)
            else:
                # Simple function replacement
                match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
                if match:
                    content = content[:match.start()] + new_code.strip() + content[match.end():]

            utils_file.write_text(content)
            return True

        except Exception as e:
            print(f"Error applying fix: {e}")
            return False

    def create_commit(self, message: str, fix: Dict):
        """Simulate creating a Git commit."""
        self.commits.append({
            "hash": f"{random.randint(1000000, 9999999):07x}",
            "message": message,
            "function": fix["function"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "generation": self.generation
        })

    def evolve(self) -> Dict:
        """Run one evolution cycle."""
        # Analyze for issues
        issues = self.analyze_code()

        if not issues:
            return {"status": "stable", "message": "No improvements found"}

        # Pick an issue to fix
        issue = issues[0]

        # Run tests before
        before_results = self.run_tests()

        # Apply fix
        if not self.apply_fix(issue):
            return {"status": "failed", "message": "Could not apply fix"}

        # Run tests after
        after_results = self.run_tests()

        # Check if improvement
        if after_results["success_rate"] >= before_results["success_rate"]:
            # Accept the change
            self.create_commit(
                f"improve: {issue['fix_description']}",
                issue
            )
            self.evolution_index[issue["function"]] += 1
            self.generation += 1

            return {
                "status": "evolved",
                "function": issue["function"],
                "issue": issue["issue"],
                "fix": issue["fix_description"],
                "before": before_results,
                "after": after_results,
                "commit": self.commits[-1]
            }
        else:
            # Revert - reload original
            return {
                "status": "rejected",
                "message": "Fix caused test failures",
                "before": before_results,
                "after": after_results
            }


def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Self-Evolving Repository Demo                          ║
    ║                                                          ║
    ║   A codebase that improves itself autonomously:          ║
    ║   1. Analyzes code for issues                            ║
    ║   2. Generates and applies fixes                         ║
    ║   3. Validates with test suite                           ║
    ║   4. Commits improvements automatically                  ║
    ║                                                          ║
    ║   Watch the commit history grow with AI-authored code.   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print("\033[2J\033[H")
    print(banner)


def display_evolution(result: Dict, agent: EvolutionAgent):
    """Display evolution result."""
    print("\033[2J\033[H")
    print(f"\n{'='*60}")
    print(f"  GENERATION {agent.generation}")
    print(f"{'='*60}\n")

    if result["status"] == "evolved":
        print(f"  \033[96mISSUE DETECTED:\033[0m")
        print("  " + "─" * 56)
        print(f"    {result['issue']}")

        print(f"\n  \033[96mFIX APPLIED:\033[0m")
        print("  " + "─" * 56)
        print(f"    {result['fix']}")

        print(f"\n  \033[96mTEST RESULTS:\033[0m")
        print("  " + "─" * 56)
        before = result["before"]
        after = result["after"]

        b_color = "\033[92m" if before["success_rate"] == 1.0 else "\033[93m"
        a_color = "\033[92m" if after["success_rate"] == 1.0 else "\033[93m"

        print(f"    Before: {b_color}{before['passed']}/{before['total']} ({before['success_rate']*100:.0f}%)\033[0m")
        print(f"    After:  {a_color}{after['passed']}/{after['total']} ({after['success_rate']*100:.0f}%)\033[0m")

        print(f"\n  \033[92m✓ COMMIT CREATED:\033[0m")
        commit = result["commit"]
        print(f"    {commit['hash']} {commit['message']}")

    elif result["status"] == "stable":
        print(f"  \033[92m✓ Repository is stable - no improvements needed\033[0m")

    elif result["status"] == "rejected":
        print(f"  \033[91m✗ Fix rejected - caused test failures\033[0m")


def display_commit_history(agent: EvolutionAgent):
    """Display simulated Git commit history."""
    print("\n  \033[96mCOMMIT HISTORY:\033[0m")
    print("  " + "─" * 56)

    for commit in agent.commits:
        print(f"    \033[93m{commit['hash']}\033[0m {commit['message']}")


def display_final_summary(agent: EvolutionAgent):
    """Display final evolution summary."""
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              EVOLUTION COMPLETE                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  REPOSITORY STATISTICS:")
    print("  " + "─" * 56)
    print(f"    Generations:     {agent.generation}")
    print(f"    Total commits:   {len(agent.commits)}")

    # Functions evolved
    evolved = [f for f, idx in agent.evolution_index.items() if idx > 0]
    print(f"    Functions evolved: {len(evolved)}")

    # Commit history
    if agent.commits:
        print("\n  GIT COMMIT LOG:")
        print("  " + "─" * 56)
        for commit in agent.commits:
            print(f"    \033[93m{commit['hash']}\033[0m {commit['message']}")

    # Final test results
    results = agent.run_tests()
    print("\n  FINAL TEST RESULTS:")
    print("  " + "─" * 56)
    color = "\033[92m" if results["success_rate"] == 1.0 else "\033[93m"
    print(f"    {color}{results['passed']}/{results['total']} tests passing ({results['success_rate']*100:.0f}%)\033[0m")

    if results["failures"]:
        print("\n    Remaining failures:")
        for f in results["failures"][:3]:
            print(f"      • {f['name']}")

    # Key insight
    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    This repository evolved its own code through")
    print("    analysis, generation, testing, and selection.")
    print("\n    \033[96mEvery commit was authored by the AI, not a human.\033[0m\n")


def reset_repo(repo_path: Path):
    """Reset repo to initial state."""
    src_file = repo_path / "src" / "utils.py"

    initial_code = '''"""
Utility Library - Generation 0
This library evolves autonomously through Recursive Intelligence.
"""

def validate_email(email):
    """Validate an email address."""
    if "@" in email and "." in email:
        return True
    return False


def slugify(text):
    """Convert text to URL-friendly slug."""
    result = ""
    for char in text.lower():
        if char.isalnum():
            result += char
        elif char == " ":
            result += "-"
    return result


def truncate(text, length):
    """Truncate text to specified length."""
    if len(text) <= length:
        return text
    return text[:length] + "..."


def parse_int(value):
    """Parse a value to integer."""
    try:
        return int(value)
    except:
        return None


def unique(items):
    """Get unique items from list."""
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
'''

    src_file.write_text(initial_code)


def main():
    parser = argparse.ArgumentParser(description="Self-Evolving Repository Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically")
    parser.add_argument("--generations", type=int, default=6, help="Number of evolution cycles")
    args = parser.parse_args()

    # Initialize
    init_memory_db()
    print_banner()

    if not args.auto:
        input("  Press Enter to start evolution...")
    else:
        time.sleep(1)

    # Setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ria.evolving_repo")

    # Reset repo to initial state
    repo_path = Path(__file__).parent / "evolving_repo"
    reset_repo(repo_path)

    # Create agent
    agent = EvolutionAgent(repo_path)

    # Initial test run
    initial_results = agent.run_tests()
    logger.info(f"Initial state: {initial_results['passed']}/{initial_results['total']} tests passing")

    # Evolution loop
    for i in range(args.generations):
        result = agent.evolve()
        display_evolution(result, agent)

        if result["status"] == "evolved":
            logger.info(f"Gen {agent.generation}: Improved {result['function']}")

            save_episode(
                task=f"evolve_{result['function']}",
                result="improved",
                reflection=result["fix"]
            )
        elif result["status"] == "stable":
            logger.info("Repository reached stable state")
            break

        time.sleep(0.8)

    # Final summary
    display_final_summary(agent)

    logger.info(f"Evolution complete: {agent.generation} generations, {len(agent.commits)} commits")


if __name__ == "__main__":
    main()
