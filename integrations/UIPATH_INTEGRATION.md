# RIK + UiPath Integration Guide
## Transform Your RPA with Intelligent Exception Handling

This guide shows you exactly how to integrate RIK into your UiPath workflows to handle exceptions that would normally break traditional RPA.

---

## Why RIK + UiPath?

**Traditional RPA Problem:**
```
Invoice arrives → Missing PO number → ❌ Bot stops → ⚠️ Exception queue → 👤 Human intervention required
```

**With RIK:**
```
Invoice arrives → Missing PO number → 🧠 RIK analyzes → ✓ Auto-resolves → ✅ Process continues
```

**Result:** 92% automation rate vs 60% traditional RPA (+32% improvement)

---

## Integration Methods

### Method 1: HTTP Request Activity (No Coding Required)
✅ Easiest to set up
✅ No code required
✅ Works with any UiPath license

### Method 2: C# Client Library (Advanced)
✅ Type-safe
✅ Better error handling
✅ Reusable across workflows

---

## Method 1: HTTP Request Activity

### Step-by-Step Tutorial

#### 1. Prepare Your Workflow

Add these activities to your workflow:
1. **HTTP Request** (from UiPath.WebAPI.Activities package)
2. **Deserialize JSON** (built-in)
3. **If** (built-in)

#### 2. Configure HTTP Request Activity

**Properties:**
- **Endpoint:** `http://localhost:8000/process_invoice`
- **Method:** `POST`
- **Accept Format:** `application/json`
- **Body Format:** `application/json`

**Headers:**
```vb
New Dictionary(Of String, String) From {
    {"Content-Type", "application/json"}
}
```

**Body:**
```vb
"{" & _
"  ""pdf_content"": """ & invoiceDataJson.Replace("""", "\""") & """," & _
"  ""invoice_id"": """ & invoiceNumber & """" & _
"}"
```

**Output:**
- Variable: `httpResponse` (Type: `HttpResponseMessage`)

#### 3. Parse Response

Add **Deserialize JSON** activity:
- **JsonString:** `httpResponse.Content.ReadAsStringAsync().Result`
- **TypeArgument:** `Newtonsoft.Json.Linq.JObject`
- **Output:** `rikResponse` (Type: `JObject`)

#### 4. Extract Values

Add **Assign** activities:

```vb
' Extract final action
finalAction = rikResponse("final_action").ToString()

' Extract confidence score
confidence = CDbl(rikResponse("confidence_score").ToString())

' Extract reasoning
reasoning = rikResponse("reasoning").ToString()

' Extract exception info
exceptionsFound = CInt(rikResponse("exceptions_found").ToString())
exceptionsResolved = CInt(rikResponse("exceptions_resolved").ToString())

' Check if needs human review
needsReview = (finalAction = "escalate") OrElse (confidence < 0.7)
```

#### 5. Add Decision Logic

Add **If** activity:
- **Condition:** `needsReview = False`

**Then (Auto-process):**
```
├─ Log Message: "RIK Decision: " + finalAction + " (Confidence: " + confidence.ToString("P0") + ")"
├─ If finalAction = "approve"
│   └─ [Your approval logic - e.g., update ERP, send email]
└─ If finalAction = "reject"
    └─ [Your rejection logic - e.g., archive, notify]
```

**Else (Escalate to Human):**
```
├─ Log Message: "Escalating to human review: " + reasoning
├─ Add Queue Item (Orchestrator queue: "InvoiceReview")
│   ├─ Reference: invoiceNumber
│   └─ SpecificContent: New Dictionary From {
│       {"invoice_id", invoiceNumber},
│       {"reasoning", reasoning},
│       {"confidence", confidence}
│   }
└─ Send Email to reviewer
```

### Complete Workflow Diagram

```
┌─────────────────────────┐
│  Read Invoice Email     │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Extract PDF Attachment │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Parse Invoice Data     │
│  (OCR / Invoice Parser) │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Build JSON             │
│  (Serialize invoice to  │
│   JSON string)          │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  HTTP POST to RIK       │
│  /process_invoice       │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Deserialize Response   │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Extract: finalAction,  │
│  confidence, reasoning  │
└───────────┬─────────────┘
            │
     ┌──────▼──────┐
     │ If needs    │
     │ review?     │
     └──────┬──────┘
          ┌─┴─┐
          │   │
    No ───┤   ├─── Yes
          │   │
    ┌─────▼────────┐    ┌────▼─────────────┐
    │ Auto-Process │    │ Escalate to      │
    │              │    │ Human (Queue)    │
    │ ├─ Approve   │    │                  │
    │ └─ Reject    │    │ ├─ Add to Queue  │
    │              │    │ └─ Send Email    │
    └──────────────┘    └──────────────────┘
```

---

## Method 2: C# Client Library

### Setup

1. **Add Files to Project:**
   - Copy `integrations/csharp/RIKClient.cs` to your UiPath project folder

2. **Add NuGet Package:**
   - Open "Manage Packages"
   - Search for "Newtonsoft.Json"
   - Install version 13.0.3+

3. **Import Namespaces:**
   In Project settings → Imports:
   - `RIK`
   - `Newtonsoft.Json`
   - `System.Threading.Tasks`

### Using Invoke Code Activity

Add **Invoke Code** activity:

**Input Arguments:**
- `invoiceDataJson` (String)
- `invoiceNumber` (String)

**Output Arguments:**
- `finalAction` (String)
- `confidence` (Double)
- `reasoning` (String)
- `needsReview` (Boolean)

**Code:**
```csharp
var client = new RIKClient("http://localhost:8000");

var result = await client.ProcessInvoiceAsync(invoiceDataJson, invoiceNumber);

finalAction = result.FinalAction;
confidence = result.ConfidenceScore;
reasoning = result.Reasoning;
needsReview = result.NeedsHumanReview();

client.Dispose();
```

### Example: Complete Invoice Processing Workflow

```vb
' Variables
Dim invoiceDataJson As String
Dim invoiceNumber As String
Dim finalAction As String
Dim confidence As Double
Dim reasoning As String
Dim needsReview As Boolean

' 1. Read invoice and extract data
' ... your invoice processing logic ...

' 2. Call RIK via Invoke Code
' ... paste C# code above ...

' 3. Decision logic
If needsReview = False Then
    ' Auto-process
    If finalAction = "approve" Then
        ' Approve invoice
        Log Message "Auto-approved: " & reasoning
        ' ... create invoice in ERP ...
    ElseIf finalAction = "reject" Then
        ' Reject invoice
        Log Message "Auto-rejected: " & reasoning
        ' ... archive and notify ...
    End If
Else
    ' Escalate to human
    Log Message "Escalated to human: " & reasoning
    ' ... add to Orchestrator queue ...
End If
```

---

## Common Use Cases

### 1. Missing Purchase Order Number

**Traditional RPA:**
```
❌ Exception: PO number not found → Bot stops
```

**With RIK:**
```
✓ RIK checks: Amount < $5000 AND trusted vendor → Auto-approve with retroactive PO
```

### 2. Low OCR Confidence

**Traditional RPA:**
```
❌ OCR confidence <95% → Manual review required
```

**With RIK:**
```
✓ RIK cross-references: Vendor known, amount matches historical → Auto-approve
```

### 3. Unknown Vendor

**Traditional RPA:**
```
❌ Vendor not in master list → Exception queue
```

**With RIK:**
```
✓ RIK analyzes: Similar vendor name found, website verified → Flag for audit but process
```

### 4. Duplicate Invoice Detection

**Traditional RPA:**
```
❌ Invoice number exists → Hard stop
```

**With RIK:**
```
✓ RIK checks: Same invoice but different PO line items → Treat as separate charge
```

---

## Error Handling in UiPath

### Try-Catch Block

```vb
Try
    ' HTTP Request to RIK
    ...

Catch ex As WebException
    ' Connection error
    Log Error "Cannot connect to RIK: " & ex.Message
    ' Fallback: Add to manual review queue

Catch ex As JsonException
    ' Parse error
    Log Error "Cannot parse RIK response: " & ex.Message
    ' Fallback: Add to manual review queue

End Try
```

### Retry Logic

```vb
Dim retryCount As Integer = 0
Dim maxRetries As Integer = 3
Dim success As Boolean = False

Do While (retryCount < maxRetries) And (success = False)
    Try
        ' Call RIK
        ...
        success = True

    Catch ex As Exception
        retryCount = retryCount + 1
        If retryCount < maxRetries Then
            Log Message "RIK call failed, retrying... (" & retryCount & "/" & maxRetries & ")"
            System.Threading.Thread.Sleep(2000 * retryCount) ' Exponential backoff
        Else
            Log Error "RIK call failed after " & maxRetries & " attempts"
            ' Add to manual review queue
        End If
    End Try
Loop
```

---

## Orchestrator Integration

### Queue for Human Review

When RIK escalates (`final_action = "escalate"`), add to Orchestrator queue:

**Add Queue Item Activity:**
- **QueueName:** "InvoiceExceptionReview"
- **Reference:** Invoice number
- **Priority:** Based on amount (High if >$10K)
- **SpecificContent:**
  ```vb
  New Dictionary(Of String, Object) From {
      {"invoice_id", invoiceNumber},
      {"vendor_name", vendorName},
      {"amount", amount},
      {"rik_reasoning", reasoning},
      {"rik_confidence", confidence},
      {"exceptions_found", exceptionsFound}
  }
  ```

### Dashboard Metrics

Track RIK performance in Orchestrator:
- Total invoices processed
- Auto-approved %
- Auto-rejected %
- Escalated %
- Average confidence score
- Average processing time

---

## Performance Tips

### 1. Batch Processing

Instead of calling RIK for each invoice individually:

```vb
' Process 10 invoices concurrently
Dim tasks As New List(Of Task(Of InvoiceProcessingResult))

For Each invoice In invoiceBatch
    Dim client = New RIKClient("http://localhost:8000")
    tasks.Add(client.ProcessInvoiceAsync(invoice.JsonData, invoice.Id))
Next

Dim results = Task.WhenAll(tasks).Result

' Process results
For Each result In results
    ' ... decision logic ...
Next
```

### 2. Connection Pooling

Reuse the RIK client across multiple calls:

```vb
' Create once at workflow start
Dim rikClient As New RIKClient("http://localhost:8000")

' Use for all invoices
For Each invoice In invoices
    Dim result = rikClient.ProcessInvoiceAsync(invoice.JsonData, invoice.Id).Result
    ' ... process result ...
Next

' Dispose at workflow end
rikClient.Dispose()
```

### 3. Caching

Cache RIK responses for duplicate checks:

```vb
Dim responseCache As New Dictionary(Of String, JObject)

Dim cacheKey = invoiceNumber & "_" & amount.ToString()

If responseCache.ContainsKey(cacheKey) Then
    ' Use cached response
    rikResponse = responseCache(cacheKey)
Else
    ' Call RIK and cache
    ' ... HTTP request ...
    responseCache.Add(cacheKey, rikResponse)
End If
```

---

## Testing Your Integration

### 1. Unit Test with Sample Invoices

Test these scenarios:
- ✅ Valid invoice (should auto-approve)
- ✅ Missing PO (should auto-approve if under threshold)
- ✅ Unknown vendor (should escalate)
- ✅ Duplicate invoice (should escalate)
- ✅ High amount + exceptions (should escalate)

### 2. Check Response Times

Monitor RIK performance:
- Median: ~80-120ms
- P95: <200ms
- P99: <500ms

If slower, check:
- Network latency
- RIK server load
- Database performance

### 3. Validate Decisions

Compare RIK decisions against human decisions for first 100 invoices:
- Agreement rate should be >85%
- Escalation rate should be 10-20%
- False positives (wrong auto-approve) should be <2%

---

## Production Deployment

### Checklist

- [ ] RIK API deployed to production server
- [ ] API key authentication enabled
- [ ] HTTPS configured (for production)
- [ ] Health check monitoring set up
- [ ] Orchestrator queues created
- [ ] Email notifications configured
- [ ] Dashboard / metrics tracking enabled
- [ ] Backup/fallback logic tested
- [ ] Error handling and retries implemented
- [ ] Logging configured
- [ ] Team trained on escalation queue

### Monitoring

Set up alerts for:
- RIK API downtime (>1 min)
- High escalation rate (>30%)
- Low confidence average (<0.7)
- Slow response times (>500ms p95)

---

## ROI Calculator

**Before RIK:**
- 1,000 invoices/month
- 40% have exceptions
- 60% automation rate → 400 invoices need manual review
- 10 min per manual review → 4,000 min (67 hours)
- $30/hour → $2,000/month

**After RIK:**
- 1,000 invoices/month
- 40% have exceptions
- 92% automation rate → 80 invoices need manual review
- 10 min per review → 800 min (13 hours)
- $30/hour → $400/month

**Monthly Savings:** $1,600
**Annual Savings:** $19,200
**5-Year Savings:** $96,000

Plus:
- Faster processing (80ms vs hours)
- Reduced error rate
- Better audit trail
- Scalable to higher volumes

---

## Support

- **RIK API Docs:** http://localhost:8000/docs
- **Python SDK:** See `rik_sdk/` directory
- **C# Client:** See `integrations/csharp/`
- **Integration Guide:** See `integrations/INTEGRATION_GUIDE.md`

---

## License

MIT
