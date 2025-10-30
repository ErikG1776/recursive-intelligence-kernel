# 🤖 RIK Self-Healing Web Scraper Demo

**Complete guide for building and demonstrating a real self-healing web scraper using RIK + n8n**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [What You'll Build](#what-youll-build)
3. [Prerequisites](#prerequisites)
4. [Setup Instructions](#setup-instructions)
5. [Live Demo Script](#live-demo-script)
6. [Breaking & Fixing Live](#breaking--fixing-live)
7. [Measuring ROI](#measuring-roi)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This demo showcases **real, non-simulated** self-healing automation:

- ✅ **Real web scraping** (Hacker News)
- ✅ **Real failures** (you control when/how it breaks)
- ✅ **Real recovery** (RIK finds working selectors in seconds)
- ✅ **Real metrics** (logs every recovery with timestamps)

**Value Proposition:**
> "Traditional RPA: Scraper breaks when website updates CSS. Engineer spends 20 minutes fixing. **With RIK:** Auto-recovers in 5 seconds. Across 100 bots, saves $14K/month."

---

## 🏗️ What You'll Build

### Architecture
```
n8n Workflow
    ↓
[Schedule: Every 5 min]
    ↓
[HTTP: Scrape Hacker News]
    ↓
[Code: Extract with CSS selector]
    ↓
[IF: Success?]
    ├─ YES → Log to Google Sheets
    └─ NO  → Call RIK API
              ↓
         [RIK analyzes HTML]
              ↓
         [Returns 5 alternatives]
              ↓
         [Retry with best selector]
              ↓
         [Log recovery metrics]
```

### What Gets Demonstrated
1. **Normal Operation**: Scraper works, data flows to Google Sheets
2. **Failure**: You break the selector during demo
3. **Auto-Recovery**: RIK finds alternative in 3-5 seconds
4. **Learning**: RIK logs strategy for future use
5. **Metrics**: Dashboard shows recovery rate, time saved

---

## ✅ Prerequisites

### Required
- [x] Python 3.8+ installed
- [x] n8n installed (via npm or Docker)
- [x] Google account (for Sheets logging)
- [x] Basic understanding of CSS selectors

### Optional but Recommended
- [ ] Postman (for testing API directly)
- [ ] ngrok (if n8n is remote)

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies (5 min)

```bash
cd recursive-intelligence-kernel

# Install beautifulsoup4 for HTML parsing
pip install beautifulsoup4 lxml

# Verify installation
python3 -c "from bs4 import BeautifulSoup; print('✅ BeautifulSoup installed')"
```

### Step 2: Start RIK API (2 min)

```bash
# Terminal 1: Start RIK API
python3 rik_api.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test the API:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "5.3.0",
  "features": ["selector_recovery", "memory", "metrics", "reasoning"]
}
```

### Step 3: Set Up Google Sheets (5 min)

1. **Create a new Google Sheet**
   - Go to https://sheets.google.com
   - Create new spreadsheet named "RIK Web Scraper Demo"
   - Add headers in row 1:
     ```
     Timestamp | Selector | Status | Details | Confidence
     ```

2. **Get Sheet ID**
   - Copy the ID from URL:
     ```
     https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
     ```

3. **Set up n8n Google Sheets credentials**
   - In n8n: Settings → Credentials → Add New
   - Select "Google Sheets API"
   - Follow OAuth flow to authorize

### Step 4: Import n8n Workflow (5 min)

1. **Start n8n**
   ```bash
   # Terminal 2: Start n8n
   npx n8n

   # Or if using Docker:
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     n8nio/n8n
   ```

2. **Access n8n**
   - Open http://localhost:5678
   - Login/create account (local only)

3. **Import workflow**
   - Click "Workflows" → "Import from File"
   - Select `n8n_workflows/rik_self_healing_scraper.json`
   - Click "Import"

4. **Configure workflow**
   - Open the workflow
   - Click "Log Success to Google Sheets" node
   - Update `documentId` with your Sheet ID
   - Click "Log Recovery to Google Sheets" node
   - Update `documentId` with your Sheet ID
   - Click "Save"

### Step 5: Test End-to-End (5 min)

1. **Manual test run**
   - In n8n workflow, click "Execute Workflow"
   - Wait 10-15 seconds
   - Check execution log

**Expected result:**
```
✅ Scraped 30 titles successfully
```

2. **Verify Google Sheets**
   - Open your Google Sheet
   - Should see new row with:
     - Current timestamp
     - Selector: `.titleline > a`
     - Status: Success
     - ~30 titles found

3. **Test RIK API directly** (optional)
   ```bash
   curl -X POST http://localhost:8000/recover_selector \
     -H "Content-Type: application/json" \
     -d '{
       "failed_selector": ".old-selector",
       "html": "<html><h1 class=\"titleline\">Test</h1></html>",
       "url": "https://example.com"
     }'
   ```

---

## 🎬 Live Demo Script

### Pre-Demo Checklist (Do this before audience arrives)
- [ ] RIK API running (Terminal 1)
- [ ] n8n running (Terminal 2)
- [ ] Google Sheet open in browser tab
- [ ] n8n workflow open in another tab
- [ ] Demo dashboard open (Streamlit app)
- [ ] All services tested and working

### Demo Timeline (10 minutes total)

#### **00:00-02:00 - Show Normal Operation**

**Script:**
> "This is a typical RPA bot that scrapes Hacker News every 5 minutes for the top stories. Let me show you it working normally."

**Actions:**
1. Open Google Sheet (empty or with 1-2 rows)
2. In n8n, click "Execute Workflow"
3. Wait for completion (15 sec)
4. Refresh Google Sheet - show new row with data
5. Point out: "30 titles extracted successfully using this CSS selector"

**Key Point:** "This works great... until the website changes their HTML."

---

#### **02:00-03:00 - Break It (Simulate Real-World Failure)**

**Script:**
> "Websites update their HTML all the time. Let me simulate what happens when Hacker News changes their CSS classes - this is the #1 reason RPA bots fail in production."

**Actions:**
1. In n8n, open "Extract Titles" code node
2. Change selector from `.titleline > a` to `.old-titleline > a`
3. Click "Save"
4. Execute workflow again
5. **Point to terminal** - Show it hit the "false" branch

**Key Point:** "The bot just failed. In traditional RPA, this creates a support ticket, engineer investigates for 20 minutes, fixes it manually. Let's see RIK handle this."

---

#### **03:00-06:00 - Watch RIK Auto-Recover**

**Script:**
> "The workflow detected the failure and automatically called RIK's selector recovery API. Watch what happens..."

**Actions:**
1. Execute workflow (with broken selector)
2. **Show RIK API terminal** - Real-time logs:
   ```
   [INFO] Selector recovery requested for: .old-titleline > a
   [INFO] Analyzing HTML structure...
   [SUCCESS] Generated 5 alternatives
   [INFO] Recommended: .titleline > a (confidence: 0.90)
   ```
3. Wait 3-5 seconds
4. **Show Google Sheet** - New row shows:
   - Status: "Auto-Recovered by RIK"
   - New Selector: `.titleline > a`
   - Confidence: 90%
   - Strategy: "Detected class in HTML"

**Key Point:** "RIK just analyzed the HTML, tried 5 different selector strategies, found one that works, and logged it to memory. Total time: 5 seconds instead of 20 minutes."

---

#### **06:00-08:00 - Show the Value**

**Script:**
> "Let me show you what this means in real business terms."

**Actions:**
1. Open RIK Streamlit demo (http://localhost:8501)
2. Navigate to "📊 Analytics Dashboard"
3. Show metrics:
   - Total failures: 1
   - Auto-recoveries: 1
   - Recovery rate: 100%
   - Time saved: 20 minutes = $20

4. **Open ROI calculator**
5. Input company's real numbers:
   - Number of bots: 100
   - Failures per bot/month: 10
   - Support hourly rate: $60

6. **Show result:**
   ```
   Monthly failures: 1,000
   Traditional cost: $20,000/month
   With RIK: $6,000/month
   SAVINGS: $14,000/month = $168,000/year
   ```

**Key Point:** "For your company with 100 bots, this is $168K in annual savings. And your customers experience zero downtime."

---

#### **08:00-10:00 - Show Learning & Memory**

**Script:**
> "RIK doesn't just recover - it learns. Let me show you the memory system."

**Actions:**
1. In Streamlit demo, go to "🧠 Memory & Learning"
2. Show recent episodes list
3. Point to the recovery episode:
   ```
   Task: Selector recovery: .old-titleline > a on https://news.ycombinator.com
   Result: alternatives_generated
   Reflection: Generated 5 alternative selectors. Top strategy: Detected class in HTML
   ```
4. Type in semantic search: "titleline selector"
5. Show it retrieves the recovery episode

**Key Point:** "The next time a similar failure happens - maybe on a different website with similar structure - RIK already knows which strategies work best. It gets smarter over time."

---

## 🔨 Breaking & Fixing Live

### Ways to Break It During Demo

#### **Option 1: Change Selector** (Easiest)
In n8n "Extract Titles" node, change:
```javascript
const cssSelector = '.titleline > a';  // Working
```
To:
```javascript
const cssSelector = '.old-title';  // Broken
```

#### **Option 2: Change Regex Pattern**
```javascript
const regex = /<a[^>]+class=\"[^\"]*titleline[^\"]*\"[^>]*>([^<]+)</gi;  // Working
```
To:
```javascript
const regex = /<a[^>]+class=\"[^\"]*old-class[^\"]*\"[^>]*>([^<]+)</gi;  // Broken
```

#### **Option 3: Simulate Network Issue**
In "Fetch Hacker News" node, change URL to:
```
https://news.ycombinator.com/nonexistent-page
```

### How RIK Fixes Each

| Break Type | RIK Strategy | Time to Recover |
|------------|--------------|-----------------|
| Wrong class selector | Analyzes HTML, finds actual classes | 3-5 seconds |
| Wrong regex | Generates alternative patterns | 4-6 seconds |
| Wrong URL | Suggests URL corrections, retries | 5-8 seconds |

---

## 📊 Measuring ROI

### Metrics to Track

**Before RIK (Traditional RPA):**
- Average fix time: 20 minutes per failure
- Failures per bot per month: 10
- Support engineer hourly rate: $60
- **Cost per bot per month:** 10 × (20/60) × $60 = $200

**With RIK:**
- Average recovery time: 5 seconds
- Auto-recovery rate: 70-80%
- Manual fixes needed: 2-3 per month
- **Cost per bot per month:** 3 × (20/60) × $60 = $60

**Savings per bot:** $140/month

**Company with 100 bots:**
- Monthly savings: $14,000
- Annual savings: $168,000
- ROI: 840% (if RIK costs $20K/year)

### Real-World Impact

**Customer Satisfaction:**
- Traditional: 20 min downtime per failure = angry customers
- With RIK: 5 sec recovery = customers don't even notice

**Team Efficiency:**
- Traditional: Support team spends 333 hours/month fixing bots
- With RIK: Support team spends 100 hours/month = 233 hours freed up

---

## 🐛 Troubleshooting

### RIK API won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Try different port
uvicorn rik_api:app --host 0.0.0.0 --port 8001
```

### n8n can't reach RIK API
```bash
# If RIK API is on different machine, use ngrok
ngrok http 8000

# Update n8n workflow to use ngrok URL
https://your-ngrok-url.ngrok.io/recover_selector
```

### Google Sheets not logging
- Verify credentials are set up correctly
- Check Sheet ID is correct
- Ensure sheet has headers in row 1
- Check n8n has internet access

### Selector recovery returns empty alternatives
```bash
# Test the endpoint directly
curl -X POST http://localhost:8000/recover_selector \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Check RIK API logs for errors
```

### Workflow executes but no data
- Check n8n execution log for errors
- Verify Hacker News is accessible
- Try a different website (Reddit, Wikipedia)

---

## 🎓 Advanced Demos

### Demo Variation 1: Multiple Websites
- Add nodes for Reddit, Wikipedia, GitHub trending
- Show RIK handles different HTML structures
- Demonstrate learning across sites

### Demo Variation 2: A/B Testing
- Run two identical scrapers
- One with RIK, one without
- Show side-by-side failure handling

### Demo Variation 3: Historical Recovery Rate
- Populate database with past recoveries
- Show analytics dashboard with trends
- Demonstrate improvement over time

---

## 📚 Additional Resources

- **Full RIK Documentation:** See main README.md
- **API Reference:** http://localhost:8000/docs (when API is running)
- **n8n Documentation:** https://docs.n8n.io
- **Support:** Create issue on GitHub

---

## ✅ Demo Checklist

Before presenting to stakeholders:

**Technical Setup**
- [ ] RIK API starts without errors
- [ ] n8n workflow imports successfully
- [ ] Google Sheets credentials configured
- [ ] Test execution completes successfully
- [ ] Can break and recover selector live

**Presentation Prep**
- [ ] Google Sheet open in browser tab
- [ ] n8n workflow open in browser tab
- [ ] Streamlit demo dashboard open
- [ ] Terminal windows arranged for visibility
- [ ] Know how to break selector quickly
- [ ] Have company-specific ROI numbers ready

**Backup Plans**
- [ ] Screenshots of successful recovery
- [ ] Recorded video of demo (in case of technical issues)
- [ ] Test payload for direct API testing
- [ ] Alternative website if Hacker News is down

---

## 🎯 Expected Demo Outcome

After this demo, your audience should understand:

1. ✅ **The Problem:** RPA bots break constantly when websites change
2. ✅ **The Solution:** RIK auto-recovers in seconds, not minutes
3. ✅ **The Technology:** Real AI-powered fallback strategies, not simulation
4. ✅ **The ROI:** $168K/year savings for 100 bots
5. ✅ **Next Steps:** Pilot with 2-3 problematic production bots

---

**Ready to demo? Run through the checklist and you're good to go!** 🚀

For questions or issues, check the main documentation or create a GitHub issue.
