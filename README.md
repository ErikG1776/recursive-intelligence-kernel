# Recursive Intelligence Algorithm (RIA)

> **Self-improving AI systems that learn, adapt, and evolve autonomously.**

---

## What is RIA?

**Recursive Intelligence Algorithm** is an engineering paradigm where AI systems improve themselves through continuous feedback loops:

```
Observe → Reason → Act → Reflect → Adapt → (repeat)
```

Unlike traditional AI that requires retraining, RIA systems:
- **Learn from failures** in real-time
- **Evolve strategies** based on outcomes
- **Self-modify code** to improve performance
- **Accumulate knowledge** across sessions

---

## Why This Matters

| Traditional AI | Recursive Intelligence |
|----------------|------------------------|
| Static after training | Continuously improves |
| Fails on edge cases | Learns from failures |
| Requires human intervention | Self-healing |
| One-size-fits-all | Adapts to context |

**Commercial Applications:**
- Self-healing automation (RPA that survives UI changes)
- Adaptive web scrapers (handles site redesigns)
- Autonomous code repair (finds and fixes bugs)
- Evolving game AI (improves with each game)

---

## Quick Start

### Run a Demo (30 seconds)

```bash
# Clone the repo
git clone https://github.com/ErikG1776/recursive-intelligence-kernel.git
cd recursive-intelligence-kernel

# Install dependencies
pip install -r requirements.txt

# Run the self-evolving snake game
python demos/snake_evolution.py --auto --games 30
```

You'll see an agent evolve from random movement (0 avg score) to pathfinding (60+ avg score) in under a minute.

### Run the Core API

```bash
# Start the RIA API server
uvicorn rik_api:app --reload

# In another terminal, run a task
curl -X POST http://localhost:8000/run_task \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Analyze and improve"}'
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  META-CONTROLLER                     │
│         (Evaluates fitness, manages rollback)        │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ REASONING │  │  MEMORY   │  │ EXECUTION │
│  ENGINE   │  │  SYSTEMS  │  │   LAYER   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     ▼
           ┌─────────────────┐
           │ FALLBACK SYSTEM │
           │  (Self-healing) │
           └─────────────────┘
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized configuration and logging |
| `db.py` | SQLite connection pooling and management |
| `memory.py` | Episodic, semantic, and procedural memory |
| `reasoning.py` | Task validation, abstraction, planning |
| `meta.py` | Fitness evaluation, rollback, architecture |
| `execution.py` | Concurrent execution with locks |
| `rik_api.py` | FastAPI REST endpoints |

---

## Demo Suite

We've built **12 demos** proving RIA works across domains:

### Core Concepts
| Demo | What It Shows | Run Command |
|------|---------------|-------------|
| **Maze Solver** | Strategy evolution for pathfinding | `python demos/self_evolving_maze_solver.py --auto` |
| **Snake Game** | Agent learns to play snake | `python demos/snake_evolution.py --auto` |
| **Meta-Evolving Agent** | Agent rewrites its own architecture | `python demos/meta_evolving_agent.py --auto` |

### Self-Healing Systems
| Demo | What It Shows | Run Command |
|------|---------------|-------------|
| **Adaptive Scraper** | Web scraper survives site changes | `python demos/adaptive_scraper.py --auto` |
| **Self-Healing RPA** | UI automation survives redesigns | `python demos/self_healing_rpa.py --auto` |
| **USASpending Demo** | Live RPA on federal government site | `python usaspending_demo.py --visible` |

### Production RPA Engine
| File | Description |
|------|-------------|
| `rpa_engine.py` | Production-ready self-healing RPA engine with 9 locator strategies |
| `usaspending_demo.py` | Live demo on USASpending.gov (real federal site) |

### Autonomous Code Evolution
| Demo | What It Shows | Run Command |
|------|---------------|-------------|
| **Self-Debugging Agent** | Finds and fixes code bugs | `python demos/self_debugging_agent.py --auto` |
| **Autonomous Bug Fixer** | Repairs failing tests | `python demos/autonomous_bugfixer.py --auto` |
| **Self-Evolving Repo** | Codebase improves itself | `python demos/self_evolving_repo.py --auto` |

### Multi-Agent Systems
| Demo | What It Shows | Run Command |
|------|---------------|-------------|
| **Adversarial Evolution** | Two agents strengthen each other | `python demos/adversarial_evolution.py --auto` |
| **Multi-Agent Co-Design** | 4 agents collaborate on a system | `python demos/multi_agent_codesign.py --auto` |
| **Recursive Self-Replication** | Agent creates improved copies of itself | `python demos/recursive_self_replication.py --auto` |

---

## SDK Usage

```python
from rik_sdk.client import RIKClient

# Connect to RIA
rik = RIKClient(base_url="http://127.0.0.1:8000")

# Run a task
result = rik.run_task("Optimize this process")

# Get system metrics
metrics = rik.get_metrics()

# Query memory
memory = rik.get_memory()
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run_task` | POST | Execute a reasoning task |
| `/metrics` | GET | Get system performance metrics |
| `/memory` | GET | Query episodic memory |
| `/fitness_history` | GET | Get fitness score history |
| `/health` | GET | Health check |

---

## Project Structure

```
recursive-intelligence-kernel/
├── config.py          # Configuration
├── db.py              # Database management
├── memory.py          # Memory systems
├── reasoning.py       # Reasoning engine
├── meta.py            # Meta-controller
├── execution.py       # Execution layer
├── rik_api.py         # REST API
├── main.py            # Entry point
│
├── rpa_engine.py      # Production self-healing RPA engine
├── usaspending_demo.py # Live demo on federal site
│
├── demos/             # 12 demonstration scripts
│   ├── snake_evolution.py
│   ├── multi_agent_codesign.py
│   └── ...
│
├── rik_sdk/           # Python SDK
│   └── client.py
│
├── rik_fail_safe/     # Fallback/recovery system
│   └── fallback_core.py
│
└── data/
    └── memory.db      # Persistent memory
```

---

## Key Concepts

### 1. Episodic Memory
Every action is recorded with context and outcome:
```python
save_episode(
    task="navigate_to_cart",
    result="success",
    reflection="Used CSS selector after ID failed"
)
```

### 2. Strategy Evolution
Agents maintain multiple strategies and evolve based on performance:
```python
strategies = ["basic", "advanced", "optimized"]
# Agent evolves: basic (60%) → advanced (80%) → optimized (95%)
```

### 3. Fitness Evaluation
Every run is scored on efficiency, robustness, and goal achievement:
```python
fitness = evaluate_fitness()
# {"efficiency": 0.92, "robustness": 0.85, "score": 0.88}
```

### 4. Rollback & Recovery
Failed experiments can be rolled back to last known good state:
```python
rollback_to_generation(gen_id=5)  # Restore generation 5
```

---

## Requirements

```
Python 3.8+
FastAPI
uvicorn
SQLite3
scikit-learn
numpy
networkx
beautifulsoup4 (for web demos)
playwright (for RPA demos)
```

Install all:
```bash
pip install -r requirements.txt
```

---

## Commercial Opportunities

### Immediate Applications
1. **Self-Healing RPA** - Automation that survives UI changes
2. **Adaptive Web Scraping** - Scrapers that fix themselves
3. **Autonomous Testing** - Tests that evolve with the codebase
4. **Dynamic API Clients** - Clients that adapt to API changes

### Enterprise Value
- **Reduced maintenance** - Systems fix themselves
- **Higher reliability** - Learning from every failure
- **Faster adaptation** - No manual updates needed
- **Continuous improvement** - Gets better over time

### Integration Paths
- **SaaS product** - Hosted RIA service
- **SDK licensing** - Embed in existing products
- **Consulting** - Custom RIA implementations
- **Research partnerships** - Academic collaborations

---

## License

MIT License © 2025 Erik Galardi

---

## Citation

If you use RIA in research or products:

> *Recursive Intelligence Algorithm (RIA) — Erik Galardi (2025)*
> github.com/ErikG1776/recursive-intelligence-kernel

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Run tests: `python integration_test.py`
4. Submit a PR

---

## Contact

- GitHub: [@ErikG1776](https://github.com/ErikG1776)
- Project: [recursive-intelligence-kernel](https://github.com/ErikG1776/recursive-intelligence-kernel)
