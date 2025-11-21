"""
meta.py | Recursive Intelligence Kernel (RIK) v5.0
Bricks 1 & 6 & 7: Rollback Mechanism + Architecture Visualization + Fitness Function
-------------------------------------------------------------------------------------
Provides:
1. Safe code modification and rollback system
2. Mermaid.js visualization of current ADL architecture
3. Architecture fitness evaluation
"""

import os
import random
from datetime import datetime
from typing import Optional
from config import setup_logging, DB_PATH
from db import get_cursor

logger = setup_logging("rik.meta")


# ==========================================================
# === Brick 1: Rollback Mechanism ==========================
# ==========================================================

def _init_modifications_table() -> None:
    """Ensure the modifications table exists."""
    with get_cursor() as cursor:
        cursor.execute("""
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


# Initialize on module load
_init_modifications_table()


def apply_modification(
    component_path: str,
    new_code: str,
    description: str = ""
) -> int:
    """
    Stores the current code for rollback, applies a new code snippet,
    and logs the modification in the database.

    Args:
        component_path: Path to the file to modify.
        new_code: New code content to write.
        description: Description of the change.

    Returns:
        The modification ID.

    Raises:
        FileNotFoundError: If component doesn't exist.
    """
    if not os.path.exists(component_path):
        raise FileNotFoundError(f"Component {component_path} not found")

    with open(component_path, "r") as f:
        original_code = f.read()

    with open(component_path, "w") as f:
        f.write(new_code)

    with get_cursor() as cursor:
        cursor.execute("""
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
        mod_id = cursor.lastrowid

    logger.info(f"Modification applied to {component_path} (id={mod_id})")
    return mod_id


def rollback(mod_id: int) -> str:
    """
    Rolls back a modification by ID, restoring the original code.

    Args:
        mod_id: The modification ID to rollback.

    Returns:
        The component path that was rolled back.

    Raises:
        ValueError: If modification ID not found.
    """
    with get_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT component, rollback_code FROM modifications WHERE id = ?",
            (mod_id,)
        )
        row = cursor.fetchone()

    if not row:
        raise ValueError(f"No modification found with ID {mod_id}")

    component_path, rollback_code = row
    with open(component_path, "w") as f:
        f.write(rollback_code)

    logger.info(f"Rolled back modification {mod_id} on {component_path}")
    return component_path


def get_modification_history(limit: int = 10) -> list[dict]:
    """Get recent modifications from the database."""
    with get_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT * FROM modifications ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "component": row[1],
                "description": row[2],
                "timestamp": row[7] if len(row) > 7 else None
            }
            for row in rows
        ]


# ==========================================================
# === Brick 6: Architecture Visualization ==================
# ==========================================================

def visualize_architecture(
    adl_schema: Optional[dict] = None,
    save_path: str = "architecture_diagram.mmd"
) -> str:
    """
    Converts an ADL-like dictionary into a Mermaid diagram definition and saves it.
    If no schema is provided, generates a default RIK v5.0 architecture diagram.

    Args:
        adl_schema: Architecture definition as {source: [targets]} dict.
        save_path: Path to save the Mermaid diagram.

    Returns:
        The Mermaid diagram string.
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
        # Sanitize node names for Mermaid
        safe_source = source.replace("-", "_").replace(" ", "_")
        if not targets:
            mermaid_lines.append(f"    {safe_source}[{source}]")
        else:
            for target in targets:
                safe_target = target.replace("-", "_").replace(" ", "_")
                mermaid_lines.append(
                    f"    {safe_source}[{source}] --> {safe_target}[{target}]"
                )

    diagram = "\n".join(mermaid_lines)

    with open(save_path, "w") as f:
        f.write(diagram)

    logger.info(f"Mermaid architecture diagram generated: {save_path}")
    return diagram


# ==========================================================
# === Brick 7: Fitness Function ============================
# ==========================================================

def evaluate_fitness() -> dict:
    """
    Simulates architecture performance metrics and stores
    a fitness score (efficiency + robustness) / 2 in the DB.

    Returns:
        Dictionary with efficiency, robustness, and fitness_score.
    """
    # Simulated performance metrics (0-1 range)
    efficiency = round(random.uniform(0.8, 1.0), 3)
    robustness = round(random.uniform(0.8, 1.0), 3)
    fitness_score = round((efficiency + robustness) / 2, 3)

    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS architecture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT,
                efficiency REAL,
                robustness REAL,
                fitness_score REAL,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO architecture (version, efficiency, robustness, fitness_score, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "v5.0",
            efficiency,
            robustness,
            fitness_score,
            datetime.utcnow().isoformat()
        ))

    result = {
        "efficiency": efficiency,
        "robustness": robustness,
        "fitness_score": fitness_score
    }

    logger.info(
        f"Fitness evaluated: efficiency={efficiency}, "
        f"robustness={robustness}, score={fitness_score}"
    )
    return result


def get_fitness_history(limit: int = 10) -> list[dict]:
    """Get recent fitness evaluations."""
    with get_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT * FROM architecture ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "version": row[1],
                "efficiency": row[2],
                "robustness": row[3],
                "fitness_score": row[4],
                "timestamp": row[5]
            }
            for row in rows
        ]


# ==========================================================
# === Manual Test Runner ===================================
# ==========================================================
if __name__ == "__main__":
    logger.info(f"Rollback system ready. Database at: {DB_PATH}")
    visualize_architecture()
    result = evaluate_fitness()
    print(f"Fitness: {result}")
