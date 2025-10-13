"""
api_integration.py | RIK-Fail-Safe v1.0
------------------------------------------------------------
Simulated REST API / microservice integration with fallback recovery.
Shows how rik-fail-safe can wrap API calls and recover gracefully.
"""

from fallback_core import (
    diagnose,
    generate_strategies,
    simulate_counterfactuals,
    execute_best_strategy,
    explain_success,
)

def run_api_example():
    print("\n🌐 Running API Integration Example...\n")

    try:
        # Pretend we're calling an external API
        print("[📡] Sending request to external service...")
        raise TimeoutError("API request timed out after 15 s")  # Simulated failure

    except Exception as e:
        diag = diagnose(e, {"endpoint": "https://example.com/data"})
        strats = generate_strategies(diag)
        sims = simulate_counterfactuals(strats)
        result = execute_best_strategy(sims)
        explain_success(result)


if __name__ == "__main__":
    run_api_example()