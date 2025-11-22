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

import sys
from datetime import datetime, timezone
from meta import evaluate_fitness
from memory import save_episode, retrieve_context, init_memory_db
from reasoning import create_abstractions
from rik_fail_safe.fallback_core import (
    diagnose,
    generate_strategies,
    simulate_counterfactuals,
    execute_best_strategy,
)


def recursive_run(task: str):
    """
    Public API hook for the Recursive Intelligence Kernel.
    Executes the full recursive reasoning loop.
    """
    print(f"[RIK] Running recursive task: {task}")
    timestamp = datetime.now(timezone.utc).isoformat()

    # Ensure database is initialized
    init_memory_db()

    try:
        # 1. Retrieve context from prior episodes
        context = retrieve_context(task)
        print(f"[RIK] Retrieved context: {context}")

        # 2. Attempt to create abstractions from past episodes
        create_abstractions()

        # 3. Simulate task execution (in real use, this would be actual work)
        # For demonstration, we simulate potential failures
        task_success = True
        fallback_used = False

        # Simulate failure scenario for demonstration
        if "fail" in task.lower() or "error" in task.lower():
            task_success = False
            try:
                raise Exception(f"Simulated failure during task: {task}")
            except Exception as e:
                # 4. Engage fallback system
                diag = diagnose(e, {"task": task})
                strategies = generate_strategies(diag, context)
                sims = simulate_counterfactuals(strategies, context)
                result = execute_best_strategy(sims)
                fallback_used = True
                task_success = result["status"] == "success"

        # 5. Generate reflection
        if task_success:
            reflection = (
                f"Task '{task}' processed successfully. "
                f"{'Fallback recovery engaged. ' if fallback_used else ''}"
                "Recursive reflection complete."
            )
        else:
            reflection = f"Task '{task}' failed after fallback attempts."

        # 6. Save episode to memory
        save_episode(task, "success" if task_success else "failure", reflection)

        # 7. Evaluate system-level performance
        fitness_score = evaluate_fitness()

        result = {
            "timestamp": timestamp,
            "task": task,
            "status": "success" if task_success else "failure",
            "reflection": reflection,
            "fitness_score": fitness_score,
            "context_used": context,
            "fallback_engaged": fallback_used,
        }

        print(f"[RIK] Recursive task complete. Fitness: {fitness_score:.3f}")
        return result

    except Exception as e:
        error_msg = f"Error while executing recursive_run: {e}"
        print(f"[RIK-ERROR] {error_msg}")

        # Still save the failed episode for learning
        save_episode(task, "error", str(e))

        return {
            "timestamp": timestamp,
            "task": task,
            "status": "error",
            "message": str(e),
        }


if __name__ == "__main__":
    # Accept task from command line or use default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Demonstrate recursive reflection"

    print(recursive_run(task))
