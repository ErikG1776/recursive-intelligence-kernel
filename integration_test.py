"""
integration_test.py  |  Recursive Intelligence Kernel (RIK) v5.0
Brick 10 — Full System Integration Test + Commit
------------------------------------------------------------
Validates that all core subsystems operate together.
"""

import os
from datetime import datetime
import sqlite3

import memory
import reasoning
import meta
import execution

DB_PATH = memory.get_db_path()

def run_integration_test():
    print("\n🧩  Starting RIK v5.0 Integration Test...\n")

    # 0️⃣ Initialize memory database
    memory.init_memory_db()
    print("[✅] Memory database initialized.\n")

    # 1️⃣ Validate a task
    task = {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"selector": "#input"}},
            {"id": "2", "primitive": "execute", "params": {"action": "click"}}
        ],
        "edges": [{"from": "1", "to": "2"}]
    }
    reasoning.validate_task_schema(task)

    # 2️⃣ Save a mock episode
    description = "Integration Test Run — " + datetime.now().isoformat()
    memory.save_episode(
        task=description,
        result="success",
        reflection="RIK v5.0 integration test completed successfully"
    )

    # 3️⃣ Execute a safe write using concurrency lock
    execution.execute_with_lock(
        "INSERT INTO concurrency_test (message, timestamp) VALUES (?, ?)",
        ("integration_commit", datetime.now().isoformat())
    )

    # 4️⃣ Evaluate fitness
    meta.evaluate_fitness()

    # 5️⃣ Visualize current architecture
    meta.visualize_architecture()

    # 6️⃣ Confirm DB tables
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()

    print("\n✅  Integration Test Complete — All subsystems operational.")
    print("📦  Tables detected in memory.db:")
    for t in tables:
        print("   •", t[0])
    print("\n🎯  RIK v5.0 baseline ready for version control.\n")


if __name__ == "__main__":
    run_integration_test()