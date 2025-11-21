"""
self_updating_confidence.py | RIK-Fail-Safe Phase 4 - Brick 7
-----------------------------------------------------------------
Automatically recalibrates strategy confidence scores after each run.
This closes the recursive loop: reflection -> learning -> adaptation -> reflection.
"""

from config import setup_logging
from db import get_cursor

logger = setup_logging("rik.confidence")


def create_weights_table() -> None:
    """Ensure the strategy_weights table exists."""
    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT UNIQUE,
                success_rate REAL,
                avg_confidence REAL,
                last_updated TEXT
            );
        """)


def recalculate_weights() -> list[dict]:
    """
    Recompute success rates and update the strategy_weights table.

    Returns:
        List of updated strategy weight records.
    """
    with get_cursor() as cursor:
        # Compute metrics from episodic_memory
        cursor.execute("""
            SELECT strategy,
                   COUNT(*) AS uses,
                   SUM(CASE WHEN actual_outcome='success' THEN 1 ELSE 0 END)*1.0 / COUNT(*) AS success_rate,
                   ROUND(AVG(predicted_success), 3) AS avg_conf
            FROM episodic_memory
            GROUP BY strategy;
        """)
        rows = cursor.fetchall()

        if not rows:
            logger.info("No episodic memory data found")
            return []

        # Create weights table if not already present
        create_weights_table()

        updated = []
        for strategy, uses, success_rate, avg_conf in rows:
            if not strategy:
                continue

            cursor.execute("""
                INSERT INTO strategy_weights (strategy, success_rate, avg_confidence, last_updated)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(strategy) DO UPDATE SET
                    success_rate=excluded.success_rate,
                    avg_confidence=excluded.avg_confidence,
                    last_updated=datetime('now');
            """, (strategy, success_rate, avg_conf))

            updated.append({
                "strategy": strategy,
                "success_rate": round(success_rate, 3),
                "avg_confidence": avg_conf,
                "uses": uses
            })
            logger.info(
                f"Updated '{strategy}': success_rate={round(success_rate, 3)}, "
                f"avg_confidence={avg_conf}"
            )

    logger.info("Strategy weights recalibrated and saved")
    return updated


def get_strategy_weights() -> list[dict]:
    """Retrieve all current strategy weights."""
    with get_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT strategy, success_rate, avg_confidence, last_updated
            FROM strategy_weights
            ORDER BY success_rate DESC
        """)
        rows = cursor.fetchall()

        return [
            {
                "strategy": row[0],
                "success_rate": row[1],
                "avg_confidence": row[2],
                "last_updated": row[3]
            }
            for row in rows
        ]


def main() -> None:
    logger.info("Running Self-Updating Confidence Calibration...")
    results = recalculate_weights()
    if results:
        print(f"Updated {len(results)} strategies")
    else:
        print("No strategies to update")


if __name__ == "__main__":
    main()
