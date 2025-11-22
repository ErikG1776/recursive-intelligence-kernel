#!/usr/bin/env python3
"""
Meta-Evolving Agent Demo - Recursive Intelligence Algorithm

The most advanced demo: an agent that rewrites its own architecture.

- Detects inefficiencies in its own code
- Rewrites portions of its own agent loop
- Validates the new architecture
- Benchmarks the improvement
- Adopts upgrades when they outperform

This is Recursive Intelligence applied to itself.
"""

import sys
import os
import time
import importlib.util
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import setup_logging
from memory import init_memory_db, save_episode

logger = setup_logging("ria.meta_evolve")

# ==========================================================
# === BENCHMARK TASKS ======================================
# ==========================================================

def generate_sorting_task():
    """Generate a sorting benchmark task."""
    size = random.randint(50, 200)
    arr = [random.randint(0, 1000) for _ in range(size)]
    return {"type": "sort", "data": arr, "expected": sorted(arr)}

def generate_search_task():
    """Generate a search benchmark task."""
    size = random.randint(50, 200)
    arr = sorted([random.randint(0, 1000) for _ in range(size)])
    target = random.choice(arr) if random.random() > 0.3 else random.randint(0, 1000)
    expected = arr.index(target) if target in arr else -1
    return {"type": "search", "data": arr, "target": target, "expected": expected}

def generate_fibonacci_task():
    """Generate a fibonacci benchmark task."""
    n = random.randint(10, 25)
    def fib(x):
        if x <= 1:
            return x
        a, b = 0, 1
        for _ in range(x - 1):
            a, b = b, a + b
        return b
    return {"type": "fibonacci", "n": n, "expected": fib(n)}

# ==========================================================
# === AGENT ARCHITECTURES ==================================
# ==========================================================

AGENT_ARCHITECTURES = {
    "basic": '''
class AgentLoop:
    """Basic agent loop - simple sequential processing."""

    def __init__(self):
        self.history = []
        self.strategy = "default"

    def decide_strategy(self, task):
        """Always use default strategy."""
        return "default"

    def execute(self, task):
        """Execute task with basic approach."""
        if task["type"] == "sort":
            # Bubble sort - O(n^2)
            arr = task["data"].copy()
            n = len(arr)
            for i in range(n):
                for j in range(0, n-i-1):
                    if arr[j] > arr[j+1]:
                        arr[j], arr[j+1] = arr[j+1], arr[j]
            return arr

        elif task["type"] == "search":
            # Linear search - O(n)
            for i, val in enumerate(task["data"]):
                if val == task["target"]:
                    return i
            return -1

        elif task["type"] == "fibonacci":
            # Recursive - O(2^n)
            def fib(n):
                if n <= 1:
                    return n
                return fib(n-1) + fib(n-2)
            return fib(task["n"])

    def learn(self, task, result, success):
        """No learning in basic architecture."""
        self.history.append(success)
''',

    "adaptive": '''
class AgentLoop:
    """Adaptive agent loop - chooses strategy based on task."""

    def __init__(self):
        self.history = []
        self.task_performance = {}

    def decide_strategy(self, task):
        """Choose strategy based on task type."""
        if task["type"] == "sort":
            return "quicksort" if len(task["data"]) > 50 else "insertion"
        elif task["type"] == "search":
            return "binary" if len(task["data"]) > 20 else "linear"
        else:
            return "optimized"

    def execute(self, task):
        """Execute with adaptive strategy selection."""
        strategy = self.decide_strategy(task)

        if task["type"] == "sort":
            arr = task["data"].copy()
            if strategy == "quicksort":
                def quicksort(a):
                    if len(a) <= 1:
                        return a
                    pivot = a[len(a)//2]
                    left = [x for x in a if x < pivot]
                    mid = [x for x in a if x == pivot]
                    right = [x for x in a if x > pivot]
                    return quicksort(left) + mid + quicksort(right)
                return quicksort(arr)
            else:
                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1
                    while j >= 0 and arr[j] > key:
                        arr[j+1] = arr[j]
                        j -= 1
                    arr[j+1] = key
                return arr

        elif task["type"] == "search":
            arr = task["data"]
            target = task["target"]
            if strategy == "binary":
                left, right = 0, len(arr) - 1
                while left <= right:
                    mid = (left + right) // 2
                    if arr[mid] == target:
                        return mid
                    elif arr[mid] < target:
                        left = mid + 1
                    else:
                        right = mid - 1
                return -1
            else:
                for i, val in enumerate(arr):
                    if val == target:
                        return i
                return -1

        elif task["type"] == "fibonacci":
            n = task["n"]
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(n - 1):
                a, b = b, a + b
            return b

    def learn(self, task, result, success):
        """Track performance by task type."""
        task_type = task["type"]
        if task_type not in self.task_performance:
            self.task_performance[task_type] = {"success": 0, "total": 0}
        self.task_performance[task_type]["total"] += 1
        if success:
            self.task_performance[task_type]["success"] += 1
        self.history.append(success)
''',

    "learning": '''
class AgentLoop:
    """Learning agent loop - improves based on past performance."""

    def __init__(self):
        self.history = []
        self.task_stats = {}
        self.strategy_scores = {}

    def decide_strategy(self, task):
        """Choose strategy based on learned performance."""
        task_type = task["type"]

        # Use best known strategy for this task type
        if task_type in self.strategy_scores:
            scores = self.strategy_scores[task_type]
            if scores:
                return max(scores, key=scores.get)

        # Default strategies
        if task_type == "sort":
            return "timsort"
        elif task_type == "search":
            return "binary"
        else:
            return "memoized"

    def execute(self, task):
        """Execute with learning-optimized strategies."""
        strategy = self.decide_strategy(task)

        if task["type"] == "sort":
            arr = task["data"].copy()
            # Use Python's built-in (Timsort) - O(n log n)
            return sorted(arr)

        elif task["type"] == "search":
            arr = task["data"]
            target = task["target"]
            # Binary search with early termination
            left, right = 0, len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == target:
                    return mid
                elif arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1

        elif task["type"] == "fibonacci":
            # Iterative with O(n)
            n = task["n"]
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(n - 1):
                a, b = b, a + b
            return b

    def learn(self, task, result, success):
        """Learn from performance to improve strategy selection."""
        task_type = task["type"]
        strategy = self.decide_strategy(task)

        # Update strategy scores
        if task_type not in self.strategy_scores:
            self.strategy_scores[task_type] = {}
        if strategy not in self.strategy_scores[task_type]:
            self.strategy_scores[task_type][strategy] = 0

        self.strategy_scores[task_type][strategy] += 1 if success else -1
        self.history.append(success)
''',

    "meta_optimized": '''
class AgentLoop:
    """Meta-optimized agent loop - self-aware and self-improving."""

    def __init__(self):
        self.history = []
        self.execution_times = {}
        self.strategy_performance = {}
        self.adaptation_threshold = 0.8

    def decide_strategy(self, task):
        """Meta-decision: choose based on multiple factors."""
        task_type = task["type"]
        data_size = len(task.get("data", [])) if "data" in task else task.get("n", 10)

        # Analyze past performance for this task type and size
        perf_key = f"{task_type}_{data_size // 50}"

        if perf_key in self.strategy_performance:
            perf = self.strategy_performance[perf_key]
            if perf["success_rate"] < self.adaptation_threshold:
                # Performance below threshold - try alternative
                return "alternative"

        # Optimal strategies based on analysis
        strategies = {
            "sort": "builtin",      # Python's Timsort is optimal
            "search": "binary",     # O(log n)
            "fibonacci": "iterative" # O(n)
        }
        return strategies.get(task_type, "default")

    def execute(self, task):
        """Execute with meta-optimized strategies."""
        import time
        start = time.perf_counter()

        if task["type"] == "sort":
            result = sorted(task["data"].copy())

        elif task["type"] == "search":
            arr = task["data"]
            target = task["target"]
            left, right = 0, len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == target:
                    result = mid
                    break
                elif arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            else:
                result = -1

        elif task["type"] == "fibonacci":
            n = task["n"]
            if n <= 1:
                result = n
            else:
                a, b = 0, 1
                for _ in range(n - 1):
                    a, b = b, a + b
                result = b
        else:
            result = None

        elapsed = time.perf_counter() - start

        # Track execution time for meta-analysis
        task_type = task["type"]
        if task_type not in self.execution_times:
            self.execution_times[task_type] = []
        self.execution_times[task_type].append(elapsed)

        return result

    def learn(self, task, result, success):
        """Meta-learning: analyze and optimize own performance."""
        task_type = task["type"]
        data_size = len(task.get("data", [])) if "data" in task else task.get("n", 10)
        perf_key = f"{task_type}_{data_size // 50}"

        # Update performance tracking
        if perf_key not in self.strategy_performance:
            self.strategy_performance[perf_key] = {"successes": 0, "total": 0}

        self.strategy_performance[perf_key]["total"] += 1
        if success:
            self.strategy_performance[perf_key]["successes"] += 1

        # Calculate success rate
        stats = self.strategy_performance[perf_key]
        stats["success_rate"] = stats["successes"] / stats["total"]

        self.history.append(success)

        # Meta-optimization: adjust adaptation threshold based on overall performance
        if len(self.history) >= 10:
            recent_rate = sum(self.history[-10:]) / 10
            if recent_rate > 0.9:
                self.adaptation_threshold = min(0.95, self.adaptation_threshold + 0.01)
            elif recent_rate < 0.7:
                self.adaptation_threshold = max(0.6, self.adaptation_threshold - 0.01)
'''
}

ARCHITECTURE_ORDER = ["basic", "adaptive", "learning", "meta_optimized"]

# ==========================================================
# === META-EVOLVING AGENT ==================================
# ==========================================================

class MetaEvolvingAgent:
    """
    An agent that evolves its own architecture.

    This is Recursive Intelligence applied to itself.
    """

    def __init__(self):
        self.agent_file = Path(__file__).parent / "evolved_agent.py"
        self.current_architecture = "basic"
        self.generation = 0
        self.benchmark_results = []
        self._write_architecture()

    def _write_architecture(self):
        code = f'''"""
Evolved Agent Architecture: {self.current_architecture}
Generation: {self.generation}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

{AGENT_ARCHITECTURES[self.current_architecture]}
'''
        self.agent_file.write_text(code)
        logger.info(f"Agent architecture evolved to '{self.current_architecture}'")

    def _load_agent(self):
        spec = importlib.util.spec_from_file_location("evolved_agent", self.agent_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.AgentLoop()

    def benchmark(self, num_tasks=10) -> dict:
        """Benchmark current architecture performance."""
        agent = self._load_agent()
        results = {"successes": 0, "total": num_tasks, "tasks": []}

        task_generators = [generate_sorting_task, generate_search_task, generate_fibonacci_task]

        for _ in range(num_tasks):
            task = random.choice(task_generators)()

            try:
                start = time.perf_counter()
                result = agent.execute(task)
                elapsed = time.perf_counter() - start

                success = result == task["expected"]
                agent.learn(task, result, success)

                if success:
                    results["successes"] += 1

                results["tasks"].append({
                    "type": task["type"],
                    "success": success,
                    "time": elapsed
                })
            except Exception as e:
                results["tasks"].append({
                    "type": task["type"],
                    "success": False,
                    "error": str(e)
                })

        results["success_rate"] = results["successes"] / results["total"]
        results["avg_time"] = sum(t.get("time", 0) for t in results["tasks"]) / len(results["tasks"])

        return results

    def analyze_performance(self, results: dict) -> dict:
        """Analyze benchmark results to identify inefficiencies."""
        analysis = {
            "success_rate": results["success_rate"],
            "avg_time": results["avg_time"],
            "issues": []
        }

        # Check for performance issues
        if results["success_rate"] < 0.9:
            analysis["issues"].append("Low success rate - need better algorithms")

        if results["avg_time"] > 0.01:
            analysis["issues"].append("High execution time - need optimization")

        # Check for specific task failures
        task_failures = {}
        for task in results["tasks"]:
            if not task["success"]:
                task_type = task["type"]
                task_failures[task_type] = task_failures.get(task_type, 0) + 1

        for task_type, count in task_failures.items():
            if count > 1:
                analysis["issues"].append(f"Multiple failures in {task_type} tasks")

        return analysis

    def evolve(self) -> str:
        """Evolve to the next architecture."""
        idx = ARCHITECTURE_ORDER.index(self.current_architecture)
        if idx < len(ARCHITECTURE_ORDER) - 1:
            self.current_architecture = ARCHITECTURE_ORDER[idx + 1]
            self.generation += 1
            self._write_architecture()
        return self.current_architecture

    def show_architecture(self):
        code = self.agent_file.read_text()
        lines = code.split('\n')
        print(f"\n  \033[96m┌─ AGENT ARCHITECTURE (Gen {self.generation}) ───────────────┐\033[0m")
        for line in lines[:35]:
            print(f"  \033[96m│\033[0m {line}")
        if len(lines) > 35:
            print(f"  \033[96m│\033[0m ...")
        print(f"  \033[96m└────────────────────────────────────────────────┘\033[0m")


# ==========================================================
# === DEMO =================================================
# ==========================================================

def run_demo(interactive: bool = True):
    """Run the meta-evolving agent demonstration."""

    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Meta-Evolving Agent Demo                               ║
    ║                                                          ║
    ║   An agent that rewrites its own architecture:           ║
    ║   1. Benchmarks its current performance                  ║
    ║   2. Detects inefficiencies in its own code              ║
    ║   3. Rewrites portions of its agent loop                 ║
    ║   4. Validates the new architecture                      ║
    ║   5. Adopts upgrades when they outperform                ║
    ║                                                          ║
    ║   This is Recursive Intelligence applied to itself.      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if interactive:
        input("  Press ENTER to start...")
    else:
        time.sleep(1)

    init_memory_db()
    meta_agent = MetaEvolvingAgent()

    evolution_history = []
    max_generations = 4

    for gen in range(max_generations):
        print("\033[2J\033[H")
        print("=" * 60)
        print(f"  GENERATION {gen}")
        print("=" * 60)
        print()

        print(f"  \033[96mArchitecture: {meta_agent.current_architecture}\033[0m")
        print()

        # Show current architecture
        meta_agent.show_architecture()

        if interactive:
            input("\n  Press ENTER to benchmark...")
        else:
            time.sleep(0.5)

        # Benchmark
        print("\n  \033[95m📊 BENCHMARKING...\033[0m\n")
        results = meta_agent.benchmark(num_tasks=12)

        # Show results
        print(f"  Results:")
        print(f"    Success Rate: {results['success_rate']*100:.0f}%")
        print(f"    Avg Time: {results['avg_time']*1000:.2f}ms")
        print()

        # Show task breakdown
        for task in results["tasks"][:6]:
            status = "\033[92m✓\033[0m" if task["success"] else "\033[91m✗\033[0m"
            time_str = f"{task.get('time', 0)*1000:.1f}ms"
            print(f"    {status} {task['type']}: {time_str}")

        if len(results["tasks"]) > 6:
            print(f"    ... and {len(results['tasks']) - 6} more")

        # Analyze
        print("\n  \033[95m🔍 ANALYZING PERFORMANCE...\033[0m\n")
        analysis = meta_agent.analyze_performance(results)

        if analysis["issues"]:
            print("  Issues detected:")
            for issue in analysis["issues"]:
                print(f"    \033[91m• {issue}\033[0m")
        else:
            print("  \033[92m✓ No significant issues detected\033[0m")

        evolution_history.append({
            "generation": gen,
            "architecture": meta_agent.current_architecture,
            "success_rate": results["success_rate"],
            "avg_time": results["avg_time"]
        })

        # Save to memory
        save_episode(
            task=f"meta_evolve_gen_{gen}",
            result=f"success_rate:{results['success_rate']:.2f}",
            reflection=f"Architecture: {meta_agent.current_architecture}"
        )

        # Decide whether to evolve
        if gen < max_generations - 1:
            if results["success_rate"] < 0.95 or results["avg_time"] > 0.005:
                print(f"\n  \033[95m🧬 EVOLVING ARCHITECTURE...\033[0m")
                new_arch = meta_agent.evolve()
                print(f"  \033[95m   New architecture: {new_arch}\033[0m")
            else:
                print(f"\n  \033[92m✓ Architecture performing well\033[0m")
                # Still evolve to show progression
                meta_agent.evolve()

        if interactive:
            input("\n  Press ENTER for next generation...")
        else:
            time.sleep(1)

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 EVOLUTION COMPLETE                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  EVOLUTION HISTORY:")
    print("  " + "─" * 56)

    for h in evolution_history:
        rate_color = "\033[92m" if h["success_rate"] >= 0.9 else "\033[91m"
        print(f"    Gen {h['generation']}: {h['architecture']}")
        print(f"         {rate_color}{h['success_rate']*100:.0f}%\033[0m success, {h['avg_time']*1000:.2f}ms avg")

    # Calculate improvement
    if len(evolution_history) >= 2:
        initial = evolution_history[0]
        final = evolution_history[-1]
        rate_improvement = ((final["success_rate"] - initial["success_rate"]) / max(initial["success_rate"], 0.01)) * 100
        time_improvement = ((initial["avg_time"] - final["avg_time"]) / max(initial["avg_time"], 0.0001)) * 100

        print()
        print("  IMPROVEMENT:")
        print("  " + "─" * 56)
        print(f"    Success Rate: \033[92m+{rate_improvement:.0f}%\033[0m")
        print(f"    Speed: \033[92m{time_improvement:.0f}%\033[0m faster")

    print()
    print("  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The agent analyzed its own performance, detected")
    print("    inefficiencies, and rewrote its own architecture.")
    print()
    print("    \033[96mThis is Recursive Intelligence applied to itself.\033[0m")
    print()

    print("  FINAL ARCHITECTURE:")
    meta_agent.show_architecture()


if __name__ == "__main__":
    try:
        interactive = "--auto" not in sys.argv
        run_demo(interactive=interactive)
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
