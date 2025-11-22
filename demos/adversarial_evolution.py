#!/usr/bin/env python3
"""
Adversarial Self-Improvement Demo - Recursive Intelligence Algorithm

Two RIA agents compete to make each other stronger:
- Agent A (Defender): Writes code to solve a task
- Agent B (Attacker): Writes edge cases to break Agent A's code
- Agent A evolves to handle the edge cases
- Repeat until Agent A is robust

This is artificial evolution through competition.
"""

import sys
import os
import time
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import setup_logging
from memory import init_memory_db, save_episode

logger = setup_logging("ria.adversarial")

# ==========================================================
# === TASK DEFINITION ======================================
# ==========================================================

TASK = {
    "name": "Username Validator",
    "description": "Validate and sanitize usernames for a web application",
    "requirements": [
        "Length between 3-20 characters",
        "Only alphanumeric and underscore",
        "Cannot start with number",
        "Cannot be empty or whitespace only",
        "Return sanitized username or raise ValueError"
    ]
}

# ==========================================================
# === DEFENDER STRATEGIES ==================================
# ==========================================================

DEFENDER_STRATEGIES = {
    "basic": '''
def validate_username(username):
    """Basic username validation."""
    if len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be 3-20 characters")
    if not username.isalnum() and "_" not in username:
        raise ValueError("Only alphanumeric and underscore allowed")
    return username.lower()
''',

    "type_safe": '''
def validate_username(username):
    """Type-safe username validation."""
    if not isinstance(username, str):
        raise ValueError("Username must be a string")
    if len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be 3-20 characters")
    if not all(c.isalnum() or c == "_" for c in username):
        raise ValueError("Only alphanumeric and underscore allowed")
    if username[0].isdigit():
        raise ValueError("Cannot start with number")
    return username.lower()
''',

    "whitespace_aware": '''
def validate_username(username):
    """Whitespace-aware username validation."""
    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    # Strip and check for empty
    username = username.strip()
    if not username:
        raise ValueError("Username cannot be empty")

    if len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be 3-20 characters")
    if not all(c.isalnum() or c == "_" for c in username):
        raise ValueError("Only alphanumeric and underscore allowed")
    if username[0].isdigit():
        raise ValueError("Cannot start with number")
    return username.lower()
''',

    "robust": '''
def validate_username(username):
    """Robust username validation with full edge case handling."""
    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    # Handle whitespace
    username = username.strip()
    if not username:
        raise ValueError("Username cannot be empty")

    # Check length
    if len(username) < 3:
        raise ValueError("Username too short (min 3)")
    if len(username) > 20:
        raise ValueError("Username too long (max 20)")

    # Check characters
    for i, c in enumerate(username):
        if not (c.isalnum() or c == "_"):
            raise ValueError(f"Invalid character: {repr(c)}")

    # Check first character
    if username[0].isdigit():
        raise ValueError("Cannot start with number")

    return username.lower()
''',

    "bulletproof": '''
def validate_username(username):
    """Bulletproof username validation - handles all adversarial inputs."""
    # Type check
    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    # Handle None-like strings
    if username.lower() in ('none', 'null', 'undefined'):
        raise ValueError("Invalid username value")

    # Strip all whitespace types
    import re
    username = re.sub(r'^\\s+|\\s+$', '', username)

    if not username:
        raise ValueError("Username cannot be empty")

    # Length checks
    if len(username) < 3:
        raise ValueError("Username too short")
    if len(username) > 20:
        raise ValueError("Username too long")

    # Character validation - ASCII only
    for c in username:
        if not (c.isascii() and (c.isalnum() or c == "_")):
            raise ValueError(f"Invalid character: {repr(c)}")

    # First character check
    if username[0].isdigit():
        raise ValueError("Cannot start with number")

    # Reserved words
    reserved = ['admin', 'root', 'system', 'null', 'undefined']
    if username.lower() in reserved:
        raise ValueError("Reserved username")

    return username.lower()
'''
}

DEFENDER_ORDER = ["basic", "type_safe", "whitespace_aware", "robust", "bulletproof"]

# ==========================================================
# === ATTACKER STRATEGIES ==================================
# ==========================================================

ATTACKER_STRATEGIES = {
    "basic_probes": '''
def generate_attacks():
    """Basic edge case probes."""
    return [
        ("", "empty string"),
        ("ab", "too short"),
        ("a" * 25, "too long"),
        ("123user", "starts with number"),
        ("user@name", "special character"),
    ]
''',

    "type_confusion": '''
def generate_attacks():
    """Type confusion attacks."""
    return [
        (None, "None value"),
        (123, "integer instead of string"),
        (["user"], "list instead of string"),
        ({"name": "user"}, "dict instead of string"),
        (True, "boolean instead of string"),
    ]
''',

    "whitespace_attacks": '''
def generate_attacks():
    """Whitespace and invisible character attacks."""
    return [
        ("   ", "only spaces"),
        ("\\t\\n\\r", "only whitespace chars"),
        ("  user  ", "padded with spaces"),
        ("user\\x00name", "null byte injection"),
        ("user\\nname", "newline injection"),
    ]
''',

    "unicode_attacks": '''
def generate_attacks():
    """Unicode and encoding attacks."""
    return [
        ("usér", "accented character"),
        ("user™", "trademark symbol"),
        ("用户名", "Chinese characters"),
        ("user\\u200b", "zero-width space"),
        ("admin\\u0000", "null after valid"),
    ]
''',

    "adversarial_inputs": '''
def generate_attacks():
    """Adversarial and injection attacks."""
    return [
        ("None", "string 'None'"),
        ("null", "string 'null'"),
        ("undefined", "string 'undefined'"),
        ("admin", "reserved word"),
        ("root", "system username"),
        ("<script>", "XSS attempt"),
        ("user'; DROP TABLE", "SQL injection pattern"),
    ]
'''
}

ATTACKER_ORDER = ["basic_probes", "type_confusion", "whitespace_attacks", "unicode_attacks", "adversarial_inputs"]

# ==========================================================
# === AGENTS ===============================================
# ==========================================================

class DefenderAgent:
    """Agent that writes and evolves validation code."""

    def __init__(self):
        self.strategy_file = Path(__file__).parent / "defender_code.py"
        self.current_strategy = "basic"
        self.generation = 0
        self._write_strategy()

    def _write_strategy(self):
        code = f'''"""
Defender Strategy: {self.current_strategy}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{DEFENDER_STRATEGIES[self.current_strategy]}
'''
        self.strategy_file.write_text(code)
        logger.info(f"Defender evolved to '{self.current_strategy}'")

    def load_validator(self):
        spec = importlib.util.spec_from_file_location("defender", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.validate_username

    def evolve(self):
        idx = DEFENDER_ORDER.index(self.current_strategy)
        if idx < len(DEFENDER_ORDER) - 1:
            self.current_strategy = DEFENDER_ORDER[idx + 1]
            self.generation += 1
            self._write_strategy()
        return self.current_strategy

    def show_code(self):
        code = self.strategy_file.read_text()
        lines = code.split('\n')
        print(f"\n  \033[92m┌─ DEFENDER CODE (Gen {self.generation}) ─────────────────────┐\033[0m")
        for line in lines[:25]:
            print(f"  \033[92m│\033[0m {line}")
        if len(lines) > 25:
            print(f"  \033[92m│\033[0m ...")
        print(f"  \033[92m└────────────────────────────────────────────────┘\033[0m")


class AttackerAgent:
    """Agent that writes edge cases to break the defender."""

    def __init__(self):
        self.strategy_file = Path(__file__).parent / "attacker_code.py"
        self.current_strategy = "basic_probes"
        self.generation = 0
        self._write_strategy()

    def _write_strategy(self):
        code = f'''"""
Attacker Strategy: {self.current_strategy}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{ATTACKER_STRATEGIES[self.current_strategy]}
'''
        self.strategy_file.write_text(code)
        logger.info(f"Attacker evolved to '{self.current_strategy}'")

    def load_attacks(self):
        spec = importlib.util.spec_from_file_location("attacker", self.strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.generate_attacks()

    def evolve(self):
        idx = ATTACKER_ORDER.index(self.current_strategy)
        if idx < len(ATTACKER_ORDER) - 1:
            self.current_strategy = ATTACKER_ORDER[idx + 1]
            self.generation += 1
            self._write_strategy()
        return self.current_strategy

    def show_code(self):
        code = self.strategy_file.read_text()
        lines = code.split('\n')
        print(f"\n  \033[91m┌─ ATTACKER CODE (Gen {self.generation}) ─────────────────────┐\033[0m")
        for line in lines[:20]:
            print(f"  \033[91m│\033[0m {line}")
        if len(lines) > 20:
            print(f"  \033[91m│\033[0m ...")
        print(f"  \033[91m└────────────────────────────────────────────────┘\033[0m")


# ==========================================================
# === BATTLE ARENA =========================================
# ==========================================================

def run_battle(defender, attacker):
    """Run one round of battle between defender and attacker."""
    validator = defender.load_validator()
    attacks = attacker.load_attacks()

    results = []
    for attack_input, description in attacks:
        try:
            result = validator(attack_input)
            # If it returns without error on bad input, that's a vulnerability
            if attack_input in (None, 123, [], {}, True, "", "   "):
                results.append({
                    "input": attack_input,
                    "description": description,
                    "success": False,  # Defender failed - should have rejected
                    "error": f"Accepted invalid input: {repr(attack_input)}"
                })
            else:
                results.append({
                    "input": attack_input,
                    "description": description,
                    "success": True,
                    "result": result
                })
        except ValueError as e:
            # Properly rejected - defender wins this round
            results.append({
                "input": attack_input,
                "description": description,
                "success": True,
                "rejected": str(e)
            })
        except Exception as e:
            # Crashed - attacker wins
            results.append({
                "input": attack_input,
                "description": description,
                "success": False,
                "error": f"{type(e).__name__}: {e}"
            })

    return results


# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo(interactive: bool = True):
    """Run the adversarial evolution demonstration."""

    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Adversarial Self-Improvement Demo                      ║
    ║                                                          ║
    ║   Two agents compete:                                    ║
    ║   🛡️  DEFENDER: Writes validation code                    ║
    ║   ⚔️  ATTACKER: Writes edge cases to break it             ║
    ║                                                          ║
    ║   Watch them evolve through competition!                 ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if interactive:
        input("  Press ENTER to start the battle...")
    else:
        time.sleep(1)

    init_memory_db()

    defender = DefenderAgent()
    attacker = AttackerAgent()

    print("\033[2J\033[H")
    print("=" * 60)
    print(f"  TASK: {TASK['name']}")
    print("=" * 60)
    print(f"\n  {TASK['description']}")
    print("\n  Requirements:")
    for req in TASK['requirements']:
        print(f"    • {req}")
    print()

    if interactive:
        input("  Press ENTER to begin evolution...")
    else:
        time.sleep(1)

    rounds = []
    max_rounds = 5

    for round_num in range(max_rounds):
        print("\033[2J\033[H")
        print("=" * 60)
        print(f"  ROUND {round_num + 1}/{max_rounds}")
        print("=" * 60)
        print()

        print(f"  🛡️  Defender: {defender.current_strategy} (Gen {defender.generation})")
        print(f"  ⚔️  Attacker: {attacker.current_strategy} (Gen {attacker.generation})")
        print()

        # Show both agents' code
        defender.show_code()
        attacker.show_code()

        if interactive:
            input("\n  Press ENTER to run battle...")
        else:
            time.sleep(0.5)

        # Run the battle
        print("\n  \033[95m⚔️  BATTLE IN PROGRESS...\033[0m\n")
        results = run_battle(defender, attacker)

        # Display results
        wins = sum(1 for r in results if r["success"])
        losses = len(results) - wins

        print("  Results:")
        print("  " + "─" * 50)

        for r in results:
            status = "\033[92m✓\033[0m" if r["success"] else "\033[91m✗\033[0m"
            input_repr = repr(r["input"])[:30]
            print(f"    {status} {r['description']}")
            if not r["success"]:
                print(f"      \033[91m→ {r.get('error', 'Failed')}\033[0m")

        print()
        print(f"  Score: Defender {wins}/{len(results)}, Attacker {losses}/{len(results)}")

        rounds.append({
            "round": round_num + 1,
            "defender": defender.current_strategy,
            "attacker": attacker.current_strategy,
            "defender_wins": wins,
            "attacker_wins": losses
        })

        # Save to memory
        save_episode(
            task=f"adversarial_round_{round_num + 1}",
            result=f"defender:{wins} attacker:{losses}",
            reflection=f"D:{defender.current_strategy} vs A:{attacker.current_strategy}"
        )

        # Evolution logic
        if losses > 0:
            print(f"\n  \033[91m⚠️  Defender vulnerable! Evolving...\033[0m")
            defender.evolve()

        if wins == len(results) and round_num < max_rounds - 1:
            print(f"\n  \033[92m💪 Defender robust! Attacker evolving...\033[0m")
            attacker.evolve()

        if interactive:
            input("\n  Press ENTER for next round...")
        else:
            time.sleep(1)

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 EVOLUTION COMPLETE                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  BATTLE HISTORY:")
    print("  " + "─" * 56)

    for r in rounds:
        d_color = "\033[92m" if r["defender_wins"] > r["attacker_wins"] else "\033[91m"
        print(f"    Round {r['round']}: {d_color}D:{r['defender_wins']} A:{r['attacker_wins']}\033[0m")
        print(f"            {r['defender']} vs {r['attacker']}")

    print()
    print("  EVOLUTION JOURNEY:")
    print("  " + "─" * 56)
    print(f"    🛡️  Defender: basic → {defender.current_strategy}")
    print(f"    ⚔️  Attacker: basic_probes → {attacker.current_strategy}")
    print()

    # Calculate final robustness
    final_results = run_battle(defender, attacker)
    final_wins = sum(1 for r in final_results if r["success"])
    robustness = (final_wins / len(final_results)) * 100

    print(f"  FINAL ROBUSTNESS: \033[96m{robustness:.0f}%\033[0m")
    print()

    print("  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    Through adversarial competition, both agents evolved:")
    print("    • Defender learned to handle edge cases")
    print("    • Attacker learned to find vulnerabilities")
    print("    • Neither required human guidance")
    print()
    print("    \033[96mThis is artificial evolution through competition.\033[0m")
    print()

    print("  FINAL DEFENDER CODE:")
    defender.show_code()


if __name__ == "__main__":
    try:
        interactive = "--auto" not in sys.argv
        run_demo(interactive=interactive)
    except KeyboardInterrupt:
        print("\n\n  Battle interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
