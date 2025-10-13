from rik_sdk.client import RIKClient

rik = RIKClient()

print("\n=== Running Recursive Task ===")
print(rik.run_task("Demonstrate recursive reflection"))

print("\n=== Current Metrics ===")
print(rik.get_metrics())

print("\n=== Recent Memory ===")
print(rik.get_memory())