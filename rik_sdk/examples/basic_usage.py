"""
RIK SDK - Basic Usage Examples
===============================

Simple examples demonstrating how to use the RIK Python SDK.
"""

from rik_sdk import RIKClient
from rik_sdk.exceptions import RIKError, RIKConnectionError


def example_health_check():
    """Check if RIK API is healthy and ready."""
    print("=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    # Simple liveness check
    if client.is_alive():
        print("✓ API is alive")
    else:
        print("✗ API is not responding")
        return

    # Readiness check
    if client.is_ready():
        print("✓ API is ready to handle requests")
    else:
        print("⚠ API is not ready (database or other issues)")

    # Detailed health status
    health = client.get_health()
    print(f"\nHealth Status: {health.status}")
    print(f"Subsystems:")
    for system, status in health.subsystems.items():
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {system}")

    # Version info
    version = client.get_version()
    print(f"\nVersion: {version['version']}")
    print(f"Environment: {version['environment']}")


def example_get_metrics():
    """Get performance metrics."""
    print("\n" + "=" * 60)
    print("Example 2: Performance Metrics")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    metrics = client.get_metrics()
    print(f"Efficiency: {metrics.efficiency:.1%}")
    print(f"Total Episodes: {metrics.total_episodes}")
    print(f"Successful: {metrics.successful_episodes}")
    print(f"Failed: {metrics.failed_episodes}")
    print(f"Avg Processing Time: {metrics.avg_processing_time_seconds:.3f}s")


def example_run_task():
    """Execute a reasoning task."""
    print("\n" + "=" * 60)
    print("Example 3: Run Reasoning Task")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    task = "Analyze a scenario where an invoice has a missing PO number"
    print(f"Task: {task}")

    result = client.run_task(task)
    print(f"\nResult: {result.result}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Processing Time: {result.processing_time_seconds:.3f}s")


def example_with_api_key():
    """Use API with authentication."""
    print("\n" + "=" * 60)
    print("Example 4: Authenticated Request")
    print("=" * 60)

    # Initialize client with API key
    client = RIKClient(
        base_url="http://localhost:8000",
        api_key="your-api-key-here",  # Replace with actual key
        timeout=60.0,  # 60 second timeout
        max_retries=5   # Retry up to 5 times
    )

    print(f"Client configured: {client}")

    # All requests will now include API key in headers
    if client.is_alive():
        print("✓ Authenticated request successful")


def example_context_manager():
    """Use RIK client as a context manager for automatic cleanup."""
    print("\n" + "=" * 60)
    print("Example 5: Context Manager (Auto Cleanup)")
    print("=" * 60)

    with RIKClient("http://localhost:8000") as client:
        health = client.get_health()
        print(f"Health: {health.status}")
        # Session automatically closed when exiting context

    print("✓ Client session automatically closed")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    client = RIKClient("http://localhost:9999")  # Wrong port

    try:
        client.is_alive()
    except RIKConnectionError as e:
        print(f"✓ Caught connection error: {e.message}")
        print(f"  URL attempted: {e.url}")
    except RIKError as e:
        print(f"Other RIK error: {e}")


if __name__ == "__main__":
    print("\n🚀 RIK SDK - Basic Usage Examples\n")

    try:
        example_health_check()
        example_get_metrics()
        example_run_task()
        example_with_api_key()
        example_context_manager()
        example_error_handling()

        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("=" * 60)

    except RIKConnectionError:
        print("\n❌ ERROR: Cannot connect to RIK API at http://localhost:8000")
        print("   Make sure the API is running:")
        print("   $ python3 rik_api.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
