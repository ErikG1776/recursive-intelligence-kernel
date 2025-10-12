# 🧠 Recursive Intelligence Kernel (RIK) v5.0
Autonomous, self-evaluating agent kernel for recursive intelligence research.

---

## 🚀 Deployment Overview
RIK v5.0 runs as a Docker service with two main components:
- **rik-agent** → Core recursive intelligence kernel (meta, reasoning, memory, fallback)
- **watchdog** → Lightweight process that monitors the kernel’s runtime and kills runaway loops

---

## 🐋 Docker Compose Quick Start

### 1️⃣ Build and Run
```bash
docker compose up --build -d