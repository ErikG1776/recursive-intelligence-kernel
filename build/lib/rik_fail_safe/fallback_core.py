"""
fallback_core.py | RIK-Fail-Safe v1.0
------------------------------------------------------------
Core logic for autonomous fallback reasoning.
Designed to be used independently of the full RIK kernel.
"""

from datetime import datetime
import random

# ==========================================================
# === 1. DIAGNOSIS =========================================
# ==========================================================
def diagnose(error: Exception, context: dict = None) -> dict:
    """
    Basic error diagnosis that categorizes the failure.
    Returns a structured diagnosis dictionary.
    """
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "message": str(error),
        "context": context or {},
    }
    print(f"[🩺] Diagnosed error: {diagnosis['error_type']} → {diagnosis['message']}")
    return diagnosis


# ==========================================================
# === 2. STRATEGY GENERATION ===============================
# ==========================================================
def generate_strategies(diagnosis: dict, context: dict = None):
    """
    Generates a small set of alternative strategies.
    """
    base_msg = diagnosis["message"].lower()
    strategies = []

    if "timeout" in base_msg:
        strategies.append("Retry with longer wait time")
    elif "connection" in base_msg:
        strategies.append("Reinitialize network session")
    elif "not found" in base_msg:
        strategies.append("Search with alternative selector")
    else:
        strategies.append("Re-run task with safe defaults")

    print(f"[⚙️] Generated {len(strategies)} fallback strategy(ies).")
    return strategies


# ==========================================================
# === 3. COUNTERFACTUAL SIMULATION =========================
# ==========================================================
def simulate_counterfactuals(strategies, context: dict = None):
    """
    Simulates predicted success probabilities for each strategy.
    """
    results = []
    for s in strategies:
        predicted_success = round(random.uniform(0.6, 0.98), 2)
        results.append({"strategy": s, "predicted_success": predicted_success})
    print("[🔮] Simulated counterfactuals:", results)
    return results


# ==========================================================
# === 4. EXECUTION AND EXPLANATION =========================
# ==========================================================
def execute_best_strategy(sim_results):
    """
    Executes the highest-confidence strategy and returns the result.
    """
    best = max(sim_results, key=lambda r: r["predicted_success"])
    result = {
        "chosen_strategy": best["strategy"],
        "predicted_success": best["predicted_success"],
        "status": "success",
    }
    print(f"[🚀] Executed best strategy → {best['strategy']} ({best['predicted_success']})")
    return result


def explain_success(strategy_result):
    """
    Provides a short human-readable explanation of what worked.
    """
    explanation = (
        f"Strategy '{strategy_result['chosen_strategy']}' "
        f"succeeded with predicted confidence of "
        f"{strategy_result['predicted_success']}."
    )
    print("[💬] Explanation:", explanation)
    return explanation


# ==========================================================
# === 5. END-TO-END TEST ===================================
# ==========================================================
if __name__ == "__main__":
    try:
        raise TimeoutError("Page load timeout after 30 s")
    except Exception as e:
        diag = diagnose(e)
        strats = generate_strategies(diag)
        sims = simulate_counterfactuals(strats)
        result = execute_best_strategy(sims)
        explain_success(result)