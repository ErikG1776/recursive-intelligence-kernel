"""
adaptive_fallback_engine.py | RIK-Fail-Safe Phase 4 – Brick 3
--------------------------------------------------------------
Adjusts future fallback strategy selection based on historical
success data from episodic_memory.
"""

import os
import sqlite3
import random

# === Correct path to main memory.db ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))

def get_strategy_weights():
    """Fetch success rates from episodic_memory to weight future choices."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT strategy,
               COUNT(*) AS uses,
               SUM(CASE WHEN actual_outcome = 'success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS success_rate
        FROM episodic_memory
        GROUP BY strategy;
    """)
    data = c.fetchall()
    conn.close()

    weights = {}
    for strategy, uses, success_rate in data:
        if strategy:
            # Basic weighting: more successes → higher weight
            weights[strategy] = round(success_rate, 3)
    return weights or {"Re-run task with safe defaults": 1.0}

def choose_strategy(possible_strategies):
    """
    Pick a strategy, favoring ones with higher historical success.
    """
    weights = get_strategy_weights()
    print("\n📚 Current learned weights:", weights)

    scored = []
    for strat in possible_strategies:
        weight = weights.get(strat, 0.5)  # default neutral weight
        scored.append((strat, weight))

    total = sum(w for _, w in scored)
    if total == 0:
        return random.choice(possible_strategies)

    # Weighted random choice
    pick = random.uniform(0, total)
    running = 0
    for strat, weight in scored:
        running += weight
        if pick <= running:
            print(f"🎯 Adaptive engine selected: {strat}")
            return strat

    # Fallback catch-all
    return possible_strategies[0]


def demo_adaptive_choice():
    """
    Demo how the adaptive engine selects a strategy based on learned memory.
    """
    test_strategies = [
        "Retry with longer wait time",
        "Re-run task with safe defaults",
        "Search with alternative selector"
    ]
    chosen = choose_strategy(test_strategies)
    print(f"\n✅ Adaptive Fallback Engine chose: {chosen}\n")


if __name__ == "__main__":
    demo_adaptive_choice()