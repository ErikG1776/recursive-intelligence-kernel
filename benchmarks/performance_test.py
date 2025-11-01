"""
RIK Performance Benchmark Suite
================================

Measures and reports RIK's performance characteristics:
- Throughput (requests/second)
- Latency (p50, p95, p99)
- Concurrent request handling
- Memory usage
- Database performance

Usage:
    python3 benchmarks/performance_test.py

Results saved to: benchmarks/results/
"""

import time
import statistics
import json
import psutil
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests

# Benchmark configuration
BENCHMARK_CONFIG = {
    "api_url": os.getenv("RIK_BENCHMARK_URL", "http://localhost:8000"),
    "api_key": os.getenv("RIK_BENCHMARK_API_KEY", None),
    "warmup_requests": 10,
    "test_requests": 100,
    "concurrent_workers": 10,
    "timeout_seconds": 30,
}


# ============================================================================
# BENCHMARK UTILITIES
# ============================================================================

def get_memory_usage_mb():
    """Get current process memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def make_request(endpoint, method="GET", json_data=None, headers=None):
    """
    Make a timed HTTP request.

    Returns:
        dict with 'duration', 'status_code', 'success', 'error'
    """
    url = f"{BENCHMARK_CONFIG['api_url']}{endpoint}"

    if headers is None:
        headers = {}

    if BENCHMARK_CONFIG['api_key']:
        headers['X-API-Key'] = BENCHMARK_CONFIG['api_key']

    start = time.time()

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=BENCHMARK_CONFIG['timeout_seconds'])
        elif method == "POST":
            response = requests.post(url, json=json_data, headers=headers, timeout=BENCHMARK_CONFIG['timeout_seconds'])
        else:
            raise ValueError(f"Unsupported method: {method}")

        duration = time.time() - start

        return {
            "duration": duration,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "error": None,
            "response_size": len(response.content)
        }

    except Exception as e:
        duration = time.time() - start
        return {
            "duration": duration,
            "status_code": None,
            "success": False,
            "error": str(e),
            "response_size": 0
        }


def calculate_percentiles(values):
    """Calculate percentiles from a list of values"""
    if not values:
        return {}

    sorted_values = sorted(values)
    n = len(sorted_values)

    return {
        "min": sorted_values[0],
        "p25": sorted_values[int(n * 0.25)],
        "p50": sorted_values[int(n * 0.50)],
        "p75": sorted_values[int(n * 0.75)],
        "p95": sorted_values[int(n * 0.95)] if n > 20 else sorted_values[-1],
        "p99": sorted_values[int(n * 0.99)] if n > 100 else sorted_values[-1],
        "max": sorted_values[-1],
        "mean": statistics.mean(values),
        "stddev": statistics.stdev(values) if len(values) > 1 else 0
    }


# ============================================================================
# BENCHMARK TESTS
# ============================================================================

def benchmark_health_endpoint():
    """
    Benchmark: Health endpoint performance
    Simple GET request with minimal processing
    """
    print("\n" + "=" * 60)
    print("BENCHMARK 1: Health Endpoint (/health/live)")
    print("=" * 60)

    results = []

    # Warmup
    print(f"Warmup: {BENCHMARK_CONFIG['warmup_requests']} requests...")
    for _ in range(BENCHMARK_CONFIG['warmup_requests']):
        make_request("/health/live")

    # Test
    print(f"Testing: {BENCHMARK_CONFIG['test_requests']} requests...")
    start_time = time.time()

    for i in range(BENCHMARK_CONFIG['test_requests']):
        result = make_request("/health/live")
        results.append(result)

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{BENCHMARK_CONFIG['test_requests']}")

    total_time = time.time() - start_time

    # Calculate metrics
    durations = [r['duration'] * 1000 for r in results if r['success']]  # Convert to ms
    success_rate = sum(1 for r in results if r['success']) / len(results)
    throughput = len(results) / total_time

    percentiles = calculate_percentiles(durations)

    print("\n📊 Results:")
    print(f"  Total requests: {len(results)}")
    print(f"  Success rate: {success_rate:.1%}")
    print(f"  Throughput: {throughput:.1f} req/sec")
    print(f"\n  Latency (ms):")
    print(f"    Min: {percentiles['min']:.2f}")
    print(f"    P50: {percentiles['p50']:.2f}")
    print(f"    P95: {percentiles['p95']:.2f}")
    print(f"    P99: {percentiles['p99']:.2f}")
    print(f"    Max: {percentiles['max']:.2f}")
    print(f"    Mean: {percentiles['mean']:.2f} ± {percentiles['stddev']:.2f}")

    return {
        "name": "health_endpoint",
        "total_requests": len(results),
        "success_rate": success_rate,
        "throughput_per_sec": throughput,
        "latency_ms": percentiles
    }


def benchmark_invoice_processing():
    """
    Benchmark: Invoice processing with exceptions
    More complex processing with RIK reasoning
    """
    print("\n" + "=" * 60)
    print("BENCHMARK 2: Invoice Processing (/process_invoice)")
    print("=" * 60)

    # Sample invoice data (missing PO - triggers RIK reasoning)
    invoice_data = {
        "invoice_number": "BENCH-001",
        "vendor_name": "Acme Corporation",
        "amount": 4500.00,
        "date": "11/01/2024",
        "po_number": ""  # Missing - triggers exception handling
    }

    payload = {
        "pdf_content": json.dumps(invoice_data),
        "invoice_id": "BENCH-001"
    }

    results = []

    # Warmup
    print(f"Warmup: {BENCHMARK_CONFIG['warmup_requests']} requests...")
    for _ in range(BENCHMARK_CONFIG['warmup_requests']):
        make_request("/process_invoice", method="POST", json_data=payload)

    # Test
    print(f"Testing: {BENCHMARK_CONFIG['test_requests']} requests...")
    start_time = time.time()

    for i in range(BENCHMARK_CONFIG['test_requests']):
        result = make_request("/process_invoice", method="POST", json_data=payload)
        results.append(result)

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{BENCHMARK_CONFIG['test_requests']}")

    total_time = time.time() - start_time

    # Calculate metrics
    durations = [r['duration'] * 1000 for r in results if r['success']]
    success_rate = sum(1 for r in results if r['success']) / len(results)
    throughput = len(results) / total_time

    percentiles = calculate_percentiles(durations)

    print("\n📊 Results:")
    print(f"  Total requests: {len(results)}")
    print(f"  Success rate: {success_rate:.1%}")
    print(f"  Throughput: {throughput:.1f} req/sec")
    print(f"\n  Latency (ms):")
    print(f"    Min: {percentiles['min']:.2f}")
    print(f"    P50: {percentiles['p50']:.2f}")
    print(f"    P95: {percentiles['p95']:.2f}")
    print(f"    P99: {percentiles['p99']:.2f}")
    print(f"    Max: {percentiles['max']:.2f}")
    print(f"    Mean: {percentiles['mean']:.2f} ± {percentiles['stddev']:.2f}")

    return {
        "name": "invoice_processing",
        "total_requests": len(results),
        "success_rate": success_rate,
        "throughput_per_sec": throughput,
        "latency_ms": percentiles
    }


def benchmark_concurrent_load():
    """
    Benchmark: Concurrent request handling
    Tests RIK under concurrent load
    """
    print("\n" + "=" * 60)
    print("BENCHMARK 3: Concurrent Load")
    print(f"Workers: {BENCHMARK_CONFIG['concurrent_workers']}")
    print("=" * 60)

    invoice_data = {
        "invoice_number": "CONC-001",
        "vendor_name": "Acme Corporation",
        "amount": 3000.00,
        "date": "11/01/2024",
        "po_number": "PO-12345"
    }

    payload = {
        "pdf_content": json.dumps(invoice_data),
        "invoice_id": "CONC-001"
    }

    results = []
    start_time = time.time()

    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=BENCHMARK_CONFIG['concurrent_workers']) as executor:
        futures = [
            executor.submit(make_request, "/process_invoice", "POST", payload)
            for _ in range(BENCHMARK_CONFIG['test_requests'])
        ]

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)

            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/{BENCHMARK_CONFIG['test_requests']}")

    total_time = time.time() - start_time

    # Calculate metrics
    durations = [r['duration'] * 1000 for r in results if r['success']]
    success_rate = sum(1 for r in results if r['success']) / len(results)
    throughput = len(results) / total_time

    percentiles = calculate_percentiles(durations)

    print("\n📊 Results:")
    print(f"  Total requests: {len(results)}")
    print(f"  Success rate: {success_rate:.1%}")
    print(f"  Throughput: {throughput:.1f} req/sec")
    print(f"  Concurrency: {BENCHMARK_CONFIG['concurrent_workers']} workers")
    print(f"\n  Latency (ms):")
    print(f"    Min: {percentiles['min']:.2f}")
    print(f"    P50: {percentiles['p50']:.2f}")
    print(f"    P95: {percentiles['p95']:.2f}")
    print(f"    P99: {percentiles['p99']:.2f}")
    print(f"    Max: {percentiles['max']:.2f}")
    print(f"    Mean: {percentiles['mean']:.2f} ± {percentiles['stddev']:.2f}")

    return {
        "name": "concurrent_load",
        "total_requests": len(results),
        "success_rate": success_rate,
        "throughput_per_sec": throughput,
        "concurrent_workers": BENCHMARK_CONFIG['concurrent_workers'],
        "latency_ms": percentiles
    }


def benchmark_memory_usage():
    """
    Benchmark: Memory usage over time
    """
    print("\n" + "=" * 60)
    print("BENCHMARK 4: Memory Usage")
    print("=" * 60)

    invoice_data = {
        "invoice_number": "MEM-001",
        "vendor_name": "Acme Corporation",
        "amount": 2500.00,
        "date": "11/01/2024",
        "po_number": "PO-99999"
    }

    payload = {
        "pdf_content": json.dumps(invoice_data),
        "invoice_id": "MEM-001"
    }

    memory_samples = []
    initial_memory = get_memory_usage_mb()

    print(f"  Initial memory: {initial_memory:.2f} MB")
    print(f"  Processing {BENCHMARK_CONFIG['test_requests']} requests...")

    for i in range(BENCHMARK_CONFIG['test_requests']):
        make_request("/process_invoice", method="POST", json_data=payload)

        if i % 10 == 0:
            current_memory = get_memory_usage_mb()
            memory_samples.append(current_memory)

    final_memory = get_memory_usage_mb()
    memory_increase = final_memory - initial_memory

    print(f"\n📊 Results:")
    print(f"  Initial memory: {initial_memory:.2f} MB")
    print(f"  Final memory: {final_memory:.2f} MB")
    print(f"  Increase: {memory_increase:.2f} MB ({memory_increase/initial_memory * 100:.1f}%)")
    print(f"  Peak memory: {max(memory_samples):.2f} MB")
    print(f"  Memory per request: {memory_increase / BENCHMARK_CONFIG['test_requests'] * 1024:.2f} KB")

    return {
        "name": "memory_usage",
        "initial_mb": initial_memory,
        "final_mb": final_memory,
        "increase_mb": memory_increase,
        "increase_percent": memory_increase / initial_memory * 100,
        "peak_mb": max(memory_samples),
        "per_request_kb": memory_increase / BENCHMARK_CONFIG['test_requests'] * 1024
    }


# ============================================================================
# MAIN BENCHMARK RUNNER
# ============================================================================

def run_all_benchmarks():
    """Run all benchmark suites and generate report"""

    print("\n" + "█" * 60)
    print("  RIK Performance Benchmark Suite")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("█" * 60)

    print(f"\nConfiguration:")
    print(f"  API URL: {BENCHMARK_CONFIG['api_url']}")
    print(f"  Test requests: {BENCHMARK_CONFIG['test_requests']}")
    print(f"  Concurrent workers: {BENCHMARK_CONFIG['concurrent_workers']}")
    print(f"  Warmup requests: {BENCHMARK_CONFIG['warmup_requests']}")

    # Check if API is reachable
    try:
        response = requests.get(f"{BENCHMARK_CONFIG['api_url']}/health/live", timeout=5)
        if response.status_code != 200:
            print(f"\n❌ ERROR: API not responding at {BENCHMARK_CONFIG['api_url']}")
            print("   Start the API with: python3 rik_api.py")
            return
    except Exception as e:
        print(f"\n❌ ERROR: Cannot reach API at {BENCHMARK_CONFIG['api_url']}")
        print(f"   {str(e)}")
        print("   Start the API with: python3 rik_api.py")
        return

    print("\n✅ API is reachable, starting benchmarks...\n")

    # Run benchmarks
    results = []

    try:
        results.append(benchmark_health_endpoint())
        results.append(benchmark_invoice_processing())
        results.append(benchmark_concurrent_load())
        results.append(benchmark_memory_usage())
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        return
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    for result in results:
        if "throughput_per_sec" in result:
            print(f"\n{result['name'].replace('_', ' ').title()}:")
            print(f"  Throughput: {result['throughput_per_sec']:.1f} req/sec")
            print(f"  P50 latency: {result['latency_ms']['p50']:.2f} ms")
            print(f"  P95 latency: {result['latency_ms']['p95']:.2f} ms")
            print(f"  Success rate: {result['success_rate']:.1%}")

    # Save results
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"benchmark_{timestamp}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "config": BENCHMARK_CONFIG,
        "results": results
    }

    with open(results_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📁 Results saved to: {results_file}")

    print("\n✅ All benchmarks complete!")


if __name__ == "__main__":
    run_all_benchmarks()
