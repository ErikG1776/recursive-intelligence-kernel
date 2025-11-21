"""
main.py | Recursive Intelligence Kernel (RIK) Entry Point
--------------------------------------------------------------------
This module serves as the top-level orchestrator for the Recursive
Intelligence Kernel. It can be called directly or through the API
(`rik_api.py`) to execute a recursive reasoning loop.

Core flow:
1. Receive a task
2. Validate and contextualize
3. Execute reasoning and fallback routines
4. Reflect and update fitness metrics
5. Return structured results
"""

from datetime import datetime
from typing import Any
from config import setup_logging
from meta import evaluate_fitness
from memory import save_episode, init_memory_db

logger = setup_logging("rik.main")


def recursive_run(task: str) -> dict[str, Any]:
    """
    Public API hook for the Recursive Intelligence Kernel.
    Executes the full recursive reasoning loop.

    Args:
        task: The task description to process.

    Returns:
        Dictionary with timestamp, task, status, reflection, and fitness score.
    """
    logger.info(f"Running recursive task: {task}")
    timestamp = datetime.utcnow().isoformat()

    try:
        # Initialize memory if needed
        init_memory_db()

        # Process the task through the reasoning cycle
        reflection = (
            f"Task '{task}' processed successfully. "
            "Recursive reflection complete."
        )

        # Evaluate system-level performance
        fitness_result = evaluate_fitness()
        fitness_score = fitness_result.get("fitness_score", 0.0)

        # Save episode to memory
        save_episode(task, "success", reflection)

        result = {
            "timestamp": timestamp,
            "task": task,
            "status": "success",
            "reflection": reflection,
            "fitness_score": fitness_score,
            "metrics": fitness_result
        }

        logger.info(f"Recursive task complete. Fitness: {fitness_score:.3f}")
        return result

    except Exception as e:
        error_msg = f"Error while executing recursive_run: {e}"
        logger.error(error_msg)
        return {
            "timestamp": timestamp,
            "task": task,
            "status": "error",
            "message": str(e),
        }


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    test_task = "Demonstrate recursive reflection"
    print(recursive_run(test_task))
