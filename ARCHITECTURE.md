# RIK Architecture
## Technical Design & Implementation Guide

**For Engineers Building or Extending RIK**

---

## 🎯 High-Level Overview

RIK is a **stateful reasoning API** that processes automation exceptions through a multi-layer architecture combining symbolic AI reasoning with episodic memory.

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│     (Python SDK, JavaScript, C#, UiPath, Zapier, etc.)       │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Middleware: Request ID, Logging, Auth, Rate Limiting   │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Endpoints: /process_invoice, /recover_selector, etc.  │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
┌─────────────────┐ ┌────────────┐ ┌──────────────┐
│ Exception       │ │ Reasoning  │ │ Memory       │
│ Detection       │ │ Engine     │ │ System       │
│                 │ │            │ │              │
│ - Schema Val.   │ │ - Retrieve │ │ - SQLite DB  │
│ - Field Check   │ │ - Simulate │ │ - Episodes   │
│ - Rule Engine   │ │ - Decide   │ │ - Similarity │
└─────────────────┘ └────────────┘ └──────────────┘
          │              │              │
          └──────────────┼──────────────┘
                         ↓
          ┌──────────────────────────┐
          │  Decision + Confidence   │
          │  + Reasoning Explanation │
          └──────────────────────────┘
```

---

## 📦 Core Components

### 1. API Layer (`rik_api.py`)

**Purpose:** RESTful API server with production-grade middleware

**Tech Stack:**
- **FastAPI** - ASGI web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Request/response validation

**Key Features:**
```python
# Middleware Stack (runs on every request)
1. Request ID Generation  → Unique ID for tracing
2. Performance Timing     → Measure request duration
3. CORS                   → Cross-origin support
4. Authentication         → API key validation (optional)
5. Rate Limiting          → Per-client throttling
```

**Endpoints:**

| Endpoint | Purpose | Handler |
|----------|---------|---------|
| `/process_invoice` | Invoice exception handling | `invoice_processor.process_invoice()` |
| `/recover_selector` | Web scraper self-healing | Web selector recovery logic |
| `/test_selector` | Selector validation | BeautifulSoup/lxml testing |
| `/health` | Detailed health check | Subsystem status checks |
| `/health/live` | Kubernetes liveness | Simple alive check |
| `/health/ready` | Kubernetes readiness | Database connectivity |
| `/metrics` | Performance metrics | Meta-controller fitness |
| `/invoice_stats` | ROI statistics | Memory aggregation |
| `/version` | Version info | Config version/env |
| `/memory` | Memory episodes | SQLite query |

**File:** `rik_api.py` (900+ lines)

---

### 2. Invoice Processor (`invoice_processor.py`)

**Purpose:** Intelligent exception handler for invoice processing

**Architecture:**

```python
def process_invoice(invoice_data):
    # Step 1: Exception Detection
    exceptions = detect_exceptions(invoice_data)
    # Found: Missing PO, Low confidence, Unknown vendor, etc.

    # Step 2: Retrieve Similar Cases from Memory
    similar_cases = memory.get_similar_cases(exceptions)
    # Finds: 3 cases with similar patterns

    # Step 3: Simulate Resolution Strategies
    strategies = [
        {"action": "approve", "condition": "trusted_vendor"},
        {"action": "escalate", "condition": "high_risk"}
    ]
    outcomes = simulate_strategies(strategies, invoice_data, similar_cases)

    # Step 4: Select Best Strategy
    best_strategy = max(outcomes, key=lambda x: x['confidence'])

    # Step 5: Execute & Store in Memory
    decision = execute_strategy(best_strategy)
    memory.store_episode(invoice_data, decision, exceptions)

    return {
        "final_action": decision.action,
        "confidence_score": decision.confidence,
        "reasoning": decision.explanation,
        "exceptions_found": len(exceptions),
        "exceptions_resolved": count_resolved(exceptions)
    }
```

**Exception Types Detected:**
1. **Missing Fields** - PO number, vendor name, amount
2. **Low Confidence** - OCR extraction confidence <95%
3. **Unknown Vendor** - Not in master vendor list
4. **Amount Threshold** - Exceeds approval limits
5. **Duplicate Detection** - Invoice number already processed

**Decision Logic:**
```python
if amount < AUTO_APPROVE_THRESHOLD and vendor in TRUSTED_VENDORS:
    return "approve"
elif any_high_risk_indicators:
    return "escalate"
else:
    return "reject"
```

**File:** `invoice_processor.py` (450+ lines)

---

### 3. Memory System (`memory.py`)

**Purpose:** Persistent episodic memory for learning and similarity matching

**Database Schema:**
```sql
CREATE TABLE memory_episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    task TEXT NOT NULL,
    result TEXT,
    confidence REAL,
    exceptions_found INTEGER,
    exceptions_resolved INTEGER,
    similar_cases_count INTEGER,
    metadata TEXT  -- JSON blob
);
```

**Key Operations:**

```python
# Store new episode
memory.store_episode(
    task="process_invoice",
    result="approved",
    confidence=0.92,
    exceptions_found=2,
    exceptions_resolved=2,
    metadata={"invoice_id": "INV-001", "vendor": "Acme"}
)

# Retrieve similar cases (TF-IDF similarity)
similar = memory.get_similar_cases(
    current_exceptions=["missing_po", "low_confidence"],
    limit=5
)
# Returns: List of past episodes with similar exception patterns

# Get statistics
stats = memory.get_episode_statistics()
# Returns: Total episodes, success rate, avg confidence, etc.
```

**Similarity Algorithm:**
- **TF-IDF Vectorization** - Convert exception patterns to vectors
- **Cosine Similarity** - Measure similarity between cases
- **Recency Weighting** - Prefer recent cases (exponential decay)

**File:** `memory.py` (800+ lines)

---

### 4. Reasoning Engine (`reasoning.py`)

**Purpose:** Core reasoning logic for task decomposition and strategy simulation

**Key Functions:**

```python
# Task Decomposition
def decompose_task(task_description):
    """Break complex task into subtasks"""
    # Uses LLM or rule-based decomposition
    return [subtask1, subtask2, subtask3]

# Strategy Simulation
def simulate_strategy(strategy, context, memory):
    """Predict outcome of strategy before execution"""
    # Retrieves similar past cases
    # Calculates probability of success
    # Returns confidence score
    return {
        "confidence": 0.87,
        "predicted_outcome": "success",
        "risk_factors": ["amount_high"]
    }

# Decision Making
def make_decision(strategies, confidences):
    """Select best strategy based on confidence"""
    best = max(zip(strategies, confidences), key=lambda x: x[1])
    return best[0]
```

**Reasoning Pipeline:**
```
Input (Exception Context)
    ↓
1. Context Understanding
    - Parse exception details
    - Extract relevant features
    ↓
2. Memory Retrieval
    - Find similar past cases
    - Calculate similarity scores
    ↓
3. Strategy Generation
    - List possible actions
    - Evaluate feasibility
    ↓
4. Outcome Simulation
    - Predict result of each strategy
    - Calculate confidence scores
    ↓
5. Decision Selection
    - Pick highest confidence strategy
    - Generate explanation
    ↓
Output (Decision + Reasoning)
```

**File:** `reasoning.py` (1000+ lines)

---

### 5. Configuration System (`config.py`)

**Purpose:** Centralized environment-based configuration

**Pattern:** Singleton configuration class with validation

```python
class Config:
    # Environment
    ENVIRONMENT = os.getenv("RIK_ENV", "development")

    # API Server
    API_HOST = os.getenv("RIK_API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("RIK_API_PORT", "8000"))

    # Security
    API_KEY_ENABLED = os.getenv("RIK_API_KEY_ENABLED", "false") == "true"
    API_KEYS = parse_csv(os.getenv("RIK_API_KEYS", ""))

    # Business Rules
    AUTO_APPROVE_THRESHOLD = float(os.getenv("RIK_AUTO_APPROVE_THRESHOLD", "5000.0"))
    TRUSTED_VENDORS = parse_csv(os.getenv("RIK_TRUSTED_VENDORS", "Acme,TechCo"))

    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        if cls.API_KEY_ENABLED and not cls.API_KEYS:
            raise ValueError("API keys required when auth enabled")
```

**Environment Files:**
- `config/development.env` - Local development
- `config/staging.env` - Staging environment
- `config/production.env` - Production environment
- `.env.example` - Template with all options

**File:** `config.py` (250 lines)

---

### 6. Logging System (`logging_config.py`)

**Purpose:** Structured JSON logging with request tracing

**Format:**
```json
{
  "timestamp": "2024-11-01T12:34:56.789Z",
  "level": "INFO",
  "logger": "rik_api",
  "message": "Processing invoice INV-001",
  "request_id": "req_abc123",
  "module": "invoice_processor",
  "function": "process_invoice",
  "line": 142,
  "duration_seconds": 0.084,
  "invoice_id": "INV-001",
  "final_action": "approve"
}
```

**Key Features:**
- **Request ID Tracking** - Trace request across components
- **Structured Fields** - Easy log aggregation/querying
- **Performance Timing** - Automatic duration logging
- **Context Manager** - `with LogTimer()` for easy timing

```python
from logging_config import get_logger, LogTimer

logger = get_logger(__name__)

with LogTimer(logger, "process_invoice", {"invoice_id": "INV-001"}):
    result = process_invoice(data)
    # Automatically logs duration on exit
```

**File:** `logging_config.py` (300 lines)

---

## 🔄 Data Flow

### Invoice Processing Flow

```
1. HTTP Request Arrives
   POST /process_invoice
   Body: {"pdf_content": "{...}", "invoice_id": "INV-001"}
   ↓
2. Middleware Processing
   - Generate request_id: "req_abc123"
   - Start performance timer
   - Validate API key (if enabled)
   - Check rate limit
   ↓
3. Request Validation (Pydantic)
   - Validate JSON schema
   - Check required fields
   - Sanitize inputs
   ↓
4. Invoice Processing
   a) Parse invoice data from PDF content
   b) Detect exceptions:
      - Missing PO number ✓
      - Low OCR confidence ✓
   c) Query memory for similar cases:
      - Found 3 similar cases
      - Similarity scores: [0.87, 0.82, 0.79]
   d) Simulate strategies:
      Strategy 1: Auto-approve (confidence: 0.92)
      Strategy 2: Escalate (confidence: 0.65)
   e) Select best strategy: Auto-approve (0.92)
   f) Generate reasoning explanation
   ↓
5. Store in Memory
   - Save episode to SQLite
   - Update statistics
   ↓
6. Response Generation
   {
     "invoice_id": "INV-001",
     "final_action": "approve",
     "confidence_score": 0.92,
     "reasoning": "Auto-approve: Amount $4,500 under threshold...",
     "exceptions_found": 2,
     "exceptions_resolved": 2,
     "processing_time_seconds": 0.084
   }
   ↓
7. Middleware Cleanup
   - Log response (with request_id)
   - Record performance metrics
   - Add response headers
   ↓
8. HTTP Response (200 OK)
   Total time: 84ms
```

---

## 🗄️ Database Schema

**SQLite Database:** `data/memory.db`

### memory_episodes Table

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `timestamp` | TEXT | ISO 8601 timestamp |
| `task` | TEXT | Task type (e.g., "process_invoice") |
| `result` | TEXT | Task result/outcome |
| `confidence` | REAL | Confidence score (0.0-1.0) |
| `exceptions_found` | INTEGER | Number of exceptions detected |
| `exceptions_resolved` | INTEGER | Number auto-resolved |
| `similar_cases_count` | INTEGER | Similar cases retrieved |
| `metadata` | TEXT | JSON blob with extra data |

**Indexes:**
```sql
CREATE INDEX idx_task ON memory_episodes(task);
CREATE INDEX idx_timestamp ON memory_episodes(timestamp);
CREATE INDEX idx_confidence ON memory_episodes(confidence);
```

---

## 🏗️ Design Decisions

### Why FastAPI?
- **Performance:** ASGI async support (high concurrency)
- **Validation:** Built-in Pydantic validation
- **Documentation:** Auto-generated OpenAPI docs
- **Modern:** Native async/await support

### Why SQLite?
- **Simplicity:** No separate database server
- **Performance:** Fast for read-heavy workloads
- **Portability:** Single file database
- **Upgrade Path:** Can migrate to PostgreSQL later

### Why TF-IDF for Similarity?
- **Fast:** O(n) similarity calculation
- **Effective:** Good for text-based exception patterns
- **Interpretable:** Can explain why cases are similar
- **Lightweight:** No ML models to maintain

### Why Separate Modules?
- **Testability:** Each module can be tested independently
- **Maintainability:** Clear separation of concerns
- **Scalability:** Can extract modules to microservices
- **Clarity:** Easier for engineers to understand

---

## 🔐 Security Architecture

### Authentication
```python
# Optional API key authentication
if config.API_KEY_ENABLED:
    # Check X-API-Key header
    # Validate against config.API_KEYS list
    # Reject with 401 if invalid
```

### Rate Limiting
```python
# Per-client rate limiting (100 req/min default)
# Uses in-memory counter (can upgrade to Redis)
# Returns 429 if limit exceeded
```

### Input Validation
```python
# Pydantic models validate:
# - Field types (str, int, float)
# - Field constraints (min_length, max_length)
# - Field patterns (regex for IDs)
# - Rejects invalid requests with 422
```

### CORS
```python
# Configurable CORS for browser access
# Default: Allow all origins in development
# Production: Restrict to specific domains
```

---

## 📈 Performance Considerations

### Request Processing Time Breakdown

```
Total: ~84ms

1. Network/HTTP parsing:        ~5ms
2. Middleware (auth, logging):   ~3ms
3. Request validation:           ~2ms
4. Invoice parsing:              ~8ms
5. Exception detection:          ~12ms
6. Memory retrieval:             ~15ms  (SQLite query + similarity calc)
7. Strategy simulation:          ~25ms  (most expensive)
8. Decision making:              ~4ms
9. Memory storage:               ~6ms
10. Response serialization:      ~4ms
```

**Optimization Targets:**
- Memory retrieval: Add caching layer (Redis)
- Strategy simulation: Parallelize simulations
- Database writes: Batch writes every N requests

### Scalability

**Current Capacity:**
- **Single Instance:** ~100 req/s
- **CPU Bound:** Strategy simulation is main bottleneck
- **Memory:** ~50MB base + ~5MB per 1000 episodes

**Scaling Options:**
1. **Horizontal:** Run multiple instances behind load balancer
2. **Database:** Migrate to PostgreSQL for better concurrency
3. **Caching:** Add Redis for memory query caching
4. **Async:** Make strategy simulation fully async

---

## 🧪 Testing Strategy

### Unit Tests
```bash
pytest tests/test_memory.py          # Memory system tests
pytest tests/test_reasoning.py       # Reasoning engine tests
pytest tests/test_invoice.py         # Invoice processing tests
```

### Integration Tests
```bash
pytest tests/test_api.py             # API endpoint tests
pytest tests/test_end_to_end.py      # Full flow tests
```

### Performance Tests
```bash
python3 benchmarks/performance_test.py
```

### Manual Testing
```bash
# Start API
python3 rik_api.py

# Run SDK examples
python3 rik_sdk/examples/invoice_processing.py
```

---

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Python 3.11
├── SQLite database (data/memory.db)
├── Logs to console + files
└── No authentication
```

### Production
```
                  ┌─────────────┐
                  │ Load Balancer│
                  │  (nginx)     │
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
    ┌─────────┐    ┌─────────┐   ┌─────────┐
    │ RIK API │    │ RIK API │   │ RIK API │
    │ Instance│    │ Instance│   │ Instance│
    │  (Pod)  │    │  (Pod)  │   │  (Pod)  │
    └────┬────┘    └────┬────┘   └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        ↓
               ┌────────────────┐
               │  PostgreSQL    │
               │  (Shared DB)   │
               └────────────────┘
```

**See:** `DEPLOYMENT.md` for complete guide

---

## 🔧 Extension Points

### Adding New Exception Types

```python
# In invoice_processor.py

def detect_exceptions(invoice_data):
    exceptions = []

    # Existing checks...

    # Add new check
    if invoice_data.get('currency') not in SUPPORTED_CURRENCIES:
        exceptions.append({
            "type": "unsupported_currency",
            "severity": "medium",
            "value": invoice_data.get('currency')
        })

    return exceptions
```

### Adding New Endpoints

```python
# In rik_api.py

@app.post("/process_receipt", tags=["Receipt Processing"])
async def process_receipt(request: ReceiptProcessRequest):
    """Process receipt with exception handling"""
    logger.info(f"Processing receipt {request.receipt_id}")

    result = receipt_processor.process(request.pdf_content)

    return {
        "receipt_id": request.receipt_id,
        "final_action": result.action,
        "confidence_score": result.confidence
    }
```

### Adding New SDKs

1. Follow pattern from existing SDKs (Python, JavaScript, C#)
2. Implement all core endpoints
3. Add error handling
4. Create examples
5. Write documentation

---

## 📚 Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `rik_api.py` | 900+ | Main API server |
| `invoice_processor.py` | 450+ | Invoice exception handler |
| `memory.py` | 800+ | Episodic memory system |
| `reasoning.py` | 1000+ | Core reasoning engine |
| `config.py` | 250 | Configuration management |
| `logging_config.py` | 300 | Structured logging |
| `rik_sdk/client.py` | 435 | Python SDK client |
| `rik_sdk/models.py` | 200 | Type-safe models |
| `rik_sdk/exceptions.py` | 100 | Custom exceptions |

---

## 🎯 Understanding the Code

### Start Here (Recommended Reading Order):

1. **GETTING_STARTED.md** - Understand what RIK does (5 min)
2. **This file (ARCHITECTURE.md)** - Understand how RIK works (15 min)
3. **config.py** - See configuration options (5 min)
4. **rik_api.py** - See API endpoints (10 min)
5. **invoice_processor.py** - See core logic (15 min)
6. **memory.py** - See memory system (10 min)
7. **rik_sdk/client.py** - See how to use RIK (5 min)

**Total:** ~65 minutes to understand the entire system

---

## 🤔 Common Questions

### Q: Can RIK handle multiple types of documents?
**A:** Currently optimized for invoices, but extensible. Add new processors similar to `invoice_processor.py`.

### Q: How does RIK learn from past decisions?
**A:** Stores episodes in SQLite, retrieves similar cases using TF-IDF similarity, uses past outcomes to inform decisions.

### Q: What happens if RIK makes a wrong decision?
**A:** Low-confidence decisions are escalated to humans. Escalation threshold is configurable (default: <70% confidence).

### Q: Can RIK integrate with my ERP system?
**A:** Yes, RIK is API-first. Call RIK from your ERP integration code, then pass RIK's decision back to your ERP.

### Q: How accurate is RIK?
**A:** Currently 92% automation rate vs 60% traditional RPA. Accuracy improves as memory grows.

### Q: Can I self-host RIK?
**A:** Yes! RIK is fully self-hosted. See `DEPLOYMENT.md` for Docker/K8s deployment.

---

## 🚀 Next Steps

1. **Read the code:** Start with `rik_api.py`
2. **Run the examples:** Try SDK examples
3. **Understand the flow:** Read "Data Flow" section above
4. **Experiment:** Modify exception detection logic
5. **Extend:** Add new features (see Extension Points)

**For remaining work:** See `PRODUCTIZATION_ROADMAP.md`
