"""
meta.py | Recursive Intelligence Kernel (RIK) v5.0
Bricks 1, 6 & 7: Rollback Mechanism + Architecture Visualization + Fitness Evaluation
-------------------------------------------------------------------------------------
Provides:
1. Safe code modification and rollback system
2. Mermaid.js visualization of current ADL architecture
3. Fitness evaluation for system performance metrics
"""

import os
import sqlite3
import random
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "memory.db")

# ==========================================================
# === Brick 1: Rollback Mechanism ==========================
# ==========================================================

def _init_db():
    """Ensure the modifications table exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component TEXT,
            change_description TEXT,
            rollback_code TEXT,
            applied_code TEXT,
            performance_before REAL,
            performance_after REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

_init_db()


def apply_modification(component_path: str, new_code: str, description: str = ""):
    """
    Stores the current code for rollback, applies a new code snippet,
    and logs the modification in the database.
    """
    if not os.path.exists(component_path):
        raise FileNotFoundError(f"Component {component_path} not found")

    with open(component_path, "r") as f:
        original_code = f.read()

    with open(component_path, "w") as f:
        f.write(new_code)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO modifications (
            component, change_description, rollback_code, applied_code,
            performance_before, performance_after, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        component_path,
        description,
        original_code,
        new_code,
        None,
        None,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

    print(f"[✅] Modification applied to {component_path} and logged.")


def rollback(mod_id: int):
    """
    Rolls back a modification by ID, restoring the original code.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT component, rollback_code FROM modifications WHERE id = ?", (mod_id,))
    row = c.fetchone()
    if not row:
        raise ValueError(f"No modification found with ID {mod_id}")

    component_path, rollback_code = row
    with open(component_path, "w") as f:
        f.write(rollback_code)

    conn.close()
    print(f"[🔁] Rolled back modification {mod_id} on {component_path}.")


# ==========================================================
# === Brick 6: Architecture Visualization =================
# ==========================================================

def visualize_architecture(adl_schema: dict = None, save_path: str = "architecture_diagram.mmd"):
    """
    Converts an ADL-like dictionary into a Mermaid diagram definition and saves it.
    If no schema is provided, generates a default RIK v5.0 architecture diagram.
    """
    if adl_schema is None:
        adl_schema = {
            "Meta-Controller": ["Reasoning Engine"],
            "Reasoning Engine": ["Memory Systems", "Execution Layer"],
            "Memory Systems": ["Fallback System"],
            "Execution Layer": ["Fallback System"],
            "Fallback System": []
        }

    mermaid_lines = ["graph TD"]
    for source, targets in adl_schema.items():
        if not targets:
            mermaid_lines.append(f"    {source}")
        else:
            for target in targets:
                mermaid_lines.append(f"    {source} --> {target}")

    diagram = "\n".join(mermaid_lines)

    with open(save_path, "w") as f:
        f.write(diagram)

    print(f"[✅] Mermaid architecture diagram generated → {save_path}")
    print("Preview:\n" + diagram)
    return diagram


# ==========================================================
# === Brick 7: Fitness Evaluation ==========================
# ==========================================================

def evaluate_fitness():
    """
    Simulates architecture performance metrics and stores
    a fitness score (efficiency + robustness) / 2 in the DB.
    """
    efficiency = round(random.uniform(0.8, 1.0), 3)
    robustness = round(random.uniform(0.8, 1.0), 3)
    fitness_score = round((efficiency + robustness) / 2, 3)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS architecture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT,
            efficiency REAL,
            robustness REAL,
            fitness_score REAL,
            timestamp TEXT
        )
    """)
    c.execute("""
        INSERT INTO architecture (version, efficiency, robustness, fitness_score, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "v5.0",
        efficiency,
        robustness,
        fitness_score,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

    print(f"[📈] Efficiency: {efficiency} | Robustness: {robustness} | Fitness Score: {fitness_score}")
    return fitness_score


# ==========================================================
# === Manual Test Runner ===================================
# ==========================================================
if __name__ == "__main__":
    print("[ℹ️] Rollback system ready. Database verified at:", DB_PATH)
    visualize_architecture()
    evaluate_fitness()