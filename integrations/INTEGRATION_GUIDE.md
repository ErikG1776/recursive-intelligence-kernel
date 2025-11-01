# RIK Integration Guide
## How to Integrate RIK with Popular Automation Platforms

This guide shows you how to integrate RIK (Recursive Intelligence Kernel) with popular automation and integration platforms.

---

## Table of Contents

1. [UiPath Integration](#uipath-integration)
2. [Zapier Integration](#zapier-integration)
3. [Microsoft Power Automate](#microsoft-power-automate)
4. [Make.com (Integromat)](#makecom-integromat)
5. [n8n Integration](#n8n-integration)
6. [Generic Webhook/HTTP Integration](#generic-webhookhttp-integration)

---

## UiPath Integration

### Method 1: HTTP Request Activity (Recommended for Beginners)

**Step 1: Add HTTP Request Activity**
1. Drag "HTTP Request" activity into your workflow
2. Configure the activity:

**Configuration:**
- **Endpoint:** `http://localhost:8000/process_invoice`
- **Method:** `POST`
- **Headers:**
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **Body:**
  ```json
  {
    "pdf_content": "{\"invoice_number\":\"INV-001\",\"vendor_name\":\"Acme Corp\",\"amount\":5000,\"po_number\":\"\"}",
    "invoice_id": "INV-001"
  }
  ```

**Step 2: Parse Response**
1. Add "Deserialize JSON" activity
2. Input: HTTP Request response
3. TypeArgument: `Newtonsoft.Json.Linq.JObject`

**Step 3: Extract Values**
```vb
' Extract final action
finalAction = response("final_action").ToString()

' Extract confidence
confidence = CDbl(response("confidence_score").ToString())

' Extract reasoning
reasoning = response("reasoning").ToString()

' Check if needs review
needsReview = (finalAction = "escalate") OrElse (confidence < 0.7)
```

**Step 4: Decision Logic**
```
If needsReview = True Then
    ' Send to human review queue
    ' Log escalation
Else
    ' Auto-approve or auto-reject
    Log Message: "Automated decision: " + finalAction
End If
```

### Method 2: C# Client Library (Advanced)

1. **Add RIKClient.cs** to your project
2. **Add NuGet Package:** Newtonsoft.Json
3. **Use Invoke Code Activity:**

```csharp
// Input arguments: invoiceData (String)
// Output arguments: finalAction (String), reasoning (String), confidence (Double)

var client = new RIKClient("http://localhost:8000");
var result = await client.ProcessInvoiceAsync(invoiceData, "INV-001");

finalAction = result.FinalAction;
reasoning = result.Reasoning;
confidence = result.ConfidenceScore;
```

### Complete UiPath Workflow Example

```
[Read PDF] → [Extract Invoice Data] → [HTTP Request to RIK]
                                              ↓
                                      [Deserialize JSON]
                                              ↓
                                         [Decision]
                                        ↙         ↘
                              [Approve/Reject]  [Escalate to Human]
                                    ↓                  ↓
                              [Update ERP]      [Add to Review Queue]
```

---

## Zapier Integration

### Create a Zap with RIK

**Trigger:** When invoice received (Gmail, Dropbox, etc.)

**Action: Webhooks by Zapier - POST Request**

1. **URL:** `http://your-rik-server.com:8000/process_invoice`
2. **Method:** POST
3. **Data:**
   ```json
   {
     "pdf_content": "{{invoice_data}}",
     "invoice_id": "{{invoice_number}}"
   }
   ```
4. **Headers:**
   - `Content-Type`: `application/json`
   - `X-API-Key`: `your-api-key` (if authentication enabled)

**Action: Filter by Zapier**

- Continue only if: `final_action` equals `approve`

**Action: Create Invoice in QuickBooks/Xero/ERP**

- Map fields from RIK response

### Example Zap Flow

```
Gmail (New Email) → Extract Attachment → POST to RIK → Filter (if approved) → Create in QuickBooks
```

### Advanced: Handle Escalations

```
POST to RIK → Paths:
  ├─ Path A (approved): Create in ERP
  ├─ Path B (rejected): Archive and notify
  └─ Path C (escalate): Send Slack notification to finance team
```

---

## Microsoft Power Automate

### Create a Flow with RIK

**Trigger:** When a file is created (SharePoint, OneDrive, etc.)

**Action: HTTP - Send an HTTP request**

1. **URI:** `http://your-rik-server.com:8000/process_invoice`
2. **Method:** POST
3. **Headers:**
   ```json
   {
     "Content-Type": "application/json"
   }
   ```
4. **Body:**
   ```json
   {
     "pdf_content": "@{body('Get_file_content')}",
     "invoice_id": "@{triggerOutputs()?['body/Name']}"
   }
   ```

**Action: Parse JSON**

- Content: `@body('HTTP')`
- Schema:
  ```json
  {
    "type": "object",
    "properties": {
      "final_action": {"type": "string"},
      "confidence_score": {"type": "number"},
      "reasoning": {"type": "string"},
      "exceptions_found": {"type": "integer"}
    }
  }
  ```

**Action: Condition**

- If `final_action` equals `approve`
  - Yes: Create item in Dynamics 365 / Dataverse
  - No: Send email to approver

### Example Flow

```
OneDrive (New Invoice) → HTTP POST to RIK → Parse JSON → Condition
                                                          ↙      ↘
                                                  [Auto-Process]  [Request Approval]
```

---

## Make.com (Integromat)

### Create a Scenario with RIK

**Module 1: Trigger (e.g., Google Drive - Watch Files)**

**Module 2: HTTP - Make a Request**

- **URL:** `http://your-rik-server.com:8000/process_invoice`
- **Method:** POST
- **Headers:**
  - Name: `Content-Type`, Value: `application/json`
- **Body (JSON):**
  ```json
  {
    "pdf_content": "{{1.data}}",
    "invoice_id": "{{1.name}}"
  }
  ```

**Module 3: Router**

- **Route 1:** Filter: `final_action` = `approve`
  - Action: Create record in Airtable/Monday.com

- **Route 2:** Filter: `final_action` = `escalate`
  - Action: Send Slack message to #finance-review

- **Route 3:** Filter: `final_action` = `reject`
  - Action: Move file to "Rejected" folder

### Example Scenario

```
Google Drive → RIK HTTP POST → Router
                                ├─ Approved → Create in Airtable
                                ├─ Escalate → Slack Notification
                                └─ Reject → Move to Folder
```

---

## n8n Integration

RIK already has n8n integration examples! See: `demos/web_scraper_self_healing/n8n_workflow.json`

### Quick Setup

1. **Import Workflow:** Import the JSON file into n8n
2. **Configure HTTP Request Node:**
   - URL: `http://localhost:8000/process_invoice`
   - Method: POST
   - Authentication: None (or API Key if enabled)
   - Body: JSON with invoice data

3. **Add Logic:**
   ```
   Trigger → RIK API Call → Switch Node
                             ├─ approved → Webhook/Database
                             ├─ rejected → Archive
                             └─ escalate → Email Notification
   ```

---

## Generic Webhook/HTTP Integration

For any platform that supports HTTP/Webhook, use this generic approach:

### Endpoint

```
POST http://your-rik-server:8000/process_invoice
Content-Type: application/json
```

### Request Body

```json
{
  "pdf_content": "{\"invoice_number\":\"INV-001\",\"vendor_name\":\"Acme\",\"amount\":5000,\"po_number\":\"\"}",
  "invoice_id": "INV-001",
  "context": {
    "source": "email_attachment",
    "received_date": "2024-11-01"
  }
}
```

### Response (Success - 200 OK)

```json
{
  "invoice_id": "INV-001",
  "final_action": "approve",
  "confidence_score": 0.92,
  "reasoning": "Auto-approve: Amount under $5000, trusted vendor",
  "exceptions_found": 1,
  "exceptions_resolved": 1,
  "processing_time_seconds": 0.084,
  "traditional_rpa_would_fail": true
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `final_action` | string | `"approve"`, `"reject"`, or `"escalate"` |
| `confidence_score` | float | 0.0 to 1.0 (confidence in decision) |
| `reasoning` | string | Explanation of the decision |
| `exceptions_found` | int | Number of exceptions detected |
| `exceptions_resolved` | int | Number auto-resolved by RIK |
| `traditional_rpa_would_fail` | bool | Would traditional RPA have failed? |

### Error Responses

**401 Unauthorized** (if API key required):
```json
{
  "detail": "Invalid API key"
}
```

**422 Validation Error**:
```json
{
  "detail": "Validation error: pdf_content cannot be empty"
}
```

**429 Rate Limited**:
```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Authentication

If you've enabled API key authentication in RIK (via `RIK_API_KEY_ENABLED=true`):

### Add Header to All Requests

```
X-API-Key: your-api-key-here
```

### Example with cURL

```bash
curl -X POST http://localhost:8000/process_invoice \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"pdf_content": "{...}", "invoice_id": "INV-001"}'
```

---

## Best Practices

### 1. Error Handling

Always handle these scenarios:
- **Connection timeout:** Retry with exponential backoff
- **Rate limiting:** Wait and retry based on `Retry-After` header
- **Validation errors:** Log and alert for investigation
- **Server errors (5xx):** Retry up to 3 times

### 2. Confidence Thresholds

```javascript
if (confidence_score >= 0.9) {
    // High confidence - auto-process
} else if (confidence_score >= 0.7) {
    // Medium confidence - flag for review but process
} else {
    // Low confidence - escalate to human
}
```

### 3. Logging

Log these fields for audit trail:
- `invoice_id`
- `final_action`
- `confidence_score`
- `reasoning`
- `processing_time_seconds`
- Timestamp

### 4. Monitoring

Set up alerts for:
- High escalation rate (>20%)
- Low confidence scores (avg <0.7)
- Processing time spikes (>1s)
- API errors or timeouts

---

## Platform-Specific Tips

### UiPath
- Use Orchestrator Queues for escalated items
- Log Business Exceptions for failed RIK calls
- Use RE-Framework for robust retry logic

### Zapier
- Use Zapier's built-in retry (3 automatic retries)
- Add delay step before RIK call if rate limiting concerns
- Use Paths for complex decision logic

### Power Automate
- Use "Scope" for error handling
- Add "Delay" action for rate limiting
- Use Variables to store confidence scores

### Make.com
- Use Error Handlers on HTTP module
- Add Filters to prevent unnecessary downstream calls
- Use Aggregator for batch processing

---

## Example: End-to-End Invoice Automation

```
[Email arrives with PDF] →
[Extract PDF attachment] →
[POST to RIK] →
[Parse Response] →
Decision:
  ├─ approve + confidence >0.9 → [Create in ERP] → [Archive PDF] → [Send confirmation email]
  ├─ approve + confidence 0.7-0.9 → [Create in ERP] → [Flag for audit]
  ├─ escalate → [Add to review queue] → [Notify finance team]
  └─ reject → [Archive as rejected] → [Log reason]
```

---

## Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **Python SDK:** See `rik_sdk/` directory
- **JavaScript Client:** See `integrations/javascript/`
- **C# Client:** See `integrations/csharp/`
- **n8n Workflow:** See `demos/web_scraper_self_healing/`

---

## License

MIT
