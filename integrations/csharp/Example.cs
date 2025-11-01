/**
 * RIK C# Client - Example Usage
 * ==============================
 *
 * Build with: csc /reference:Newtonsoft.Json.dll RIKClient.cs Example.cs
 * Run with: ./Example.exe
 *
 * Or with dotnet:
 * - Add Newtonsoft.Json NuGet package
 * - dotnet build
 * - dotnet run
 */

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Newtonsoft.Json;
using RIK;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("🚀 RIK C# Client - Example Usage\n");

        using (var client = new RIKClient("http://localhost:8000"))
        {
            try
            {
                // ============================================================
                // Example 1: Health Check
                // ============================================================
                Console.WriteLine(new string('=', 60));
                Console.WriteLine("Example 1: Health Check");
                Console.WriteLine(new string('=', 60));

                bool isAlive = await client.IsAliveAsync();
                Console.WriteLine($"API is alive: {(isAlive ? "✓" : "✗")}");

                if (isAlive)
                {
                    var health = await client.GetHealthAsync();
                    Console.WriteLine($"Health status: {health.Status}");
                    Console.WriteLine("Subsystems:");
                    foreach (var system in health.Subsystems)
                    {
                        string icon = system.Value ? "✓" : "✗";
                        Console.WriteLine($"  {icon} {system.Key}");
                    }

                    var version = await client.GetVersionAsync();
                    Console.WriteLine($"\nVersion: {version.Version}");
                    Console.WriteLine($"Environment: {version.Environment}");
                }

                // ============================================================
                // Example 2: Process Invoice with Exceptions
                // ============================================================
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("Example 2: Process Invoice with Exceptions");
                Console.WriteLine(new string('=', 60));

                var invoiceData = new
                {
                    invoice_number = "INV-CS-001",
                    vendor_name = "Microsoft Corporation",
                    amount = 6500.00,
                    date = "2024-11-01",
                    po_number = "",  // Missing PO number - exception!
                    extraction_confidence = 0.25  // Low confidence - another exception!
                };

                Console.WriteLine("\n📄 Processing Invoice:");
                Console.WriteLine($"   Invoice #: {invoiceData.invoice_number}");
                Console.WriteLine($"   Vendor: {invoiceData.vendor_name}");
                Console.WriteLine($"   Amount: ${invoiceData.amount:N2}");
                Console.WriteLine($"   PO Number: {(string.IsNullOrEmpty(invoiceData.po_number) ? "(MISSING)" : invoiceData.po_number)}");
                Console.WriteLine($"   Confidence: {invoiceData.extraction_confidence:P0}");

                string pdfContent = JsonConvert.SerializeObject(invoiceData);
                var invoiceResult = await client.ProcessInvoiceAsync(
                    pdfContent,
                    invoiceData.invoice_number
                );

                Console.WriteLine("\n🧠 RIK Analysis:");
                Console.WriteLine($"   Final Action: {invoiceResult.FinalAction.ToUpper()}");
                Console.WriteLine($"   Confidence: {invoiceResult.ConfidenceScore:P0}");
                Console.WriteLine($"   Processing Time: {invoiceResult.ProcessingTimeSeconds:F3}s");
                Console.WriteLine($"   Exceptions Found: {invoiceResult.ExceptionsFound}");
                Console.WriteLine($"   Exceptions Resolved: {invoiceResult.ExceptionsResolved}");
                Console.WriteLine($"   Similar Cases: {invoiceResult.SimilarCasesFound}");

                Console.WriteLine("\n💡 Reasoning:");
                Console.WriteLine($"   {invoiceResult.Reasoning}");

                if (invoiceResult.TraditionalRPAWouldFail)
                {
                    Console.WriteLine("\n📊 RPA Comparison:");
                    Console.WriteLine("   ✗ Traditional RPA: WOULD FAIL");
                    Console.WriteLine("   ✓ RIK: SUCCESS");
                }

                if (invoiceResult.NeedsHumanReview())
                {
                    Console.WriteLine("\n⚠️  Escalated to human review");
                }
                else
                {
                    Console.WriteLine("\n✓  Fully automated (no human review needed)");
                }

                // ============================================================
                // Example 3: Recover Web Scraper Selector
                // ============================================================
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("Example 3: Recover Broken Selector");
                Console.WriteLine(new string('=', 60));

                string html = @"
                    <div class='product-card'>
                        <h2 class='product-title'>Premium Widget</h2>
                        <div class='pricing-container'>
                            <span class='price-tag price-current'>$99.99</span>
                        </div>
                    </div>
                ";

                string failedSelector = ".old-price";

                Console.WriteLine($"\n🔍 Attempting to recover selector:");
                Console.WriteLine($"   Failed Selector: {failedSelector}");
                Console.WriteLine($"   Target: Product price");

                var selectorResult = await client.RecoverSelectorAsync(
                    failedSelector,
                    html,
                    "https://example.com/products/widget",
                    new Dictionary<string, object>
                    {
                        { "target_element", "product price" },
                        { "example_value", "$99.99" }
                    }
                );

                Console.WriteLine("\n✓ Selector Recovered!");
                Console.WriteLine($"   New Selector: {selectorResult.RecoveredSelector}");
                Console.WriteLine($"   Type: {selectorResult.SelectorType}");
                Console.WriteLine($"   Confidence: {selectorResult.ConfidenceScore:P0}");

                Console.WriteLine("\n💡 Reasoning:");
                Console.WriteLine($"   {selectorResult.Reasoning}");

                // Test the recovered selector
                var testResult = await client.TestSelectorAsync(
                    selectorResult.RecoveredSelector,
                    html,
                    selectorResult.SelectorType
                );

                Console.WriteLine("\n🧪 Testing new selector:");
                Console.WriteLine($"   {(testResult.Success ? "✓" : "✗")} Selector works!");
                if (testResult.ElementCount > 0)
                {
                    Console.WriteLine($"   Matched {testResult.ElementCount} element(s)");
                }

                // ============================================================
                // Example 4: Performance Metrics & ROI
                // ============================================================
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("Example 4: Performance Metrics & ROI");
                Console.WriteLine(new string('=', 60));

                var metrics = await client.GetMetricsAsync();
                Console.WriteLine("\n📊 Performance Metrics:");
                Console.WriteLine($"   Efficiency: {metrics.Efficiency:P1}");
                Console.WriteLine($"   Total Episodes: {metrics.TotalEpisodes}");
                Console.WriteLine($"   Successful: {metrics.SuccessfulEpisodes}");
                Console.WriteLine($"   Failed: {metrics.FailedEpisodes}");

                var stats = await client.GetInvoiceStatsAsync();
                Console.WriteLine("\n💰 Invoice Processing ROI:");
                Console.WriteLine($"   Total Processed: {stats.TotalInvoicesProcessed:N0}");
                Console.WriteLine($"   RIK Automation Rate: {stats.AutomationRate:P1}");
                Console.WriteLine($"   Traditional RPA Rate: {stats.TraditionalRPAAutomationRate:P1}");
                Console.WriteLine($"   Improvement: {stats.AutomationImprovement}");
                Console.WriteLine($"   Annual Savings: ${stats.AnnualSavingsUSD:N2}");

                // ============================================================
                // Example 5: Batch Processing
                // ============================================================
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("Example 5: Batch Invoice Processing");
                Console.WriteLine(new string('=', 60));

                var invoices = new[]
                {
                    new { invoice_number = "INV-001", vendor_name = "Acme Corp", amount = 1000.0, po_number = "PO-123" },
                    new { invoice_number = "INV-002", vendor_name = "TechCo", amount = 5000.0, po_number = "" },  // Missing PO
                    new { invoice_number = "INV-003", vendor_name = "SupplyCo", amount = 15000.0, po_number = "PO-456" }
                };

                Console.WriteLine($"\n📋 Processing {invoices.Length} invoices...");

                var tasks = new List<Task<InvoiceProcessingResult>>();
                foreach (var inv in invoices)
                {
                    string content = JsonConvert.SerializeObject(inv);
                    tasks.Add(client.ProcessInvoiceAsync(content, inv.invoice_number));
                }

                var results = await Task.WhenAll(tasks);

                int automated = 0;
                int escalated = 0;
                foreach (var result in results)
                {
                    if (result.NeedsHumanReview())
                        escalated++;
                    else
                        automated++;
                }

                Console.WriteLine("\n📊 Batch Results:");
                Console.WriteLine($"   Total: {results.Length}");
                Console.WriteLine($"   Automated: {automated} ({(double)automated / results.Length:P0})");
                Console.WriteLine($"   Escalated: {escalated} ({(double)escalated / results.Length:P0})");

                Console.WriteLine("\n📋 Individual Results:");
                for (int i = 0; i < results.Length; i++)
                {
                    string icon = results[i].NeedsHumanReview() ? "⚠️" : "✓";
                    Console.WriteLine($"   {icon} {invoices[i].invoice_number}: {results[i].FinalAction.ToUpper()} " +
                                    $"(confidence: {results[i].ConfidenceScore:P0})");
                }

                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("✓ All examples completed!");
                Console.WriteLine(new string('=', 60));
            }
            catch (RIKAuthenticationException ex)
            {
                Console.WriteLine($"\n❌ Authentication Error: {ex.Message}");
            }
            catch (RIKValidationException ex)
            {
                Console.WriteLine($"\n❌ Validation Error: {ex.Message}");
            }
            catch (RIKException ex)
            {
                Console.WriteLine($"\n❌ RIK Error: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
                Console.WriteLine("   Make sure the RIK API is running:");
                Console.WriteLine("   $ python3 rik_api.py");
            }
        }
    }
}
