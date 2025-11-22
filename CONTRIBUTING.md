# Contributing to RIK - Engineer Onboarding Guide

This guide helps new engineers understand the Recursive Intelligence Kernel (RIK) codebase and get productive quickly.

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# Or install individual packages:
pip install fastapi uvicorn jsonschema scikit-learn networkx beautifulsoup4 matplotlib
```

### 2. Run Integration Test
```bash
python3 integration_test.py
```
This validates all subsystems work together. Expected output includes fitness metrics and database table confirmations.

### 3. Start the API
```bash
python3 rik_api.py
# API runs on http://0.0.0.0:8000
```

### 4. Run the Demo
```bash
python3 demos/live_agi_ui_navigator.py
```

---

## Project Architecture

### Core Modules (in order of execution flow)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | Entry point orchestrator | `recursive_run(task)` |
| `reasoning.py` | Task validation & abstraction | `validate_task_schema()`, `create_abstractions()`, `validate_analogy()` |
| `memory.py` | Multi-type persistence | `save_episode()`, `get_recent_episodes()`, `retrieve_context()` |
| `meta.py` | Fitness & rollback | `evaluate_fitness()`, `apply_modification()`, `rollback()`, `visualize_architecture()` |
| `execution.py` | Concurrency control | `sqlite_lock()`, `execute_with_lock()` |

### Fail-Safe Subsystem (`rik_fail_safe/`)

| File | Purpose |
|------|---------|
| `fallback_core.py` | Core diagnosis → strategy → execute pipeline |
| `api_integration.py` | API error handling |
| `selenium_integration.py` | Selenium browser automation recovery |
| `playwright_integration.py` | Playwright browser automation recovery |

### Supporting Files

| File | Purpose |
|------|---------|
| `rik_api.py` | FastAPI REST endpoints |
| `self_updating_confidence.py` | Bayesian weight calibration |
| `runtime_learning_injector.py` | Inject learned weights at runtime |
| `integration_test.py` | Full system validation |

---

## Cognitive Feedback Loop

The core RIK loop follows this pattern:

```
1. RECEIVE TASK
   ↓
2. RETRIEVE CONTEXT (memory.retrieve_context)
   ↓
3. CREATE ABSTRACTIONS (reasoning.create_abstractions)
   ↓
4. EXECUTE TASK
   ↓
5. [ON FAILURE] → FALLBACK SYSTEM
   - diagnose() → generate_strategies() → simulate_counterfactuals() → execute_best_strategy()
   ↓
6. SAVE EPISODE (memory.save_episode)
   ↓
7. EVALUATE FITNESS (meta.evaluate_fitness)
   ↓
8. LOOP
```

---

## Database Schema

All data persisted in `data/memory.db` (SQLite).

### Core Tables

```sql
-- Task execution history
episodes (id, timestamp, task, result, reflection)

-- System modifications for rollback
modifications (id, component, change_description, rollback_code, applied_code,
               performance_before, performance_after, timestamp)

-- Learned strategy effectiveness
strategy_weights (id, strategy, success_rate, avg_confidence, last_updated)

-- Discovered task patterns
abstractions (id, name, definition, timestamp)

-- System performance metrics
architecture (id, version, efficiency, robustness, fitness_score, timestamp)

-- Strategy tracking for learning
episodic_memory (id, timestamp, strategy, predicted_success, actual_outcome, context)
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run_task` | POST | Execute recursive reasoning task |
| `/metrics` | GET | Get current fitness metrics |
| `/memory` | GET | Retrieve recent episodes |

### Example Usage
```bash
# Run a task
curl -X POST http://localhost:8000/run_task \
  -H "Content-Type: application/json" \
  -d '{"task": "Demonstrate recursive reflection"}'

# Get metrics
curl http://localhost:8000/metrics

# Get memory
curl http://localhost:8000/memory
```

---

## Task Grammar

Tasks are represented as directed acyclic graphs (DAGs):

```json
{
  "nodes": [
    {"id": "1", "primitive": "locate", "params": {"selector": "#input"}},
    {"id": "2", "primitive": "execute", "params": {"action": "click"}}
  ],
  "edges": [
    {"from": "1", "to": "2", "condition": "always"}
  ]
}
```

**Primitives:** `locate`, `transform`, `validate`, `execute`

---

## Demo Guide

### Live AGI UI Navigator

Demonstrates semantic UI perception and self-healing navigation.

```bash
# Run with bundled sample
python3 demos/live_agi_ui_navigator.py

# Run against a URL
python3 demos/live_agi_ui_navigator.py https://example.com --goal "log in"

# Export trace as JSON
python3 demos/live_agi_ui_navigator.py --format json --save trace.json
```

**What it demonstrates:**
- DOM element extraction with semantic labels
- Intent matching (ranks UI candidates for goals)
- Action chain planning (click → fill → validate)
- Self-healing (rescans DOM when primary action fails)

---

## Key Design Patterns

### 1. Context Manager for DB Locking
```python
with sqlite_lock() as conn:
    conn.execute("INSERT INTO ...")
# Automatic commit/rollback and connection cleanup
```

### 2. Fallback Pipeline
```python
diagnosis = diagnose(error, context)
strategies = generate_strategies(diagnosis)
simulations = simulate_counterfactuals(strategies)
result = execute_best_strategy(simulations)
```

### 3. Episodic Memory Pattern
```python
save_episode(task, result, reflection)  # After each run
context = retrieve_context(task)         # Before next run
```

---

## Testing

### Run All Tests
```bash
python3 integration_test.py
```

### Test Individual Modules
```bash
python3 reasoning.py      # Test grammar validation & analogy
python3 memory.py         # Test memory operations
python3 meta.py           # Test fitness & visualization
python3 execution.py      # Test concurrency locking
python3 rik_fail_safe/fallback_core.py  # Test fallback pipeline
```

---

## Common Tasks

### Add a New Fallback Strategy
1. Edit `rik_fail_safe/fallback_core.py`
2. Add condition in `generate_strategies()`
3. Test with `python3 rik_fail_safe/fallback_core.py`

### Add a New Primitive
1. Edit `reasoning.py`
2. Add to `TASK_GRAMMAR["nodes"]["items"]["properties"]["primitive"]["enum"]`
3. Implement handler in execution layer

### Extend Memory Schema
1. Edit `memory.py` → `init_memory_db()`
2. Add new table creation
3. Add corresponding save/retrieve functions

---

## Troubleshooting

### "No such table" errors
Run `python3 memory.py` to initialize the database tables.

### Import errors
Ensure you're running from the project root directory.

### Demo not finding elements
Check that `data/sample_login_page.html` exists for local demo.

---

## Code Style

- Use type hints for function signatures
- Follow existing docstring format (module header + function docs)
- Prefix print statements with context: `[RIK]`, `[MEMORY]`, `[🩺]`, etc.
- Keep functions focused and under 50 lines when possible

---

## Architecture Diagram

Generate the current architecture visualization:
```bash
python3 meta.py
# Creates: architecture_diagram.mmd
```

View in any Mermaid-compatible renderer (GitHub, VS Code plugin, etc.)

---

## Questions?

- Review `README.md` for high-level overview
- Check individual module docstrings for implementation details
- Run integration test to verify system health
