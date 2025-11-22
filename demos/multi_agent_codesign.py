#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - Multi-Agent Recursive Co-Design

A swarm of specialized agents collaboratively design a system:
1. Architect Agent - designs high-level structure
2. Engineer Agent - implements the code
3. Tester Agent - writes adversarial tests
4. Optimizer Agent - identifies and fixes inefficiencies
5. Coordinator - evolves/replaces underperforming agents

This demonstrates emergent collaboration through recursive intelligence.
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


class Agent:
    """Base class for all agents in the co-design swarm."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.generation = 0
        self.performance_history = []
        self.strategy = "basic"

    def act(self, context: Dict) -> Dict:
        """Perform agent's action. Override in subclasses."""
        raise NotImplementedError

    def record_performance(self, score: float, feedback: str):
        """Record performance for evolution decisions."""
        self.performance_history.append({
            "score": score,
            "feedback": feedback,
            "generation": self.generation,
            "strategy": self.strategy
        })

    def get_avg_performance(self, last_n: int = 3) -> float:
        """Get average recent performance."""
        if not self.performance_history:
            return 0.0
        recent = self.performance_history[-last_n:]
        return sum(p["score"] for p in recent) / len(recent)


class ArchitectAgent(Agent):
    """Designs high-level architecture and module structure."""

    STRATEGIES = ["minimal", "modular", "defensive", "optimized"]

    def __init__(self):
        super().__init__("Architect", "Design system architecture")
        self.strategy = "minimal"

    def act(self, context: Dict) -> Dict:
        """Generate architecture based on task requirements."""
        task = context.get("task", {})
        task_type = task.get("type", "calculator")

        if self.strategy == "minimal":
            return self._minimal_architecture(task_type)
        elif self.strategy == "modular":
            return self._modular_architecture(task_type)
        elif self.strategy == "defensive":
            return self._defensive_architecture(task_type)
        elif self.strategy == "optimized":
            return self._optimized_architecture(task_type)
        return self._minimal_architecture(task_type)

    def _minimal_architecture(self, task_type: str) -> Dict:
        """Minimal viable architecture."""
        return {
            "modules": ["core"],
            "interfaces": {
                "core": ["process"]
            },
            "dependencies": {},
            "notes": "Minimal single-module design"
        }

    def _modular_architecture(self, task_type: str) -> Dict:
        """Modular architecture with separation of concerns."""
        return {
            "modules": ["input_handler", "processor", "output_formatter"],
            "interfaces": {
                "input_handler": ["validate", "parse"],
                "processor": ["compute"],
                "output_formatter": ["format"]
            },
            "dependencies": {
                "processor": ["input_handler"],
                "output_formatter": ["processor"]
            },
            "notes": "Modular design with clear separation"
        }

    def _defensive_architecture(self, task_type: str) -> Dict:
        """Defensive architecture with error handling."""
        return {
            "modules": ["validator", "processor", "error_handler", "logger"],
            "interfaces": {
                "validator": ["validate_input", "validate_output"],
                "processor": ["compute"],
                "error_handler": ["handle", "recover"],
                "logger": ["log"]
            },
            "dependencies": {
                "processor": ["validator"],
                "error_handler": ["logger"]
            },
            "notes": "Defensive design with comprehensive error handling"
        }

    def _optimized_architecture(self, task_type: str) -> Dict:
        """Optimized architecture for performance."""
        return {
            "modules": ["cache", "validator", "processor", "output"],
            "interfaces": {
                "cache": ["get", "set", "invalidate"],
                "validator": ["validate"],
                "processor": ["compute", "compute_batch"],
                "output": ["format", "format_batch"]
            },
            "dependencies": {
                "processor": ["cache", "validator"],
                "output": ["processor"]
            },
            "notes": "Performance-optimized with caching and batching"
        }

    def evolve(self):
        """Evolve to better strategy based on feedback."""
        current_idx = self.STRATEGIES.index(self.strategy)
        if current_idx < len(self.STRATEGIES) - 1:
            self.strategy = self.STRATEGIES[current_idx + 1]
            self.generation += 1
            return True
        return False


class EngineerAgent(Agent):
    """Implements code following the architecture."""

    STRATEGIES = ["basic", "typed", "documented", "production"]

    def __init__(self):
        super().__init__("Engineer", "Implement code from architecture")
        self.strategy = "basic"

    def act(self, context: Dict) -> Dict:
        """Generate implementation based on architecture."""
        architecture = context.get("architecture", {})
        task = context.get("task", {})

        if self.strategy == "basic":
            return self._basic_implementation(architecture, task)
        elif self.strategy == "typed":
            return self._typed_implementation(architecture, task)
        elif self.strategy == "documented":
            return self._documented_implementation(architecture, task)
        elif self.strategy == "production":
            return self._production_implementation(architecture, task)
        return self._basic_implementation(architecture, task)

    def _basic_implementation(self, arch: Dict, task: Dict) -> Dict:
        """Basic implementation without extras."""
        code = '''
class Calculator:
    def compute(self, operation, a, b):
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b
        return None
'''
        return {"code": code, "style": "basic"}

    def _typed_implementation(self, arch: Dict, task: Dict) -> Dict:
        """Implementation with type hints."""
        code = '''
from typing import Optional, Union

Number = Union[int, float]

class Calculator:
    def compute(self, operation: str, a: Number, b: Number) -> Optional[Number]:
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                return None
            return a / b
        return None
'''
        return {"code": code, "style": "typed"}

    def _documented_implementation(self, arch: Dict, task: Dict) -> Dict:
        """Implementation with documentation."""
        code = '''
from typing import Optional, Union

Number = Union[int, float]

class Calculator:
    """A calculator that performs basic arithmetic operations."""

    def compute(self, operation: str, a: Number, b: Number) -> Optional[Number]:
        """
        Perform an arithmetic operation on two numbers.

        Args:
            operation: One of 'add', 'subtract', 'multiply', 'divide'
            a: First operand
            b: Second operand

        Returns:
            Result of the operation, or None if invalid
        """
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        raise ValueError(f"Unknown operation: {operation}")
'''
        return {"code": code, "style": "documented"}

    def _production_implementation(self, arch: Dict, task: Dict) -> Dict:
        """Production-ready implementation."""
        code = '''
from typing import Optional, Union
from functools import lru_cache

Number = Union[int, float]

class Calculator:
    """Production-ready calculator with caching and validation."""

    OPERATIONS = {"add", "subtract", "multiply", "divide"}

    def __init__(self):
        self._cache = {}

    def validate(self, operation: str, a: Number, b: Number) -> bool:
        """Validate inputs before computation."""
        if operation not in self.OPERATIONS:
            return False
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return False
        if operation == "divide" and b == 0:
            return False
        return True

    def compute(self, operation: str, a: Number, b: Number) -> Number:
        """
        Perform an arithmetic operation with caching.

        Raises:
            ValueError: If inputs are invalid
        """
        if not self.validate(operation, a, b):
            raise ValueError(f"Invalid operation: {operation}({a}, {b})")

        cache_key = (operation, a, b)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b

        self._cache[cache_key] = result
        return result

    def compute_batch(self, operations: list) -> list:
        """Process multiple operations efficiently."""
        return [self.compute(op, a, b) for op, a, b in operations]
'''
        return {"code": code, "style": "production"}

    def evolve(self):
        """Evolve to better strategy."""
        current_idx = self.STRATEGIES.index(self.strategy)
        if current_idx < len(self.STRATEGIES) - 1:
            self.strategy = self.STRATEGIES[current_idx + 1]
            self.generation += 1
            return True
        return False


class TesterAgent(Agent):
    """Writes adversarial tests and fuzzing inputs."""

    STRATEGIES = ["basic", "edge_cases", "adversarial", "comprehensive"]

    def __init__(self):
        super().__init__("Tester", "Generate tests and find bugs")
        self.strategy = "basic"

    def act(self, context: Dict) -> Dict:
        """Generate test cases based on implementation."""
        implementation = context.get("implementation", {})

        if self.strategy == "basic":
            return self._basic_tests()
        elif self.strategy == "edge_cases":
            return self._edge_case_tests()
        elif self.strategy == "adversarial":
            return self._adversarial_tests()
        elif self.strategy == "comprehensive":
            return self._comprehensive_tests()
        return self._basic_tests()

    def _basic_tests(self) -> Dict:
        """Basic happy-path tests."""
        return {
            "tests": [
                {"name": "test_add", "op": "add", "a": 2, "b": 3, "expected": 5},
                {"name": "test_subtract", "op": "subtract", "a": 5, "b": 3, "expected": 2},
                {"name": "test_multiply", "op": "multiply", "a": 4, "b": 3, "expected": 12},
                {"name": "test_divide", "op": "divide", "a": 6, "b": 2, "expected": 3},
            ],
            "coverage": "basic"
        }

    def _edge_case_tests(self) -> Dict:
        """Tests including edge cases."""
        return {
            "tests": [
                {"name": "test_add", "op": "add", "a": 2, "b": 3, "expected": 5},
                {"name": "test_add_zero", "op": "add", "a": 0, "b": 0, "expected": 0},
                {"name": "test_add_negative", "op": "add", "a": -5, "b": 3, "expected": -2},
                {"name": "test_multiply_zero", "op": "multiply", "a": 100, "b": 0, "expected": 0},
                {"name": "test_divide", "op": "divide", "a": 6, "b": 2, "expected": 3},
                {"name": "test_divide_float", "op": "divide", "a": 5, "b": 2, "expected": 2.5},
            ],
            "coverage": "edge_cases"
        }

    def _adversarial_tests(self) -> Dict:
        """Adversarial tests designed to break things."""
        return {
            "tests": [
                {"name": "test_add", "op": "add", "a": 2, "b": 3, "expected": 5},
                {"name": "test_divide_zero", "op": "divide", "a": 5, "b": 0, "expected": "error"},
                {"name": "test_invalid_op", "op": "power", "a": 2, "b": 3, "expected": "error"},
                {"name": "test_large_numbers", "op": "multiply", "a": 10**10, "b": 10**10, "expected": 10**20},
                {"name": "test_float_precision", "op": "add", "a": 0.1, "b": 0.2, "expected": 0.3, "tolerance": 0.0001},
                {"name": "test_negative_divide", "op": "divide", "a": -6, "b": -2, "expected": 3},
            ],
            "coverage": "adversarial"
        }

    def _comprehensive_tests(self) -> Dict:
        """Comprehensive test suite."""
        return {
            "tests": [
                # Basic operations
                {"name": "test_add", "op": "add", "a": 2, "b": 3, "expected": 5},
                {"name": "test_subtract", "op": "subtract", "a": 5, "b": 3, "expected": 2},
                {"name": "test_multiply", "op": "multiply", "a": 4, "b": 3, "expected": 12},
                {"name": "test_divide", "op": "divide", "a": 6, "b": 2, "expected": 3},
                # Edge cases
                {"name": "test_add_zero", "op": "add", "a": 0, "b": 0, "expected": 0},
                {"name": "test_multiply_zero", "op": "multiply", "a": 100, "b": 0, "expected": 0},
                {"name": "test_divide_float", "op": "divide", "a": 5, "b": 2, "expected": 2.5},
                # Adversarial
                {"name": "test_divide_zero", "op": "divide", "a": 5, "b": 0, "expected": "error"},
                {"name": "test_invalid_op", "op": "power", "a": 2, "b": 3, "expected": "error"},
                # Negative numbers
                {"name": "test_add_negative", "op": "add", "a": -5, "b": -3, "expected": -8},
                {"name": "test_subtract_negative", "op": "subtract", "a": -5, "b": 3, "expected": -8},
                # Large numbers
                {"name": "test_large_multiply", "op": "multiply", "a": 10**6, "b": 10**6, "expected": 10**12},
            ],
            "coverage": "comprehensive"
        }

    def evolve(self):
        """Evolve to better strategy."""
        current_idx = self.STRATEGIES.index(self.strategy)
        if current_idx < len(self.STRATEGIES) - 1:
            self.strategy = self.STRATEGIES[current_idx + 1]
            self.generation += 1
            return True
        return False


class OptimizerAgent(Agent):
    """Identifies inefficiencies and suggests improvements."""

    STRATEGIES = ["basic", "performance", "memory", "comprehensive"]

    def __init__(self):
        super().__init__("Optimizer", "Identify and fix inefficiencies")
        self.strategy = "basic"

    def act(self, context: Dict) -> Dict:
        """Analyze code and suggest optimizations."""
        implementation = context.get("implementation", {})
        test_results = context.get("test_results", {})

        if self.strategy == "basic":
            return self._basic_analysis(implementation, test_results)
        elif self.strategy == "performance":
            return self._performance_analysis(implementation, test_results)
        elif self.strategy == "memory":
            return self._memory_analysis(implementation, test_results)
        elif self.strategy == "comprehensive":
            return self._comprehensive_analysis(implementation, test_results)
        return self._basic_analysis(implementation, test_results)

    def _basic_analysis(self, impl: Dict, results: Dict) -> Dict:
        """Basic code review."""
        suggestions = []
        code = impl.get("code", "")

        if "def " in code and '"""' not in code:
            suggestions.append("Add docstrings to functions")

        if "int, float" not in code and "Number" not in code:
            suggestions.append("Add type hints")

        return {
            "suggestions": suggestions,
            "priority": "low",
            "analysis_type": "basic"
        }

    def _performance_analysis(self, impl: Dict, results: Dict) -> Dict:
        """Performance-focused analysis."""
        suggestions = []
        code = impl.get("code", "")

        if "cache" not in code.lower():
            suggestions.append("Add caching for repeated computations")

        if "batch" not in code.lower():
            suggestions.append("Add batch processing capability")

        if results.get("failed", 0) > 0:
            suggestions.append("Fix failing tests before optimizing")

        return {
            "suggestions": suggestions,
            "priority": "medium",
            "analysis_type": "performance"
        }

    def _memory_analysis(self, impl: Dict, results: Dict) -> Dict:
        """Memory-focused analysis."""
        suggestions = []
        code = impl.get("code", "")

        if "self._cache" in code and "invalidate" not in code:
            suggestions.append("Add cache invalidation to prevent memory leaks")

        if "list" in code and "generator" not in code:
            suggestions.append("Consider using generators for large datasets")

        return {
            "suggestions": suggestions,
            "priority": "medium",
            "analysis_type": "memory"
        }

    def _comprehensive_analysis(self, impl: Dict, results: Dict) -> Dict:
        """Comprehensive analysis combining all factors."""
        suggestions = []
        code = impl.get("code", "")

        # Code quality
        if '"""' not in code:
            suggestions.append("Add comprehensive documentation")

        # Performance
        if "cache" not in code.lower():
            suggestions.append("Implement caching strategy")

        # Safety
        if "validate" not in code.lower():
            suggestions.append("Add input validation")

        # Testing
        if results.get("coverage", "") != "comprehensive":
            suggestions.append("Increase test coverage")

        # Error handling
        if "raise" not in code and "error" not in code.lower():
            suggestions.append("Add proper error handling")

        return {
            "suggestions": suggestions,
            "priority": "high",
            "analysis_type": "comprehensive",
            "score": max(0, 100 - len(suggestions) * 10)
        }

    def evolve(self):
        """Evolve to better strategy."""
        current_idx = self.STRATEGIES.index(self.strategy)
        if current_idx < len(self.STRATEGIES) - 1:
            self.strategy = self.STRATEGIES[current_idx + 1]
            self.generation += 1
            return True
        return False


class Coordinator:
    """Coordinates agents and decides evolution."""

    def __init__(self):
        self.agents = {
            "architect": ArchitectAgent(),
            "engineer": EngineerAgent(),
            "tester": TesterAgent(),
            "optimizer": OptimizerAgent()
        }
        self.generation = 0
        self.history = []

    def run_iteration(self, task: Dict) -> Dict:
        """Run one full iteration of co-design."""
        results = {}

        # 1. Architect designs
        arch_context = {"task": task}
        architecture = self.agents["architect"].act(arch_context)
        results["architecture"] = architecture

        # 2. Engineer implements
        eng_context = {"architecture": architecture, "task": task}
        implementation = self.agents["engineer"].act(eng_context)
        results["implementation"] = implementation

        # 3. Tester tests
        test_context = {"implementation": implementation}
        tests = self.agents["tester"].act(test_context)
        results["tests"] = tests

        # 4. Run tests
        test_results = self._run_tests(implementation, tests)
        results["test_results"] = test_results

        # 5. Optimizer analyzes
        opt_context = {"implementation": implementation, "test_results": test_results}
        optimization = self.agents["optimizer"].act(opt_context)
        results["optimization"] = optimization

        # Record performance
        self._record_performance(results)

        return results

    def _run_tests(self, implementation: Dict, tests: Dict) -> Dict:
        """Execute tests against implementation."""
        code = implementation.get("code", "")

        # Write code to temp file
        code_path = Path(__file__).parent / "codesign_temp.py"
        code_path.write_text(code)

        try:
            # Load module
            spec = importlib.util.spec_from_file_location("calc", code_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            calc = module.Calculator()

            # Run tests
            passed = 0
            failed = 0
            failures = []

            for test in tests.get("tests", []):
                try:
                    result = calc.compute(test["op"], test["a"], test["b"])

                    if test["expected"] == "error":
                        # Expected an error but didn't get one
                        failed += 1
                        failures.append(f"{test['name']}: expected error, got {result}")
                    elif "tolerance" in test:
                        if abs(result - test["expected"]) <= test["tolerance"]:
                            passed += 1
                        else:
                            failed += 1
                            failures.append(f"{test['name']}: {result} != {test['expected']}")
                    elif result == test["expected"]:
                        passed += 1
                    else:
                        failed += 1
                        failures.append(f"{test['name']}: {result} != {test['expected']}")

                except Exception as e:
                    if test["expected"] == "error":
                        passed += 1
                    else:
                        failed += 1
                        failures.append(f"{test['name']}: {str(e)}")

            return {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "success_rate": passed / (passed + failed) if (passed + failed) > 0 else 0,
                "failures": failures,
                "coverage": tests.get("coverage", "unknown")
            }

        except Exception as e:
            return {
                "passed": 0,
                "failed": len(tests.get("tests", [])),
                "total": len(tests.get("tests", [])),
                "success_rate": 0,
                "failures": [str(e)],
                "coverage": "error"
            }

        finally:
            if code_path.exists():
                code_path.unlink()

    def _record_performance(self, results: Dict):
        """Record agent performance from iteration."""
        test_results = results.get("test_results", {})
        success_rate = test_results.get("success_rate", 0)

        # Score agents based on their contribution
        self.agents["architect"].record_performance(
            success_rate * 100,
            f"Architecture: {results['architecture'].get('notes', '')}"
        )

        self.agents["engineer"].record_performance(
            success_rate * 100,
            f"Style: {results['implementation'].get('style', '')}"
        )

        self.agents["tester"].record_performance(
            len(results['tests'].get('tests', [])) * 10,
            f"Coverage: {results['tests'].get('coverage', '')}"
        )

        opt_score = results['optimization'].get('score', 50)
        self.agents["optimizer"].record_performance(
            opt_score,
            f"Suggestions: {len(results['optimization'].get('suggestions', []))}"
        )

        self.history.append({
            "generation": self.generation,
            "success_rate": success_rate,
            "test_coverage": test_results.get("coverage", ""),
            "agent_strategies": {
                name: agent.strategy
                for name, agent in self.agents.items()
            }
        })

    def evolve_agents(self) -> List[str]:
        """Evolve underperforming agents."""
        evolved = []

        for name, agent in self.agents.items():
            avg_perf = agent.get_avg_performance()

            # Evolve if performance is below threshold or to keep progressing
            should_evolve = (
                avg_perf < 80 or  # Poor performance
                (len(self.history) > 0 and self.history[-1]["success_rate"] < 1.0)  # Tests failing
            )

            if should_evolve and agent.evolve():
                evolved.append(f"{name} → {agent.strategy}")

        if evolved:
            self.generation += 1

        return evolved


def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Multi-Agent Recursive Co-Design                        ║
    ║                                                          ║
    ║   Watch specialized agents collaborate:                  ║
    ║   🧠 Architect - designs system structure                ║
    ║   🔧 Engineer  - implements the code                     ║
    ║   🧪 Tester    - finds bugs and edge cases               ║
    ║   🔎 Optimizer - suggests improvements                   ║
    ║                                                          ║
    ║   Each agent evolves through recursive intelligence.     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print("\033[2J\033[H")
    print(banner)


def display_iteration(coordinator: Coordinator, results: Dict, iteration: int):
    """Display results of an iteration."""
    print("\033[2J\033[H")
    print(f"\n{'='*60}")
    print(f"  ITERATION {iteration} | Generation {coordinator.generation}")
    print(f"{'='*60}\n")

    # Agent status
    print("  \033[96mAGENT STATUS:\033[0m")
    print("  " + "─" * 56)
    for name, agent in coordinator.agents.items():
        emoji = {"architect": "🧠", "engineer": "🔧", "tester": "🧪", "optimizer": "🔎"}[name]
        avg = agent.get_avg_performance()
        print(f"    {emoji} {name.capitalize():12} | Strategy: {agent.strategy:12} | Perf: {avg:.0f}%")

    # Architecture
    arch = results.get("architecture", {})
    print(f"\n  \033[96mARCHITECTURE:\033[0m")
    print("  " + "─" * 56)
    print(f"    Modules: {', '.join(arch.get('modules', []))}")
    print(f"    Notes: {arch.get('notes', '')}")

    # Implementation
    impl = results.get("implementation", {})
    print(f"\n  \033[96mIMPLEMENTATION:\033[0m")
    print("  " + "─" * 56)
    print(f"    Style: {impl.get('style', '')}")

    # Test Results
    test_results = results.get("test_results", {})
    print(f"\n  \033[96mTEST RESULTS:\033[0m")
    print("  " + "─" * 56)

    success_rate = test_results.get("success_rate", 0)
    color = "\033[92m" if success_rate == 1.0 else "\033[93m" if success_rate >= 0.8 else "\033[91m"
    print(f"    Passed: {test_results.get('passed', 0)}/{test_results.get('total', 0)}")
    print(f"    Success Rate: {color}{success_rate*100:.0f}%\033[0m")
    print(f"    Coverage: {test_results.get('coverage', '')}")

    if test_results.get("failures"):
        print(f"\n    \033[91mFailures:\033[0m")
        for failure in test_results["failures"][:3]:
            print(f"      • {failure}")

    # Optimization
    opt = results.get("optimization", {})
    if opt.get("suggestions"):
        print(f"\n  \033[96mOPTIMIZATION SUGGESTIONS:\033[0m")
        print("  " + "─" * 56)
        for suggestion in opt["suggestions"][:3]:
            print(f"    • {suggestion}")


def display_evolution(evolved: List[str]):
    """Display evolution results."""
    if evolved:
        print(f"\n  \033[92m✓ AGENTS EVOLVED:\033[0m")
        for evo in evolved:
            print(f"    • {evo}")
        time.sleep(0.5)


def display_final_summary(coordinator: Coordinator):
    """Display final summary."""
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              CO-DESIGN COMPLETE                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Final agent states
    print("  FINAL AGENT STATES:")
    print("  " + "─" * 56)
    for name, agent in coordinator.agents.items():
        emoji = {"architect": "🧠", "engineer": "🔧", "tester": "🧪", "optimizer": "🔎"}[name]
        print(f"    {emoji} {name.capitalize():12} | Gen {agent.generation} | Strategy: {agent.strategy}")

    # Evolution history
    if coordinator.history:
        print("\n  EVOLUTION HISTORY:")
        print("  " + "─" * 56)

        first = coordinator.history[0]
        last = coordinator.history[-1]

        print(f"    Initial success rate: {first['success_rate']*100:.0f}%")
        print(f"    Final success rate:   {last['success_rate']*100:.0f}%")

        if first['success_rate'] > 0:
            improvement = ((last['success_rate'] - first['success_rate']) / first['success_rate']) * 100
            print(f"    Improvement:          \033[92m{improvement:+.0f}%\033[0m")
        else:
            print(f"    Improvement:          \033[92m{last['success_rate']*100:.0f}% from 0%\033[0m")

    # Key insight
    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    Multiple specialized agents collaborated to design")
    print("    a system that none could have built alone.")
    print("\n    \033[96mThis is Recursive Intelligence through cooperation.\033[0m\n")


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Recursive Co-Design Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically")
    parser.add_argument("--iterations", type=int, default=8, help="Number of iterations")
    args = parser.parse_args()

    # Initialize
    init_memory_db()
    print_banner()

    if not args.auto:
        input("  Press Enter to start co-design...")
    else:
        time.sleep(1)

    # Setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ria.codesign")

    coordinator = Coordinator()
    task = {"type": "calculator", "requirements": ["basic arithmetic", "error handling"]}

    # Run iterations
    for i in range(1, args.iterations + 1):
        results = coordinator.run_iteration(task)
        display_iteration(coordinator, results, i)

        # Log progress
        test_results = results.get("test_results", {})
        logger.info(f"Iteration {i}: {test_results.get('success_rate', 0)*100:.0f}% success")

        # Evolve agents
        evolved = coordinator.evolve_agents()
        display_evolution(evolved)

        if evolved:
            save_episode(
                task=f"codesign_gen{coordinator.generation}",
                result="evolved",
                reflection=f"Agents evolved: {', '.join(evolved)}"
            )

        time.sleep(0.3)

    # Final summary
    display_final_summary(coordinator)

    # Log completion
    logger.info(f"Co-design complete: {coordinator.generation} generations")


if __name__ == "__main__":
    main()
