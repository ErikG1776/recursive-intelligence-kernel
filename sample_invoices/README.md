# Sample Invoice Test Cases

These JSON files simulate invoice data for demonstrating RIK's exception handling capabilities.

In production, these would be extracted from PDF files. For demo purposes, we use JSON to focus on RIK's reasoning rather than PDF parsing complexity.

## Test Cases

### 1. Standard Invoice (`1_standard_invoice.json`)
- **Status**: ✅ Happy Path
- **Vendor**: Acme Corporation (trusted)
- **Amount**: $3,240
- **PO Number**: Present
- **Expected Result**: Auto-approve (no exceptions)
- **Traditional RPA**: ✅ Success

### 2. Missing PO Number (`2_invoice_no_po.json`)
- **Status**: ⚠️ Exception
- **Vendor**: Acme Corporation (trusted)
- **Amount**: $4,100
- **PO Number**: **Missing**
- **Expected Result**: Auto-approve (trusted vendor, under $5K threshold)
- **Traditional RPA**: ❌ Fail → Manual intervention
- **RIK Reasoning**: "Vendor is trusted, amount under threshold, similar past cases approved"

### 3. Vendor Name Typo (`3_invoice_vendor_typo.json`)
- **Status**: ⚠️ Exception
- **Vendor**: "Microsft Corporation" (should be "Microsoft Corporation")
- **Amount**: $8,500
- **PO Number**: Present
- **Expected Result**: Auto-correct vendor name to "Microsoft Corporation"
- **Traditional RPA**: ❌ Fail → Vendor not found
- **RIK Reasoning**: "92% string similarity, same address/email, likely typo"

### 4. New Template Format (`4_invoice_new_template.json`)
- **Status**: ⚠️ Exception
- **Vendor**: Google LLC
- **Amount**: $4,850
- **PO Number**: Present
- **Expected Result**: Extract successfully despite new format, learn template
- **Traditional RPA**: ❌ Fail → Template not recognized
- **RIK Reasoning**: "New field names detected (qty vs quantity), adapt extraction logic"

### 5. High Amount (`5_invoice_high_amount.json`)
- **Status**: ⚠️ Exception
- **Vendor**: Amazon Web Services (trusted)
- **Amount**: **$12,500** (exceeds $5K threshold)
- **PO Number**: Present
- **Expected Result**: Escalate to manager for approval
- **Traditional RPA**: ❌ Fail → Over threshold
- **RIK Reasoning**: "Amount exceeds auto-approve limit, requires manager approval"

### 6. Multiple Exceptions (`6_invoice_multiple_exceptions.json`)
- **Status**: 🔥 Multiple Exceptions
- **Vendor**: "Salesforc Inc" (typo)
- **Amount**: $6,200 (over threshold)
- **PO Number**: **Missing**
- **Expected Result**: Escalate (multiple high-severity exceptions)
- **Traditional RPA**: ❌ Fail → Multiple errors
- **RIK Reasoning**: "Vendor typo detected (94% match), but missing PO + over threshold = escalate"

## Success Metrics

**Traditional RPA:**
- 1/6 invoices fully automated (16.7%)
- 5/6 require manual intervention (83.3%)

**RIK-Enhanced:**
- 4/6 fully automated (66.7%)
- 2/6 require escalation (33.3%)

**Improvement: 50% reduction in manual interventions**

## Usage

```bash
# Test a single invoice
curl -X POST http://localhost:8000/process_invoice \
  -H "Content-Type: application/json" \
  -d @sample_invoices/2_invoice_no_po.json

# Or use in n8n workflow to process all invoices
```

## Live Demo Script

1. **Show Traditional RPA Limitation** (2 min)
   - Upload `2_invoice_no_po.json`
   - Traditional RPA fails: "No PO number found"

2. **Show RIK Reasoning** (3 min)
   - Same invoice through RIK API
   - Watch reasoning: "Trusted vendor, amount under threshold"
   - Result: Auto-approved ✅

3. **Show Learning** (2 min)
   - Upload `6_invoice_multiple_exceptions.json`
   - RIK references past episodes
   - Shows contextual decision-making

4. **Show ROI** (2 min)
   - Call `/invoice_stats` endpoint
   - Display: 32% automation improvement
   - Calculate: $76,800/year savings for 1,000 invoices/month

Total demo time: ~10 minutes
