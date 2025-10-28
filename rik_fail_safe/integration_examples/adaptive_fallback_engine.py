"""
adaptive_fallback_engine.py | RIK Fail-Safe Module
-------------------------------------------------
Handles strategy selection and adaptive weighting
for failed RPA tasks during demo simulations.
Now auto-creates the strategy_weights table if missing.
"""

import sqlite3, os, random

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/memory.db")


# ---------------------------------------------------------------------
# 🔹 Schema self-healing
# ---------------------------------------------------------------------
def ensure_strategy_table():
    """Create or patch the strategy_weights table if needed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS strategy_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        strategy TEXT,
        uses INTEGER DEFAULT 0,
        successes INTEGER DEFAULT 0,
        actual_outcome TEXT DEFAULT '',
        weight REAL DEFAULT 1.0
    );
    """)
    # make sure the strategy column exists
    try:
        c.execute("SELECT strategy FROM strategy_weights LIMIT 1;")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE strategy_weights ADD COLUMN strategy TEXT;")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# 🔹 Retrieve strategy performance weights
# ---------------------------------------------------------------------
def get_strategy_weights():
    ensure_strategy_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT
            strategy,
            COUNT(*) AS uses,
            SUM(CASE WHEN actual_outcome = 'success' THEN 1 ELSE 0 END) AS successes
        FROM strategy_weights
        GROUP BY strategy;
    """)
    rows = c.fetchall()
    conn.close()
    weights = {r[0]: (r[2] / max(r[1], 1)) if r[1] > 0 else 1.0 for r in rows}
    if not weights:
        # default seed weights
        weights = {"Search with alternative selector": 1.0}
    return weights


# ---------------------------------------------------------------------
# 🔹 Choose the best strategy
# ---------------------------------------------------------------------
def choose_strategy(strategies):
    weights = get_strategy_weights()
    print("\n📚 Current learned weights:", weights)
    # weighted random choice
    total = sum(weights.get(s, 1.0) for s in strategies)
    pick = random.uniform(0, total)
    current = 0
    for s in strategies:
        current += weights.get(s, 1.0)
        if current >= pick:
            return s
    return random.choice(strategies)


# ---------------------------------------------------------------------
# 🔹 Simulated counterfactuals
# ---------------------------------------------------------------------
def simulate_counterfactuals(chosen_strategies):
    """Simulate alternate strategies for demonstration."""
    results = []
    for s in chosen_strategies:
        success = random.random() > 0.3
        results.append({"strategy": s, "outcome": "success" if success else "fail"})
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO strategy_weights (strategy, actual_outcome, weight) VALUES (?, ?, ?)",
            (s, "success" if success else "fail", 1.0),
        )
        conn.commit()
        conn.close()
    return results