#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - Recursive Self-Replication

An agent that evolves through self-distillation:
1. Parent agent writes a simplified version of itself
2. Tests the child against benchmarks
3. If child has innovations, merges them back
4. Creates next generation child

Evolution chain: A → A' → A'' → A''' → ...

This demonstrates bounded open-ended evolution.
"""

import sys
import time
import random
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import init_memory_db, save_episode


class AgentLineage:
    """Tracks the evolutionary lineage of agents."""

    def __init__(self):
        self.generations = []
        self.innovations = []

    def add_generation(self, agent_code: str, performance: Dict):
        """Record a new generation."""
        self.generations.append({
            "generation": len(self.generations),
            "code": agent_code,
            "performance": performance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def add_innovation(self, description: str, source_gen: int):
        """Record an innovation that was merged back."""
        self.innovations.append({
            "description": description,
            "source_generation": source_gen,
            "merged_at": len(self.generations)
        })


class ParentAgent:
    """The parent agent that generates and evaluates children."""

    def __init__(self):
        self.generation = 0
        self.capabilities = {
            "text_transform": self._get_transform_code("basic"),
            "pattern_match": self._get_match_code("basic"),
            "data_filter": self._get_filter_code("basic")
        }
        self.performance_history = []
        self.child_innovations = []

    def _get_transform_code(self, level: str) -> str:
        """Get text transformation code for given level."""
        if level == "basic":
            return '''
def transform(text):
    """Basic transformation - uppercase."""
    return text.upper()
'''
        elif level == "advanced":
            return '''
def transform(text):
    """Advanced transformation - smart case."""
    if not text:
        return text
    # Capitalize first letter of each sentence
    result = []
    capitalize_next = True
    for char in text:
        if capitalize_next and char.isalpha():
            result.append(char.upper())
            capitalize_next = False
        else:
            result.append(char.lower())
        if char in '.!?':
            capitalize_next = True
    return ''.join(result)
'''
        elif level == "optimized":
            return '''
def transform(text):
    """Optimized transformation - efficient smart case."""
    if not text:
        return text
    import re
    # Use regex for efficiency
    sentences = re.split(r'([.!?]+)', text.lower())
    result = []
    for i, part in enumerate(sentences):
        if i % 2 == 0 and part:  # Sentence content
            result.append(part[0].upper() + part[1:] if part else '')
        else:  # Punctuation
            result.append(part)
    return ''.join(result)
'''
        return self._get_transform_code("basic")

    def _get_match_code(self, level: str) -> str:
        """Get pattern matching code for given level."""
        if level == "basic":
            return '''
def match(text, pattern):
    """Basic matching - simple contains."""
    return pattern.lower() in text.lower()
'''
        elif level == "advanced":
            return '''
def match(text, pattern):
    """Advanced matching - word boundaries."""
    import re
    pattern_re = r'\\b' + re.escape(pattern) + r'\\b'
    return bool(re.search(pattern_re, text, re.IGNORECASE))
'''
        elif level == "optimized":
            return '''
def match(text, pattern):
    """Optimized matching - compiled regex with caching."""
    import re
    if not hasattr(match, '_cache'):
        match._cache = {}
    key = pattern.lower()
    if key not in match._cache:
        match._cache[key] = re.compile(r'\\b' + re.escape(pattern) + r'\\b', re.IGNORECASE)
    return bool(match._cache[key].search(text))
'''
        return self._get_match_code("basic")

    def _get_filter_code(self, level: str) -> str:
        """Get data filtering code for given level."""
        if level == "basic":
            return '''
def filter_data(items, predicate):
    """Basic filter - simple list comprehension."""
    return [item for item in items if predicate(item)]
'''
        elif level == "advanced":
            return '''
def filter_data(items, predicate):
    """Advanced filter - with type checking."""
    if not items:
        return []
    result = []
    for item in items:
        try:
            if predicate(item):
                result.append(item)
        except Exception:
            pass  # Skip items that cause errors
    return result
'''
        elif level == "optimized":
            return '''
def filter_data(items, predicate):
    """Optimized filter - generator-based for memory efficiency."""
    if not items:
        return []
    def safe_filter():
        for item in items:
            try:
                if predicate(item):
                    yield item
            except Exception:
                pass
    return list(safe_filter())
'''
        return self._get_filter_code("basic")

    def generate_child(self) -> str:
        """Generate a simplified child agent."""
        # Child attempts to simplify/optimize based on generation
        if self.generation == 0:
            # First child - try advanced patterns
            child_code = self._create_child_code("advanced")
        elif self.generation == 1:
            # Second child - try optimized patterns
            child_code = self._create_child_code("optimized")
        else:
            # Later generations - hybrid approaches
            child_code = self._create_child_code("hybrid")

        return child_code

    def _create_child_code(self, level: str) -> str:
        """Create child agent code at given level."""
        header = f'''"""
Child Agent - Generation {self.generation + 1}
Created by parent at generation {self.generation}
Optimization level: {level}
"""

'''
        if level == "hybrid":
            # Combine best aspects from innovations
            transform = self._get_transform_code("optimized")
            match = self._get_match_code("optimized")
            filter_code = self._get_filter_code("optimized")
        else:
            transform = self._get_transform_code(level)
            match = self._get_match_code(level)
            filter_code = self._get_filter_code(level)

        return header + transform + "\n" + match + "\n" + filter_code

    def merge_innovations(self, innovations: List[str]):
        """Merge successful innovations from child."""
        for innovation in innovations:
            self.child_innovations.append(innovation)

            # Update capabilities based on innovation
            if "smart case" in innovation.lower():
                self.capabilities["text_transform"] = self._get_transform_code("advanced")
            elif "regex" in innovation.lower() or "compiled" in innovation.lower():
                self.capabilities["pattern_match"] = self._get_match_code("optimized")
            elif "generator" in innovation.lower():
                self.capabilities["data_filter"] = self._get_filter_code("optimized")

    def get_current_code(self) -> str:
        """Get current parent agent code."""
        header = f'''"""
Parent Agent - Generation {self.generation}
Innovations merged: {len(self.child_innovations)}
"""

'''
        return (header +
                self.capabilities["text_transform"] + "\n" +
                self.capabilities["pattern_match"] + "\n" +
                self.capabilities["data_filter"])

    def evolve(self):
        """Evolve to next generation."""
        self.generation += 1


def create_benchmarks() -> List[Dict]:
    """Create benchmark tasks for agent evaluation."""
    return [
        # Text transformation benchmarks
        {
            "name": "transform_basic",
            "type": "transform",
            "input": "hello world",
            "expected": lambda r: r.upper() == "HELLO WORLD" or r == "Hello world"
        },
        {
            "name": "transform_sentence",
            "type": "transform",
            "input": "hello. how are you? i am fine!",
            "expected": lambda r: "Hello" in r and "How" in r
        },
        {
            "name": "transform_empty",
            "type": "transform",
            "input": "",
            "expected": lambda r: r == ""
        },
        # Pattern matching benchmarks
        {
            "name": "match_simple",
            "type": "match",
            "input": ("Hello World", "world"),
            "expected": lambda r: r == True
        },
        {
            "name": "match_word_boundary",
            "type": "match",
            "input": ("Hello World", "or"),
            "expected": lambda r: r == False  # "or" is not a word
        },
        {
            "name": "match_case_insensitive",
            "type": "match",
            "input": ("Hello World", "HELLO"),
            "expected": lambda r: r == True
        },
        # Data filtering benchmarks
        {
            "name": "filter_numbers",
            "type": "filter",
            "input": ([1, 2, 3, 4, 5], lambda x: x > 2),
            "expected": lambda r: r == [3, 4, 5]
        },
        {
            "name": "filter_empty",
            "type": "filter",
            "input": ([], lambda x: True),
            "expected": lambda r: r == []
        },
        {
            "name": "filter_mixed",
            "type": "filter",
            "input": ([1, "a", 2, "b", 3], lambda x: isinstance(x, int)),
            "expected": lambda r: r == [1, 2, 3]
        },
    ]


def evaluate_agent(agent_code: str, benchmarks: List[Dict]) -> Dict:
    """Evaluate agent code against benchmarks."""
    # Write code to temp file
    code_path = Path(__file__).parent / "replication_temp.py"
    code_path.write_text(agent_code)

    try:
        # Load module
        spec = importlib.util.spec_from_file_location("agent", code_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        passed = 0
        failed = 0
        innovations = []
        times = []

        for benchmark in benchmarks:
            try:
                start = time.perf_counter()

                if benchmark["type"] == "transform":
                    result = module.transform(benchmark["input"])
                elif benchmark["type"] == "match":
                    text, pattern = benchmark["input"]
                    result = module.match(text, pattern)
                elif benchmark["type"] == "filter":
                    items, predicate = benchmark["input"]
                    result = module.filter_data(items, predicate)
                else:
                    continue

                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)

                if benchmark["expected"](result):
                    passed += 1

                    # Check for innovations
                    if benchmark["name"] == "match_word_boundary" and result == False:
                        innovations.append("Word boundary matching")
                    elif benchmark["name"] == "transform_sentence" and "Hello" in str(result):
                        innovations.append("Smart case transformation")

                else:
                    failed += 1

            except Exception as e:
                failed += 1

        return {
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "success_rate": passed / (passed + failed) if (passed + failed) > 0 else 0,
            "avg_time": sum(times) / len(times) if times else 0,
            "innovations": innovations
        }

    except Exception as e:
        return {
            "passed": 0,
            "failed": len(benchmarks),
            "total": len(benchmarks),
            "success_rate": 0,
            "avg_time": 0,
            "innovations": [],
            "error": str(e)
        }

    finally:
        if code_path.exists():
            code_path.unlink()


def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Recursive Self-Replication Demo                        ║
    ║                                                          ║
    ║   An agent that evolves through self-distillation:       ║
    ║   1. Parent generates simplified child                   ║
    ║   2. Child is tested against benchmarks                  ║
    ║   3. Successful innovations merge back to parent         ║
    ║   4. Process repeats with improved parent                ║
    ║                                                          ║
    ║   Evolution chain: A → A' → A'' → A''' → ...             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print("\033[2J\033[H")
    print(banner)


def display_generation(gen: int, parent_perf: Dict, child_perf: Dict, innovations: List[str]):
    """Display generation results."""
    print("\033[2J\033[H")
    print(f"\n{'='*60}")
    print(f"  GENERATION {gen}")
    print(f"{'='*60}\n")

    # Parent performance
    print("  \033[96mPARENT AGENT:\033[0m")
    print("  " + "─" * 56)
    p_rate = parent_perf.get("success_rate", 0)
    p_color = "\033[92m" if p_rate >= 0.9 else "\033[93m" if p_rate >= 0.7 else "\033[91m"
    print(f"    Tests: {parent_perf.get('passed', 0)}/{parent_perf.get('total', 0)}")
    print(f"    Success Rate: {p_color}{p_rate*100:.0f}%\033[0m")
    print(f"    Avg Time: {parent_perf.get('avg_time', 0):.2f}ms")

    # Child performance
    print(f"\n  \033[96mCHILD AGENT:\033[0m")
    print("  " + "─" * 56)
    c_rate = child_perf.get("success_rate", 0)
    c_color = "\033[92m" if c_rate >= 0.9 else "\033[93m" if c_rate >= 0.7 else "\033[91m"
    print(f"    Tests: {child_perf.get('passed', 0)}/{child_perf.get('total', 0)}")
    print(f"    Success Rate: {c_color}{c_rate*100:.0f}%\033[0m")
    print(f"    Avg Time: {child_perf.get('avg_time', 0):.2f}ms")

    # Comparison
    print(f"\n  \033[96mCOMPARISON:\033[0m")
    print("  " + "─" * 56)

    if c_rate > p_rate:
        print(f"    Child outperforms parent! \033[92m+{(c_rate-p_rate)*100:.0f}%\033[0m")
    elif c_rate == p_rate:
        print(f"    Child matches parent performance")
    else:
        print(f"    Parent still better by \033[93m{(p_rate-c_rate)*100:.0f}%\033[0m")

    # Innovations
    if innovations:
        print(f"\n  \033[92m✓ INNOVATIONS DISCOVERED:\033[0m")
        for innovation in innovations:
            print(f"    • {innovation}")


def display_final_summary(lineage: AgentLineage, parent: ParentAgent):
    """Display final evolution summary."""
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              EVOLUTION COMPLETE                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Lineage
    print("  EVOLUTIONARY LINEAGE:")
    print("  " + "─" * 56)

    for i, gen in enumerate(lineage.generations):
        perf = gen["performance"]
        marker = "→" if i < len(lineage.generations) - 1 else "★"
        print(f"    {marker} Gen {i}: {perf.get('success_rate', 0)*100:.0f}% success, {perf.get('avg_time', 0):.2f}ms")

    # Innovations
    if lineage.innovations:
        print("\n  INNOVATIONS MERGED:")
        print("  " + "─" * 56)
        for innovation in lineage.innovations:
            print(f"    • {innovation['description']} (from gen {innovation['source_generation']})")

    # Improvement
    if len(lineage.generations) >= 2:
        first = lineage.generations[0]["performance"]
        last = lineage.generations[-1]["performance"]

        first_rate = first.get("success_rate", 0)
        last_rate = last.get("success_rate", 0)

        print("\n  IMPROVEMENT:")
        print("  " + "─" * 56)
        print(f"    Initial: {first_rate*100:.0f}%")
        print(f"    Final:   {last_rate*100:.0f}%")

        if first_rate > 0:
            improvement = ((last_rate - first_rate) / first_rate) * 100
            print(f"    Change:  \033[92m{improvement:+.0f}%\033[0m")
        else:
            print(f"    Change:  \033[92m{last_rate*100:.0f}% from 0%\033[0m")

        # Speed improvement
        first_time = first.get("avg_time", 1)
        last_time = last.get("avg_time", 1)
        if first_time > 0 and last_time > 0:
            speed_change = ((first_time - last_time) / first_time) * 100
            if speed_change > 0:
                print(f"    Speed:   \033[92m{speed_change:.0f}% faster\033[0m")

    # Key insight
    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The agent created simplified versions of itself,")
    print("    tested them, and merged successful innovations back.")
    print("\n    \033[96mThis is bounded open-ended evolution.\033[0m\n")


def main():
    parser = argparse.ArgumentParser(description="Recursive Self-Replication Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically")
    parser.add_argument("--generations", type=int, default=5, help="Number of generations")
    args = parser.parse_args()

    # Initialize
    init_memory_db()
    print_banner()

    if not args.auto:
        input("  Press Enter to start evolution...")
    else:
        time.sleep(1)

    # Setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ria.replication")

    parent = ParentAgent()
    lineage = AgentLineage()
    benchmarks = create_benchmarks()

    # Evolution loop
    for gen in range(args.generations):
        # Evaluate parent
        parent_code = parent.get_current_code()
        parent_perf = evaluate_agent(parent_code, benchmarks)

        # Record parent generation
        lineage.add_generation(parent_code, parent_perf)

        # Generate and evaluate child
        child_code = parent.generate_child()
        child_perf = evaluate_agent(child_code, benchmarks)

        # Check for innovations
        innovations = child_perf.get("innovations", [])

        # Display results
        display_generation(gen, parent_perf, child_perf, innovations)

        # Merge innovations if child did well
        if child_perf.get("success_rate", 0) >= parent_perf.get("success_rate", 0):
            if innovations:
                parent.merge_innovations(innovations)
                for innovation in innovations:
                    lineage.add_innovation(innovation, gen)
                    logger.info(f"Merged innovation: {innovation}")

            # Save evolution episode
            save_episode(
                task=f"replication_gen{gen}",
                result="evolved" if innovations else "stable",
                reflection=f"Child success: {child_perf.get('success_rate', 0)*100:.0f}%"
            )

        # Evolve parent for next generation
        parent.evolve()

        logger.info(f"Generation {gen}: Parent {parent_perf.get('success_rate', 0)*100:.0f}%, "
                   f"Child {child_perf.get('success_rate', 0)*100:.0f}%")

        time.sleep(0.5)

    # Final evaluation
    final_code = parent.get_current_code()
    final_perf = evaluate_agent(final_code, benchmarks)
    lineage.add_generation(final_code, final_perf)

    # Final summary
    display_final_summary(lineage, parent)

    logger.info(f"Evolution complete: {args.generations} generations, "
               f"{len(lineage.innovations)} innovations merged")


if __name__ == "__main__":
    main()
