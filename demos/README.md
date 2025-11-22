# RIK Demo Suite

Visual demonstrations of the Recursive Intelligence Kernel's cognitive RPA capabilities.

## Quick Start

```bash
# Install dependencies
pip install selenium sentence-transformers scikit-learn numpy

# Install ChromeDriver (Ubuntu/Debian)
sudo apt-get install chromium-chromedriver

# Or download from: https://chromedriver.chromium.org/downloads

# Run the demo
python demos/cognitive_rpa_demo.py
```

## What This Demo Shows

### Traditional RPA vs RIK Cognitive RPA

| Feature | Traditional RPA | RIK |
|---------|----------------|-----|
| Failure handling | Hardcoded try/catch | Dynamic diagnosis + strategy generation |
| Learning | None | Episodic memory across tasks |
| Task understanding | Keyword matching | Semantic embeddings (384-dim) |
| Recovery selection | Sequential fallback list | Counterfactual simulation |
| Self-evaluation | None | Fitness scoring |

### Demo Flow

1. **Invoice Extraction (ACME)** - Basic task, establishes baseline fitness
2. **Invoice Extraction (TechSupply)** - Shows cross-task learning from similar task
3. **PO Validation (Intentional Failure)** - Element hidden, triggers self-healing:
   - 🩺 Diagnosis: Identifies NoSuchElementException
   - ⚙️ Strategies: Generates 3 recovery options
   - 🔮 Simulation: Predicts success probability for each
   - 🚀 Execution: Picks and runs best strategy
4. **View Details** - Shows improved fitness after learning

## Key Visual Moments

Watch for these in the terminal:

```
[🧠 EMBEDDING] Task embedded to 384-dim semantic space
[🔄 TRANSFER] Learning from similar task
[🔮 SIMULATING] Predicting outcomes...
   [████████████████░░░░] 0.85 - Use semantic selector matching ← BEST
   [███████████░░░░░░░░░] 0.62 - Try alternative CSS selector
   [██████████████░░░░░░] 0.71 - Wait for dynamic content
[📈 FITNESS] 0.500 → 0.750 (↑ +0.250)
```

## Files

- `cognitive_rpa_demo.py` - Main Selenium demo with RIK cognitive loop
- `invoice_portal.html` - Local invoice web app for reliable demos
- `invoice_processing_demo.py` - CLI-only demo (no browser)

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver

## Troubleshooting

**ChromeDriver version mismatch:**
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads
```

**Headless mode:**
```python
# In cognitive_rpa_demo.py, change:
bot.start_browser(headless=True)
```

## For Presentations

1. Run demo on external monitor
2. Terminal should be visible alongside browser
3. Press ENTER to advance between tasks
4. Key talking points at each step are in the summary
