# RIA Demo Suite

This directory contains 11 demonstrations of the Recursive Intelligence Algorithm across different domains.

---

## Quick Start

All demos support `--auto` for non-interactive mode:

```bash
python demos/snake_evolution.py --auto --games 30
```

---

## Demo Categories

### 1. Core Concepts

These demos show the fundamental RIA patterns.

#### Self-Evolving Maze Solver
**File:** `self_evolving_maze_solver.py`

Pathfinding agent that evolves strategies from random exploration to A* optimization.

```bash
python demos/self_evolving_maze_solver.py --auto
```

**Key Concepts:** Strategy evolution, fitness evaluation, episodic memory

---

#### Snake Evolution
**File:** `snake_evolution.py`

Snake game agent that evolves from random movement to pathfinding.

```bash
python demos/snake_evolution.py --auto --games 30
```

**Results:** 0 → 60+ average score, 5 strategy evolutions

**Key Concepts:** Game AI, strategy progression, performance metrics

---

#### Meta-Evolving Agent
**File:** `meta_evolving_agent.py`

Agent that rewrites its own architecture to improve performance.

```bash
python demos/meta_evolving_agent.py --auto
```

**Results:** 100% speed improvement (1.81ms → 0.00ms)

**Key Concepts:** Self-modification, architecture evolution, benchmark-driven optimization

---

### 2. Self-Healing Systems

These demos show RIA applied to resilient automation.

#### Adaptive Scraper
**File:** `adaptive_scraper.py`

Web scraper that survives site changes by evolving selectors.

```bash
python demos/adaptive_scraper.py --auto
```

**Results:** 75% success rate across 4 site versions

**Key Concepts:** Selector evolution, DOM analysis, failure recovery

---

#### Self-Healing RPA
**File:** `self_healing_rpa.py`

Browser automation that survives UI redesigns.

```bash
python demos/self_healing_rpa.py --auto
```

**Results:** 62% success rate, evolves through 6 locator strategies

**Key Concepts:** Playwright automation, multi-strategy locators, UI adaptation

---

### 3. Autonomous Code Evolution

These demos show RIA applied to code generation and repair.

#### Self-Debugging Agent
**File:** `self_debugging_agent.py`

Agent that analyzes failing tests and generates fixes.

```bash
python demos/self_debugging_agent.py --auto
```

**Results:** 80% bug fix success rate across 5 bug types

**Key Concepts:** Error analysis, code generation, test-driven fixes

---

#### Autonomous Bug Fixer
**File:** `autonomous_bugfixer.py`

Agent that finds relevant code, analyzes failures, and writes fixes.

```bash
python demos/autonomous_bugfixer.py --auto
```

**Results:** 100% success rate on 5 different bugs

**Key Concepts:** Code search, semantic analysis, multi-file fixes

---

#### Self-Evolving Repository
**File:** `self_evolving_repo.py`

Simulated codebase that improves itself through autonomous commits.

```bash
python demos/self_evolving_repo.py --auto --generations 6
```

**Results:** 5 AI-authored commits improving 3 functions

**Key Concepts:** Code analysis, automated commits, test validation

---

### 4. Multi-Agent Systems

These demos show multiple RIA agents working together.

#### Adversarial Evolution
**File:** `adversarial_evolution.py`

Two agents compete to strengthen each other (Defender vs Attacker).

```bash
python demos/adversarial_evolution.py --auto
```

**Results:** 100% final robustness

**Key Concepts:** Competitive evolution, adversarial testing, co-evolution

---

#### Multi-Agent Co-Design
**File:** `multi_agent_codesign.py`

Four specialized agents collaborate to design a system.

```bash
python demos/multi_agent_codesign.py --auto --iterations 8
```

**Results:** 4 generations, agents evolve in response to each other

**Key Concepts:** Agent specialization, collaborative evolution, emergent coordination

**Agents:**
- 🧠 Architect - designs system structure
- 🔧 Engineer - implements code
- 🧪 Tester - finds bugs and edge cases
- 🔎 Optimizer - suggests improvements

---

#### Recursive Self-Replication
**File:** `recursive_self_replication.py`

Agent creates simplified versions of itself and merges innovations back.

```bash
python demos/recursive_self_replication.py --auto --generations 5
```

**Results:** 78% → 89% success rate (+14% improvement)

**Key Concepts:** Self-distillation, innovation merging, bounded evolution

---

## Understanding the Output

All demos display:

1. **Generation/Iteration** - Current evolution step
2. **Strategy** - Current approach being used
3. **Performance** - Success rate, timing, or score
4. **Evolution Events** - When strategies change
5. **Final Summary** - Overall improvement metrics

---

## Adding New Demos

To create a new demo:

1. Import core modules:
```python
from memory import init_memory_db, save_episode
```

2. Initialize memory:
```python
init_memory_db()
```

3. Save episodes after each action:
```python
save_episode(
    task="your_task_name",
    result="success/failure",
    reflection="what was learned"
)
```

4. Add `--auto` flag for non-interactive mode

5. Display clear progress and results

---

## Generated Files

These files are created during demo runs and are gitignored:

- `generated_*.py` - Generated code
- `*_temp.py` - Temporary execution files
- `code_under_test.py` - Test targets
- `evolved_agent.py` - Evolved agent code

---

## Troubleshooting

**Database errors:**
```bash
rm -f data/memory.db
```

**Import errors:**
```bash
pip install -r requirements.txt
```

**Playwright errors (RPA demo):**
```bash
playwright install chromium
```
