# 🤖 RIK Demo Guide

**Recursive Intelligence Kernel - Interactive Demo Application**

This guide will help you set up and run the RIK demo to showcase intelligent RPA capabilities to your team.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the RIK directory**
```bash
cd recursive-intelligence-kernel
```

2. **Install demo dependencies**
```bash
pip install -r requirements-demo.txt
```

3. **Initialize the memory database**
```bash
python3 -c "import memory; memory.init_memory_db()"
```

4. **Run the demo**
```bash
streamlit run demo_app.py
```

5. **Open your browser**
The demo will automatically open at `http://localhost:8501`

---

## 📊 Demo Pages Overview

### 1. 🏠 Overview
- **Purpose**: Introduction to RIK and value proposition
- **Use For**: Executive presentations, initial pitches
- **Key Points**:
  - Problem with traditional RPA
  - RIK's solution approach
  - ROI calculator showing $168K/year savings potential

### 2. 🤖 Live Bot Demo
- **Purpose**: Interactive simulation of RPA bot failures and auto-recovery
- **Use For**: Technical demos, customer proof-of-concepts
- **Features**:
  - 5 realistic RPA failure scenarios
  - Side-by-side comparison (with/without RIK)
  - Real-time strategy generation and execution
  - Visual feedback on recovery success

**Demo Flow:**
1. Select a failure scenario (e.g., "Invoice Processing - UI Element Not Found")
2. Enable "Simulate Failure" and "Enable RIK Recovery"
3. Click "Run Bot Simulation"
4. Watch RIK diagnose, strategize, and recover in real-time
5. Show the 60-80% success rate over multiple runs

### 3. 📊 Analytics Dashboard
- **Purpose**: Show measurable impact and ROI
- **Use For**: Business stakeholder meetings, ROI discussions
- **Metrics Shown**:
  - Total failures vs. auto-recoveries
  - Recovery success rate (pie chart)
  - Cost savings comparison
  - Execution timeline
  - Customizable ROI calculator

### 4. 🧠 Memory & Learning
- **Purpose**: Demonstrate how RIK learns and adapts
- **Use For**: Technical deep-dives, AI capability discussions
- **Features**:
  - Episodic memory browser
  - Semantic search (TF-IDF similarity)
  - DBSCAN clustering demonstration
  - Learning insights and trends

### 5. ⚙️ System Architecture
- **Purpose**: Technical overview for engineering teams
- **Use For**: Architecture reviews, technical evaluations
- **Content**:
  - System flowchart (Mermaid diagram)
  - Core module descriptions
  - Database schema
  - API endpoints
  - Fitness evaluation

---

## 🎯 Demo Scenarios for Different Audiences

### For Executives (15 minutes)
1. **Overview page** - Show the problem/solution (3 min)
2. **Live Bot Demo** - Run 2-3 failure scenarios (5 min)
3. **Analytics Dashboard** - Show ROI calculator with real numbers (5 min)
4. **Close** - Discuss next steps (2 min)

**Key Message**: "RIK saves $168K/year by auto-recovering from 70% of bot failures"

### For Technical Teams (30 minutes)
1. **Overview** - Quick intro (2 min)
2. **System Architecture** - Deep dive on technical design (8 min)
3. **Live Bot Demo** - Multiple scenarios with "Show Technical Details" enabled (10 min)
4. **Memory & Learning** - Demonstrate semantic search and clustering (5 min)
5. **Q&A** - Technical discussion (5 min)

**Key Message**: "RIK is a production-ready, auditable framework that integrates with your existing RPA platform"

### For Customers (20 minutes)
1. **Overview** - Focus on their pain points (3 min)
2. **Live Bot Demo** - Use scenarios relevant to their industry (10 min)
3. **Analytics Dashboard** - Customize ROI calculator with their numbers (5 min)
4. **Close** - Pilot proposal (2 min)

**Key Message**: "Your bots will break 60-80% less, saving your team hundreds of hours per month"

---

## 💡 Tips for Effective Demos

### Before the Demo
- [ ] Run through all pages yourself first
- [ ] Prepare your talking points for each section
- [ ] Have customer-specific numbers ready for ROI calculator
- [ ] Test on the presentation computer/screen
- [ ] Close unnecessary browser tabs and apps

### During the Demo
- ✅ **DO**: Let them interact with the UI
- ✅ **DO**: Run multiple bot simulations to show consistency
- ✅ **DO**: Use the ROI calculator with their real numbers
- ✅ **DO**: Show both success and failure scenarios
- ❌ **DON'T**: Rush through the analytics
- ❌ **DON'T**: Get too technical unless they ask
- ❌ **DON'T**: Spend too much time on one page

### After the Demo
- [ ] Share access to the demo environment
- [ ] Send ROI calculation summary
- [ ] Provide technical documentation if requested
- [ ] Propose pilot project with specific use case

---

## 🔧 Customization Options

### Modify Failure Scenarios
Edit `demo_app.py` around line 250 to add your company-specific scenarios:

```python
scenario = st.selectbox(
    "Choose a failure scenario:",
    [
        "Your Custom Scenario Here",
        "Another Industry-Specific Case",
        # ... existing scenarios
    ]
)
```

### Adjust ROI Calculator Defaults
Edit lines 560-570 to match your typical customer profile:

```python
num_bots = st.number_input("Number of bots deployed", value=50)  # Change default
failures_per_bot = st.number_input("Avg failures/bot/month", value=10)  # Change default
support_hourly = st.number_input("Support hourly rate ($)", value=60)  # Change default
```

### Brand Customization
Edit the CSS in lines 20-50 to match your company colors:

```python
.metric-card {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
    # ...
}
```

---

## 📈 Tracking Demo Effectiveness

After each demo, note:
- Which pages resonated most?
- Which metrics caught their attention?
- What questions did they ask?
- What objections came up?

Use this to refine your demo flow over time.

---

## 🐛 Troubleshooting

### Demo won't start
```bash
# Check if Streamlit is installed
pip show streamlit

# Reinstall if needed
pip install streamlit --upgrade
```

### Import errors
```bash
# Make sure you're in the RIK directory
cd recursive-intelligence-kernel

# Reinstall all dependencies
pip install -r requirements-demo.txt
```

### Database errors
```bash
# Reinitialize the database
python3 -c "import memory; memory.init_memory_db()"
```

### Port already in use
```bash
# Run on a different port
streamlit run demo_app.py --server.port 8502
```

---

## 🎬 Recording Demos

To create a demo video for async sharing:

1. **Mac**: Use QuickTime Player (File → New Screen Recording)
2. **Windows**: Use Xbox Game Bar (Win + G)
3. **Cross-platform**: Use OBS Studio (free)

**Recording Tips**:
- Record in 1080p or higher
- Keep videos under 10 minutes
- Add voiceover explaining each feature
- Edit out any mistakes or long pauses

---

## 📞 Support

If you encounter issues or need customization help:
1. Check the main README.md for RIK documentation
2. Review the code comments in demo_app.py
3. Test individual components using integration_test.py

---

## 🚀 Next Steps After a Successful Demo

1. **Immediate Follow-up** (within 24 hours)
   - Send demo recording or access link
   - Provide ROI summary with their numbers
   - Propose specific next steps

2. **Pilot Proposal** (within 1 week)
   - Identify 1-2 problematic bots to target
   - Define success metrics
   - Set 2-4 week timeline
   - Propose pricing/terms

3. **Pilot Execution** (weeks 2-6)
   - Deploy RIK with selected bots
   - Collect metrics daily
   - Weekly check-ins
   - Document wins and learnings

4. **Scale** (month 2+)
   - Expand to more bots
   - Full production deployment
   - Customer success case study

---

**Good luck with your demo! 🎯**

Remember: The goal isn't to show every feature—it's to prove RIK solves their specific pain point and delivers measurable ROI.
