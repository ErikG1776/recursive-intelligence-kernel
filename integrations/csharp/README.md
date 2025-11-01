# RIK C#/.NET Client

Official C# client library for the Recursive Intelligence Kernel (RIK).
**Perfect for UiPath integration!**

## Features

- ✅ Compatible with .NET Framework 4.5+ and .NET Core/5+
- ✅ Async/await support for all operations
- ✅ Strongly-typed response models
- ✅ Comprehensive error handling
- ✅ API key authentication support
- ✅ Ready for UiPath integration

## Installation

### Via .NET CLI

```bash
dotnet add package Newtonsoft.Json
```

### Via NuGet Package Manager

```
Install-Package Newtonsoft.Json
```

### Manual Installation

1. Download `RIKClient.cs`
2. Add to your project
3. Add Newtonsoft.Json NuGet package

## Quick Start

```csharp
using RIK;
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        using (var client = new RIKClient("http://localhost:8000"))
        {
            // Check if API is alive
            bool isAlive = await client.IsAliveAsync();
            Console.WriteLine($"API Status: {(isAlive ? "Online" : "Offline")}");

            // Process an invoice
            string invoiceJson = @"{
                ""invoice_number"": ""INV-001"",
                ""vendor_name"": ""Acme Corp"",
                ""amount"": 5000,
                ""po_number"": """"
            }";

            var result = await client.ProcessInvoiceAsync(invoiceJson, "INV-001");

            Console.WriteLine($"Action: {result.FinalAction}");
            Console.WriteLine($"Confidence: {result.ConfidenceScore:P0}");
            Console.WriteLine($"Reasoning: {result.Reasoning}");
        }
    }
}
```

## UiPath Integration

### Method 1: HTTP Request Activity (No Code Required)

1. **Add HTTP Request Activity** to your workflow
2. **Configure:**
   - Endpoint: `http://localhost:8000/process_invoice`
   - Method: `POST`
   - Headers: `{"Content-Type": "application/json"}`
   - Body:
     ```json
     {
       "pdf_content": "{\"invoice_number\":\"INV-001\",\"amount\":5000}",
       "invoice_id": "INV-001"
     }
     ```
3. **Parse Response** using Deserialize JSON activity
4. **Access Result:** `response("final_action").ToString()`

### Method 2: Invoke Code Activity (Advanced)

1. **Add `RIKClient.cs`** to your UiPath project
2. **Add Newtonsoft.Json** NuGet package via UiPath Package Manager
3. **Use Invoke Code** activity:

```csharp
// In UiPath Invoke Code activity:
var client = new RIKClient("http://localhost:8000");
var result = await client.ProcessInvoiceAsync(invoiceData, "INV-001");
finalAction = result.FinalAction;  // Output argument
reasoning = result.Reasoning;      // Output argument
```

See `UIPATH_INTEGRATION.md` for complete workflow examples.

## API Reference

### Constructor

```csharp
var client = new RIKClient(baseUrl, apiKey, timeoutSeconds);
```

**Parameters:**
- `baseUrl` (string): Base URL of RIK API
- `apiKey` (string, optional): API key for authentication
- `timeoutSeconds` (int, optional): Request timeout (default: 30)

### Core Methods

#### ProcessInvoiceAsync

Process invoice with intelligent exception handling.

```csharp
var result = await client.ProcessInvoiceAsync(pdfContent, "INV-001");
Console.WriteLine(result.FinalAction);  // "approve", "reject", or "escalate"
Console.WriteLine(result.ConfidenceScore);  // 0.0 to 1.0
Console.WriteLine(result.Reasoning);
```

#### RecoverSelectorAsync

Recover broken web scraper selector.

```csharp
var result = await client.RecoverSelectorAsync(".old-class", html, url);
Console.WriteLine(result.RecoveredSelector);
Console.WriteLine(result.ConfidenceScore);
```

#### TestSelectorAsync

Test if a selector works.

```csharp
var result = await client.TestSelectorAsync(".product-price", html);
Console.WriteLine(result.Success);  // true/false
Console.WriteLine(result.ElementCount);
```

#### RunTaskAsync

Execute a reasoning task.

```csharp
var result = await client.RunTaskAsync("Analyze this exception");
Console.WriteLine(result.Reasoning);
```

### Monitoring Methods

- `IsAliveAsync()` - Check if API is alive
- `IsReadyAsync()` - Check if API is ready
- `GetHealthAsync()` - Get detailed health status
- `GetMetricsAsync()` - Get performance metrics
- `GetInvoiceStatsAsync()` - Get ROI statistics
- `GetVersionAsync()` - Get API version
- `GetMemoryAsync(limit)` - Get episodic memory

## Error Handling

```csharp
try
{
    var result = await client.ProcessInvoiceAsync(pdfContent);
}
catch (RIKAuthenticationException ex)
{
    Console.WriteLine("Authentication failed. Check API key.");
}
catch (RIKValidationException ex)
{
    Console.WriteLine($"Validation error: {ex.Message}");
}
catch (RIKRateLimitException ex)
{
    Console.WriteLine("Rate limit exceeded. Wait and retry.");
}
catch (RIKException ex)
{
    Console.WriteLine($"RIK error: {ex.Message}");
}
```

## Building and Running

### .NET 5/6/7

```bash
dotnet build
dotnet run
```

### .NET Framework

```bash
csc /reference:Newtonsoft.Json.dll RIKClient.cs Example.cs
./Example.exe
```

## Examples

Run the example program:

```bash
# Make sure RIK API is running
python3 ../../rik_api.py

# Run example
dotnet run
```

## License

MIT
