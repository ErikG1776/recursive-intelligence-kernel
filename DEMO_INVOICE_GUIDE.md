# 🧠 RIK Invoice Exception Handler - Live Demo Guide

**The Killer Demo That Shows RIK Doing What Traditional RPA Cannot**

This demo showcases RIK solving the #1 RPA failure mode: **Exception Handling**

Traditional RPA: 40% exception rate → 100% manual intervention
**RIK: 40% exception rate → 80% auto-resolved through reasoning**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Complete Setup](#complete-setup)
3. [Live Demo Script (8 Minutes)](#live-demo-script)
4. [Exception Scenarios](#exception-scenarios)
5. [ROI Calculator](#roi-calculator)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## ⚡ Quick Start

```bash
# Terminal 1: Start RIK API
cd recursive-intelligence-kernel
python3 rik_api.py

# Terminal 2: Start n8n
npx n8n

# Browser: Import workflow
# 1. Open http://localhost:5678
# 2. Click "Import from File"
# 3. Select: n8n_workflows/rik_invoice_exception_handler.json
# 4. Configure Google Sheets credentials
# 5. Activate workflow
```

**Demo ready in 5 minutes!**

---

## 🛠️ Complete Setup

### Prerequisites

- ✅ RIK API running on port 8000
- ✅ n8n installed (cloud or local)
- ✅ Google Sheets account (for logging)
- ✅ Sample invoices in `sample_invoices/` folder

### Step 1: Start RIK API

```bash
cd recursive-intelligence-kernel
python3 rik_api.py
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "5.4.0",
  "features": ["invoice_processing", "exception_handling", ...]
}
```

### Step 2: Set Up Google Sheets

1. Create a new Google Sheet named **"RIK Invoice Log"**
2. Add these column headers in Row 1:
   ```
   Timestamp | Invoice_ID | Vendor | Amount | Exceptions_Found | Final_Action | Status | Processing_Time | Traditional_RPA_Would_Fail | Reasoning
   ```
3. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```

### Step 3: Configure n8n Workflow

**Option A: Cloud n8n (Recommended for Live Demo)**

If using cloud n8n (like you did with the scraper demo):

1. Upload sample invoices to a cloud folder (Google Drive, Dropbox, etc.)
2. Modify the workflow "Read Invoice Files" node to watch that folder
3. Ensure RIK API is accessible via ngrok:
   ```bash
   ngrok http 8000
   ```
4. Update workflow RIK API URL to ngrok URL

**Option B: Local n8n**

1. Import workflow: `n8n_workflows/rik_invoice_exception_handler.json`
2. Configure Google Sheets credentials
3. Update Sheet ID in "Log to Google Sheets" node
4. Ensure `sample_invoices/` folder path is correct

### Step 4: Verify End-to-End

```bash
# Test API directly
curl -X POST http://localhost:8000/process_invoice \
  -H "Content-Type: application/json" \
  -d @sample_invoices/1_standard_invoice.json
```

Expected: JSON response with `"final_action": "approve"`

---

## 🎬 Live Demo Script (8 Minutes)

**Audience:** RPA leadership, decision-makers, technical team
**Objective:** Show RIK handling exceptions that break traditional RPA
**Key Message:** "RIK is a robot with a brain"

### Setup (Before Demo)

- ✅ RIK API running
- ✅ n8n workflow activated
- ✅ Google Sheets open in browser tab
- ✅ Sample invoices ready
- ✅ Terminal visible showing RIK logs

### **Minute 0-1: The Problem Statement**

**Script:**
> "The #1 reason RPA fails is **exceptions**. When something unexpected happens - a missing field, a typo, a new format - traditional RPA bots just stop. They create a ticket, wait for a human, and cost your company time and money.
>
> In invoice processing, **40% of invoices have some exception**. With traditional RPA, that means 40% require manual intervention. That's not automation - that's babysitting robots.
>
> Today I'll show you how RIK changes this."

### **Minute 1-3: Traditional RPA Fails**

**Demo:**
1. Show `2_invoice_no_po.json` on screen
2. Point out: "This invoice is missing a PO number"
3. Explain: "Traditional RPA rule: No PO = reject"

**Script:**
> "Here's a $4,100 invoice from Acme Corporation - a trusted vendor we've worked with for years. But it's missing a PO number.
>
> Traditional RPA sees: **Missing required field → FAIL**
> Creates ticket → human reviews → takes 20 minutes → costs $20
>
> Now watch what RIK does..."

**Demo:**
1. Upload `2_invoice_no_po.json` to watched folder (or trigger manually)
2. Show n8n workflow executing in real-time
3. Point to RIK API logs showing reasoning:

```
[INFO] Invoice processing requested
[🩺] Diagnosed error: Exception → No PO number found on invoice
[🔮] Simulated counterfactuals:
  • Approve: Trusted vendor (Acme Corporation) under $10,000 threshold
  • Auto-generate: Create PO retroactively if under $5,000
  • Escalate: Request PO number from requestor
[SUCCESS] Invoice processed: APPROVE
[INFO] Traditional RPA would have failed - RIK handled 1 exceptions
```

4. Show Google Sheets update:
   - Status: ✅ APPROVED
   - Reasoning: "Trusted vendor, amount under threshold, similar past cases approved"
   - Traditional_RPA_Would_Fail: TRUE

**Script:**
> "RIK **reasoned** about this exception:
> - Vendor is trusted
> - Amount is under $5,000 threshold
> - We've approved 15 similar invoices from Acme in the past
>
> Decision: **Auto-approve**
>
> Processing time: **3 seconds** instead of 20 minutes. No human needed."

### **Minute 3-5: Multiple Exceptions**

**Script:**
> "That was one exception. Let's try something harder - **multiple exceptions** in one invoice."

**Demo:**
1. Show `6_invoice_multiple_exceptions.json`:
   - Vendor typo: "Salesforc Inc" (missing 'e')
   - Missing PO number
   - Amount: $6,200 (over $5K threshold)

**Script:**
> "This invoice has THREE problems:
> 1. Vendor name is misspelled
> 2. No PO number
> 3. Amount over our $5,000 auto-approve limit
>
> Traditional RPA would fail on ALL THREE. Let's see RIK..."

2. Upload the file
3. Show RIK reasoning through ALL exceptions:

```
[INFO] Exceptions found: 3
  Exception 1: vendor_name_typo
    - Detected: "Salesforc Inc" vs "Salesforce Inc" (94% match)
    - Decision: Auto-correct vendor name

  Exception 2: missing_po_number
    - Vendor: Salesforce Inc (trusted)
    - Decision: Would approve, but...

  Exception 3: amount_over_threshold
    - Amount: $6,200 > $5,000 threshold
    - Decision: ESCALATE to manager

[SUCCESS] Final decision: ESCALATE (multiple high-severity exceptions)
```

4. Show Google Sheets:
   - Status: ⚠️ ESCALATED
   - Reasoning: "Vendor corrected to Salesforce Inc, but amount over threshold requires manager approval"

**Script:**
> "RIK handled this intelligently:
> 1. **Auto-corrected** the vendor name typo
> 2. **Would have approved** despite missing PO (trusted vendor)
> 3. **But escalated** because amount exceeds policy
>
> Traditional RPA: Creates 3 separate error tickets
> RIK: **Understands context**, corrects what it can, escalates what it should"

### **Minute 5-7: Show the Learning**

**Script:**
> "Here's the game-changer: **RIK learns from every invoice**."

**Demo:**
1. Call the stats endpoint:
```bash
curl http://localhost:8000/invoice_stats | jq
```

2. Show the output on screen:
```json
{
  "stats": {
    "total_invoices_processed": 247,
    "invoices_with_exceptions": 98,
    "exceptions_auto_resolved": 78,
    "exceptions_escalated": 20,
    "automation_rate": 0.92,
    "traditional_rpa_automation_rate": 0.60
  },
  "roi": {
    "interventions_saved": 78,
    "cost_per_intervention": 20,
    "monthly_savings_usd": 1560,
    "annual_savings_usd": 18720,
    "automation_improvement": "32%"
  }
}
```

**Script:**
> "After processing 247 invoices:
> - 98 had exceptions (40% exception rate - normal for RPA)
> - Traditional RPA automation: **60%** (40% manual intervention)
> - RIK automation: **92%** (only 8% manual intervention)
>
> That's a **32% improvement** in automation rate.
>
> For this volume, RIK saves **$18,720 per year**.
>
> For a company processing **10,000 invoices per month**, that's **$768,000 annual savings**."

### **Minute 7-8: The Closer**

**Script:**
> "This is what makes RIK different from traditional RPA:
>
> ❌ Traditional RPA: Rule-based robot that breaks on exceptions
> ✅ RIK: Reasoning engine that **adapts** to exceptions
>
> We just showed you:
> 1. Missing fields → RIK reasons about policy + vendor trust
> 2. Typos → RIK detects and auto-corrects
> 3. Multiple exceptions → RIK understands context
> 4. Learning → RIK gets smarter with every invoice
>
> This same approach works for ANY RPA use case with exceptions:
> - Purchase orders
> - Customer service emails
> - Data entry variations
> - System changes
>
> **RIK isn't just automation. It's intelligent automation.**
>
> Questions?"

---

## 🎯 Exception Scenarios Deep Dive

### Scenario 1: Missing PO Number

**Business Context:**
- Some trusted vendors don't use POs for recurring services
- Under certain thresholds, POs aren't required
- Traditional RPA can't distinguish - just sees "missing required field"

**How RIK Handles It:**
```python
reasoning = {
    "observation": "No PO number found on invoice",
    "context": {
        "vendor": "Acme Corporation",
        "vendor_trusted": True,
        "amount": 4100.00,
        "threshold": 5000.00,
        "past_episodes": "15 similar invoices from Acme approved"
    },
    "decision": "APPROVE",
    "confidence": 0.92,
    "reasoning": "Trusted vendor under threshold with consistent approval history"
}
```

**Demo Impact:**
- Shows RIK understands **business context**, not just rules
- Demonstrates **learning from history**
- Proves **contextual reasoning**

### Scenario 2: Vendor Name Typo

**Business Context:**
- Manual data entry leads to typos
- Traditional RPA: vendor not found → reject
- Costs 20 minutes to manually verify and correct

**How RIK Handles It:**
```python
diagnosis = {
    "observed": "Vendor 'Microsft Corporation' not in database",
    "similarity_check": {
        "matched": "Microsoft Corporation",
        "confidence": 0.92,
        "matching_factors": [
            "String similarity: 92%",
            "Same address: 1 Microsoft Way, Redmond, WA",
            "Same email: accounts@microsoft.com"
        ]
    },
    "decision": "AUTO_CORRECT",
    "action": "Update vendor to 'Microsoft Corporation', notify accounts payable"
}
```

**Demo Impact:**
- Shows RIK doesn't just follow rigid rules
- Demonstrates **intelligent matching**
- Proves **self-healing capability**

### Scenario 3: New PDF Template

**Business Context:**
- Vendors update invoice templates regularly
- Traditional RPA breaks when template changes
- Requires developer to update extraction rules (2-3 hours)

**How RIK Handles It:**
```python
extraction = {
    "standard_extraction_confidence": 0.45,  # Low!
    "diagnosis": "Template not recognized, field positions changed",
    "fallback_strategy": "Semantic extraction using field labels",
    "extracted_fields": {
        "invoice_number": "2024-INV-8834",
        "amount": 4850.00,
        "vendor": "Google LLC"
    },
    "decision": "APPROVE and ADD_TEMPLATE_TO_LIBRARY",
    "learning": "New template learned for future Google LLC invoices"
}
```

**Demo Impact:**
- Shows RIK **adapts to change** without reprogramming
- Demonstrates **semantic understanding**
- Proves **continuous learning**

### Scenario 4: Amount Over Threshold

**Business Context:**
- Company policy: amounts over $5K need manager approval
- But high-value vendors with history may be exceptions
- Traditional RPA: rigid threshold

**How RIK Handles It:**
```python
analysis = {
    "amount": 12500.00,
    "threshold": 5000.00,
    "over_threshold": True,
    "vendor_context": {
        "vendor": "Amazon Web Services",
        "relationship": "Strategic partner",
        "past_high_amount_invoices": 47,
        "approval_rate": 0.96
    },
    "decision": "ESCALATE_WITH_CONTEXT",
    "message_to_manager": {
        "recommendation": "Approve",
        "reasoning": "AWS strategic partner, 96% of similar invoices approved",
        "risk": "Low - consistent vendor with strong history"
    }
}
```

**Demo Impact:**
- Shows RIK doesn't blindly enforce rules
- Demonstrates **risk assessment**
- Proves **intelligent escalation** (not just rejection)

### Scenario 5: Multiple Exceptions

**Business Context:**
- Real invoices often have multiple issues
- Traditional RPA creates multiple tickets
- Each ticket handled separately → inconsistent decisions

**How RIK Handles It:**
```python
multi_exception_reasoning = {
    "exceptions": [
        {"type": "vendor_typo", "severity": "low", "can_auto_fix": True},
        {"type": "missing_po", "severity": "medium", "can_auto_approve": True},
        {"type": "over_threshold", "severity": "high", "requires_escalation": True}
    ],
    "overall_decision_logic": {
        "step_1": "Auto-correct vendor typo (low risk)",
        "step_2": "Would approve missing PO (trusted vendor)",
        "step_3": "BUT amount over threshold → ESCALATE",
        "final": "ESCALATE with all context and auto-corrections applied"
    },
    "value_add": {
        "auto_corrected": 1,
        "would_have_approved": 1,
        "escalated_with_context": 1,
        "manager_saved_time": "15 minutes (only reviews threshold, not typo/PO)"
    }
}
```

**Demo Impact:**
- Shows RIK handles **complex scenarios**
- Demonstrates **holistic reasoning** (not isolated rule checks)
- Proves **efficiency** (fixes what it can, escalates what it must)

---

## 💰 ROI Calculator

### Input Variables

Use your company's actual numbers:

```python
# Invoice volume
invoices_per_month = 1000  # Adjust for your company

# Exception rates
exception_rate = 0.40  # 40% (industry average)

# RIK performance
rik_auto_resolution_rate = 0.80  # 80% of exceptions
traditional_rpa_auto_resolution = 0.00  # 0% of exceptions

# Costs
cost_per_manual_intervention = 20  # USD
average_processing_time_minutes = 20
```

### Calculation

```python
# Monthly calculations
total_exceptions = invoices_per_month * exception_rate

# Traditional RPA
traditional_manual = total_exceptions
traditional_cost = traditional_manual * cost_per_manual_intervention

# RIK
rik_auto_resolved = total_exceptions * rik_auto_resolution_rate
rik_manual = total_exceptions - rik_auto_resolved
rik_cost = rik_manual * cost_per_manual_intervention

# Savings
monthly_savings = traditional_cost - rik_cost
annual_savings = monthly_savings * 12

# Time savings
minutes_saved_per_month = rik_auto_resolved * average_processing_time_minutes
hours_saved_per_month = minutes_saved_per_month / 60
```

### Example Results (1,000 invoices/month)

| Metric | Traditional RPA | RIK | Improvement |
|--------|----------------|-----|-------------|
| **Automation Rate** | 60% | 92% | +32% |
| **Manual Interventions/Month** | 400 | 80 | -320 |
| **Monthly Cost** | $8,000 | $1,600 | **-$6,400** |
| **Annual Cost** | $96,000 | $19,200 | **-$76,800** |
| **Hours Saved/Month** | 0 | 106.7 | +106.7 |

### Scaled Results (10,000 invoices/month)

| Metric | Traditional RPA | RIK | Improvement |
|--------|----------------|-----|-------------|
| **Automation Rate** | 60% | 92% | +32% |
| **Manual Interventions/Month** | 4,000 | 800 | -3,200 |
| **Monthly Cost** | $80,000 | $16,000 | **-$64,000** |
| **Annual Cost** | $960,000 | $192,000 | **-$768,000** |
| **Hours Saved/Month** | 0 | 1,067 | +1,067 |

### ROI Presentation Slide

**For 10,000 invoices per month:**

```
┌─────────────────────────────────────────────────────────┐
│  🎯 RIK ROI: Invoice Exception Handling                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Annual Savings: $768,000                               │
│  Implementation Cost: ~$50,000                          │
│  Payback Period: 23 days                                │
│  3-Year ROI: 4,500%                                     │
│                                                          │
│  Plus Intangible Benefits:                              │
│  • Faster invoice processing (3s vs 20min)              │
│  • Improved vendor relationships (auto-pay)             │
│  • Reduced employee frustration (no ticket backlog)     │
│  • Scalable automation (no developer for each change)   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Issue 1: RIK API Not Responding

**Symptom:** n8n workflow fails with "Connection refused"

**Fix:**
```bash
# Check if API is running
curl http://localhost:8000/health

# If not running, start it
python3 rik_api.py

# Verify port 8000 is available
lsof -i :8000
```

### Issue 2: Google Sheets Not Logging

**Symptom:** Workflow completes but no data in sheet

**Fix:**
1. Check Google Sheets credentials in n8n
2. Verify Sheet ID is correct
3. Ensure service account has edit permission
4. Check column names match exactly (case-sensitive)

### Issue 3: Invoices Not Being Read

**Symptom:** Workflow runs but no invoices processed

**Fix:**
```bash
# Check sample_invoices folder exists
ls -la sample_invoices/

# Verify files are readable
cat sample_invoices/1_standard_invoice.json

# Check n8n folder path matches
# Update "Read Invoice Files" node path
```

### Issue 4: All Invoices Escalated

**Symptom:** RIK is too conservative, escalating everything

**Fix:**
Adjust business rules in `invoice_processor.py`:
```python
BUSINESS_RULES = {
    "auto_approve_threshold": 10000.00,  # Increase from $5K to $10K
    "require_po_over": 20000.00,  # Increase PO requirement
    "vendor_similarity_threshold": 0.80,  # Lower from 0.85 to 0.80
}
```

### Issue 5: Memory Not Learning

**Symptom:** Same invoices processed identically each time

**Fix:**
```bash
# Check database exists and is writable
ls -la data/memory.db

# Verify episodes are being saved
sqlite3 data/memory.db "SELECT COUNT(*) FROM episodes;"

# Check recent episodes
curl http://localhost:8000/memory
```

---

## ❓ FAQ

### Q1: Can RIK process real PDFs?

**A:** Yes! This demo uses JSON for simplicity, but RIK can integrate with PDF extraction libraries (PyPDF2, pdfplumber, Tesseract OCR). The reasoning engine works the same regardless of input format.

To add PDF support:
```bash
pip install pypdf2 pdfplumber
# Update extract_text_from_pdf() in invoice_processor.py
```

### Q2: How does RIK compare to AI/ML invoice processing tools?

**A:**
- **Traditional AI tools:** Extract data, but don't reason about exceptions
- **RPA tools:** Follow rules, but break on variations
- **RIK:** Combines extraction + reasoning + learning

RIK's advantage: **Contextual decision-making** using episodic memory

### Q3: What if RIK makes a wrong decision?

**A:** RIK includes confidence scores and full reasoning audit trails. Low-confidence decisions can be:
1. Escalated automatically (confidence < 0.7)
2. Reviewed by humans
3. Corrected → RIK learns from the correction

### Q4: Can RIK handle our specific business rules?

**A:** Yes! Business rules are configurable in `invoice_processor.py`. You can customize:
- Approval thresholds
- Vendor trust lists
- Exception severity levels
- Escalation criteria

### Q5: How long does implementation take?

**A:**
- **Demo/POC:** 1-2 weeks
- **Production (single use case):** 4-6 weeks
- **Enterprise rollout:** 3-6 months

Faster than traditional RPA because RIK adapts to exceptions rather than requiring exhaustive rule programming.

### Q6: What's the learning curve for our team?

**A:**
- **Business users:** Zero - RIK works in background
- **RPA developers:** 1-2 days to understand reasoning API
- **DevOps:** Standard FastAPI deployment

### Q7: Does RIK require retraining?

**A:** No! Unlike ML models:
- No training data collection
- No model retraining
- No data labeling

RIK learns from actual episodes in production (episodic memory).

### Q8: Can we use RIK with our existing RPA tools (UiPath, Automation Anywhere)?

**A:** Yes! RIK exposes REST API endpoints. Your existing bots can call RIK for:
- Exception handling
- Decision support
- Context retrieval

Integration pattern:
```
UiPath Bot → Hits exception → Calls RIK API → Gets resolution → Continues
```

### Q9: What about security and compliance?

**A:**
- All data stays on-premises (if you host RIK internally)
- Full audit trail (every decision logged with reasoning)
- No external API calls (unless you want them)
- SOC2/HIPAA friendly (same as any FastAPI service)

### Q10: How do I get executive buy-in?

**A:** Three-step approach:
1. **Run this demo** (8 minutes, shows live reasoning)
2. **Show ROI calculator** ($768K/year for 10K invoices)
3. **Pilot project** (30 days, one use case, measure actual results)

Key message: "RIK turns 60% automation into 92% automation - and it learns from every exception."

---

## 📞 Next Steps

### For Your Company Demo

1. **Customize numbers** - Use your actual invoice volume and costs
2. **Practice the script** - Get timing down to 8 minutes
3. **Prepare questions** - Anticipate technical and business questions
4. **Set up backup** - Have screenshots if live demo has issues
5. **Follow-up materials** - This guide + ROI spreadsheet

### For Production Deployment

1. **Pilot use case** - Start with one invoice type (e.g., recurring vendors)
2. **Measure baseline** - Current exception rate and handling cost
3. **Deploy RIK** - 2-4 week POC
4. **Measure results** - Actual automation improvement
5. **Scale** - Roll out to more invoice types

### For Technical Deep Dive

Want to understand how RIK works internally?

- **Reasoning Engine:** `reasoning.py` - Diagnose, simulate, validate
- **Memory System:** `memory.py` - Episodic and semantic memory
- **Meta-Controller:** `meta.py` - Architecture fitness evaluation
- **API Layer:** `rik_api.py` - REST endpoints

---

## 🎉 You're Ready!

You now have everything you need to deliver a knockout demo showing RIK doing what traditional RPA cannot: **intelligent exception handling**.

**The killer pitch:**
> "RIK is a robot with a brain. When your automation hits an exception, RIK doesn't just fail - it reasons, adapts, and learns. That's the difference between 60% automation and 92% automation. That's the difference between babysitting robots and true intelligent automation."

**Go show them what RIK can do!** 🚀

---

## 📄 Appendix: Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     n8n Workflow (Orchestration)            │
│  ┌──────────┐  ┌────────┐  ┌──────┐  ┌──────────────────┐  │
│  │ Schedule │→ │ Read   │→ │ Call │→ │ Route & Log      │  │
│  │ Trigger  │  │ Files  │  │ RIK  │  │ (Google Sheets)  │  │
│  └──────────┘  └────────┘  └───┬──┘  └──────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │         RIK API (FastAPI) - Port 8000         │
         │  ┌────────────────────────────────────────┐  │
         │  │  POST /process_invoice                 │  │
         │  │  GET  /invoice_stats                   │  │
         │  │  GET  /health                          │  │
         │  └──────────────┬─────────────────────────┘  │
         └─────────────────┼────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                    │
         ▼                                    ▼
┌──────────────────┐                 ┌───────────────────┐
│ invoice_processor│                 │  Reasoning Engine │
│                  │                 │                   │
│ • Extract fields │                 │ • diagnose()      │
│ • Detect except. │◄────────────────┤ • simulate()      │
│ • Reason about   │                 │ • validate()      │
│   exceptions     │                 │                   │
└────────┬─────────┘                 └───────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Memory System (SQLite)         │
│                                  │
│  • episodes table               │
│  • episodic_memory table        │
│  • semantic search (TF-IDF)     │
│  • clustering (DBSCAN)          │
└──────────────────────────────────┘
```

---

**Document Version:** 1.0
**Last Updated:** 2024-10-31
**RIK Version:** 5.4.0
**Maintained by:** RIK Team
