# RIK JavaScript/Node.js Client

Official JavaScript client library for the Recursive Intelligence Kernel (RIK).

## Features

- ✅ Works in both Node.js and browser environments
- ✅ Promise-based API with async/await support
- ✅ Automatic retries with exponential backoff
- ✅ Comprehensive error handling
- ✅ API key authentication support
- ✅ Request timeout management
- ✅ TypeScript-friendly (JSDoc types included)

## Installation

### Node.js

```bash
# Install dependencies
npm install

# Or manually install node-fetch
npm install node-fetch
```

### Browser

```html
<script src="rik-client.js"></script>
```

## Quick Start

### Node.js Example

```javascript
const RIKClient = require('./rik-client');

async function main() {
    // Create client
    const client = new RIKClient('http://localhost:8000');

    // Check if API is alive
    if (await client.isAlive()) {
        console.log('✓ API is running');
    }

    // Process an invoice
    const invoiceData = {
        invoice_number: 'INV-001',
        vendor_name: 'Acme Corp',
        amount: 5000,
        po_number: ''  // Missing PO - RIK will handle this!
    };

    const result = await client.processInvoice(
        JSON.stringify(invoiceData),
        'INV-001'
    );

    console.log(`Action: ${result.final_action}`);
    console.log(`Reasoning: ${result.reasoning}`);
}

main();
```

### Browser Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>RIK Client Example</title>
    <script src="rik-client.js"></script>
</head>
<body>
    <button onclick="processInvoice()">Process Invoice</button>

    <script>
        const client = new RIKClient('http://localhost:8000');

        async function processInvoice() {
            try {
                const invoiceData = {
                    invoice_number: 'INV-001',
                    vendor_name: 'Acme Corp',
                    amount: 5000
                };

                const result = await client.processInvoice(
                    JSON.stringify(invoiceData),
                    'INV-001'
                );

                alert(`Action: ${result.final_action}\nConfidence: ${result.confidence_score}`);
            } catch (error) {
                console.error('Error:', error);
            }
        }
    </script>
</body>
</html>
```

## API Reference

### Constructor

```javascript
new RIKClient(baseUrl, options)
```

**Parameters:**
- `baseUrl` (string): Base URL of RIK API (e.g., 'http://localhost:8000')
- `options` (object, optional):
  - `apiKey` (string): API key for authentication
  - `timeout` (number): Request timeout in milliseconds (default: 30000)
  - `maxRetries` (number): Maximum number of retries (default: 3)

### Core Methods

#### processInvoice(pdfContent, invoiceId, context)

Process invoice with intelligent exception handling.

```javascript
const result = await client.processInvoice(pdfContent, 'INV-001');
console.log(result.final_action);  // "approve", "reject", or "escalate"
```

#### recoverSelector(failedSelector, html, url, context)

Recover broken web scraper selector.

```javascript
const result = await client.recoverSelector('.old-class', html, 'https://example.com');
console.log(result.recovered_selector);
```

#### testSelector(selector, html, selectorType)

Test if a selector works on given HTML.

```javascript
const result = await client.testSelector('.product-price', html);
console.log(result.success);  // true/false
```

#### runTask(task)

Execute a reasoning task.

```javascript
const result = await client.runTask('Analyze this exception');
console.log(result.reasoning);
```

### Monitoring Methods

#### isAlive()

Check if API is alive.

```javascript
const alive = await client.isAlive();  // returns boolean
```

#### isReady()

Check if API is ready to handle requests.

```javascript
const ready = await client.isReady();  // returns boolean
```

#### getHealth()

Get detailed health status.

```javascript
const health = await client.getHealth();
console.log(health.status);
console.log(health.subsystems);
```

#### getMetrics()

Get performance metrics.

```javascript
const metrics = await client.getMetrics();
console.log(`Efficiency: ${metrics.efficiency}`);
```

#### getInvoiceStats()

Get invoice processing statistics and ROI.

```javascript
const stats = await client.getInvoiceStats();
console.log(`Automation rate: ${stats.automation_rate}`);
console.log(`Annual savings: $${stats.annual_savings_usd}`);
```

#### getVersion()

Get API version information.

```javascript
const version = await client.getVersion();
console.log(`Version: ${version.version}`);
```

#### getMemory(limit)

Retrieve episodic memory entries.

```javascript
const episodes = await client.getMemory(10);
episodes.forEach(ep => console.log(ep.task));
```

## Error Handling

The client throws specific error types for different failure scenarios:

```javascript
const {
    RIKError,
    RIKConnectionError,
    RIKAPIError,
    RIKAuthenticationError,
    RIKValidationError,
    RIKTimeoutError,
    RIKRateLimitError
} = require('./rik-client');

try {
    const result = await client.processInvoice(pdfContent);
} catch (error) {
    if (error instanceof RIKConnectionError) {
        console.error('Cannot connect to API:', error.url);
    } else if (error instanceof RIKAuthenticationError) {
        console.error('Authentication failed. Check API key.');
    } else if (error instanceof RIKValidationError) {
        console.error('Validation error:', error.validationErrors);
    } else if (error instanceof RIKTimeoutError) {
        console.error(`Request timed out after ${error.timeoutSeconds}s`);
    } else if (error instanceof RIKRateLimitError) {
        console.error(`Rate limited. Retry after ${error.retryAfter}s`);
    } else {
        console.error('API error:', error.message);
    }
}
```

## Examples

Run the example script:

```bash
# Make sure RIK API is running
python3 ../../rik_api.py

# Run examples
node example.js
```

## License

MIT
