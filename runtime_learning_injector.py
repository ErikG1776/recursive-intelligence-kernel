"""
runtime_learning_injector.py | RIK-Fail-Safe Phase 4 – Brick 6
-----------------------------------------------------------------
Injects learned strategy weights from episodic_memory directly
into live agent runs so that each new task adapts in real time.
"""

import os
import sqlite3
from memory import get_db_path
from rik_fail_safe.fallback_core import (
    diagnose,
    generate_strategies,
    simulate_counterfactuals,
    execute_best_strategy,
    explain_success,
)
from rik_fail_safe.integration_examples.adaptive_fallback_engine import choose_strategy

# === Correct path to main memory.db ===
DB_PATH = get_db_path()
def get_learned_weights():
    """Retrieve learned success rates for all strategies."""
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
    return {r[0]: round(r[1], 3) for r in rows if r[0]} or {"Re-run task with safe defaults": 1.0}

def rik_live_run(task_description: str, simulate_failure: bool = True):
    """
    Simulates a live agent task that automatically references
    past learning before deciding its fallback plan.
    """
    print("\n🧩 Running RIK-Fail-Safe Live Task with Runtime Learning Injection...\n")
    learned = get_learned_weights()
    print(f"[🧠] Loaded learned strategy weights: {learned}")

    try:
        print(f"[⚙️] Executing task: {task_description}")
        if simulate_failure:
            raise Exception("Simulated live failure: ElementNotFound")
        print("[✅] Task completed successfully, no fallback needed.")
    except Exception as e:
        print(f"[⚠️] Exception detected during '{task_description}': {e}")

        diag = diagnose(e, {"step": task_description})
        strategies = list(learned.keys())
        chosen = choose_strategy(strategies)  # Uses learned weights dynamically
        sims = simulate_counterfactuals([chosen])
        result = execute_best_strategy(sims)
        explain_success(result)

    print("\n[🧠] Runtime Learning Injection complete.\n")

if __name__ == "__main__":
    rik_live_run("Selenium live web test with adaptive learning")