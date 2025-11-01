/**
 * RIK C#/.NET Client
 * ===================
 *
 * Official C# client library for the Recursive Intelligence Kernel (RIK).
 * Compatible with .NET Framework 4.5+ and .NET Core/5+
 * Perfect for UiPath integration.
 *
 * Example:
 *   var client = new RIKClient("http://localhost:8000");
 *   var result = await client.ProcessInvoiceAsync(pdfContent, "INV-001");
 *   Console.WriteLine(result.FinalAction);
 */

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace RIK
{
    /// <summary>
    /// Client for interacting with the Recursive Intelligence Kernel (RIK) API.
    /// </summary>
    public class RIKClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private readonly string _apiKey;

        /// <summary>
        /// Initializes a new instance of the RIKClient class.
        /// </summary>
        /// <param name="baseUrl">Base URL of the RIK API (e.g., "http://localhost:8000")</param>
        /// <param name="apiKey">Optional API key for authentication</param>
        /// <param name="timeoutSeconds">Request timeout in seconds (default: 30)</param>
        public RIKClient(string baseUrl, string apiKey = null, int timeoutSeconds = 30)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _apiKey = apiKey;

            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(timeoutSeconds)
            };

            _httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json")
            );

            if (!string.IsNullOrEmpty(_apiKey))
            {
                _httpClient.DefaultRequestHeaders.Add("X-API-Key", _apiKey);
            }
        }

        // ====================================================================
        // CORE ENDPOINTS
        // ====================================================================

        /// <summary>
        /// Execute a reasoning task.
        /// </summary>
        public async Task<TaskResult> RunTaskAsync(string task)
        {
            var payload = new { task = task };
            var response = await PostAsync<JObject>("/run_task", payload);
            return new TaskResult(response);
        }

        /// <summary>
        /// Process invoice with intelligent exception handling.
        /// </summary>
        public async Task<InvoiceProcessingResult> ProcessInvoiceAsync(
            string pdfContent,
            string invoiceId = null,
            Dictionary<string, object> context = null)
        {
            var payload = new
            {
                pdf_content = pdfContent,
                invoice_id = invoiceId,
                context = context
            };

            var response = await PostAsync<JObject>("/process_invoice", payload);
            return new InvoiceProcessingResult(response);
        }

        /// <summary>
        /// Recover broken web scraper selector.
        /// </summary>
        public async Task<SelectorRecoveryResult> RecoverSelectorAsync(
            string failedSelector,
            string html,
            string url,
            Dictionary<string, object> context = null)
        {
            var payload = new
            {
                failed_selector = failedSelector,
                html = html,
                url = url,
                context = context
            };

            var response = await PostAsync<JObject>("/recover_selector", payload);
            return new SelectorRecoveryResult(response);
        }

        /// <summary>
        /// Test if a selector works on given HTML.
        /// </summary>
        public async Task<SelectorTestResult> TestSelectorAsync(
            string selector,
            string html,
            string selectorType = "css")
        {
            var payload = new
            {
                selector = selector,
                html = html,
                selector_type = selectorType
            };

            var response = await PostAsync<JObject>("/test_selector", payload);
            return new SelectorTestResult(response);
        }

        // ====================================================================
        // MONITORING & ANALYTICS
        // ====================================================================

        /// <summary>
        /// Get API health status.
        /// </summary>
        public async Task<HealthStatus> GetHealthAsync()
        {
            var response = await GetAsync<JObject>("/health");
            return new HealthStatus(response);
        }

        /// <summary>
        /// Check if API is alive (simple liveness check).
        /// </summary>
        public async Task<bool> IsAliveAsync()
        {
            try
            {
                var response = await GetAsync<JObject>("/health/live");
                return response["status"]?.ToString() == "alive";
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Check if API is ready to handle requests.
        /// </summary>
        public async Task<bool> IsReadyAsync()
        {
            try
            {
                var response = await GetAsync<JObject>("/health/ready");
                return response["status"]?.ToString() == "ready";
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Get performance and efficiency metrics.
        /// </summary>
        public async Task<MetricsResponse> GetMetricsAsync()
        {
            var response = await GetAsync<JObject>("/metrics");
            return new MetricsResponse(response);
        }

        /// <summary>
        /// Get invoice processing statistics and ROI data.
        /// </summary>
        public async Task<InvoiceStats> GetInvoiceStatsAsync()
        {
            var response = await GetAsync<JObject>("/invoice_stats");
            return new InvoiceStats(response);
        }

        /// <summary>
        /// Get API version information.
        /// </summary>
        public async Task<VersionInfo> GetVersionAsync()
        {
            var response = await GetAsync<JObject>("/version");
            return new VersionInfo(response);
        }

        /// <summary>
        /// Retrieve episodic memory entries.
        /// </summary>
        public async Task<List<JObject>> GetMemoryAsync(int limit = 10)
        {
            var response = await GetAsync<JObject>($"/memory?limit={limit}");
            var episodes = response["episodes"]?.ToObject<List<JObject>>();
            return episodes ?? new List<JObject>();
        }

        // ====================================================================
        // HTTP REQUEST HELPERS
        // ====================================================================

        private async Task<T> GetAsync<T>(string endpoint)
        {
            var url = $"{_baseUrl}{endpoint}";
            var response = await _httpClient.GetAsync(url);
            await EnsureSuccessStatusCodeAsync(response);

            var content = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(content);
        }

        private async Task<T> PostAsync<T>(string endpoint, object data)
        {
            var url = $"{_baseUrl}{endpoint}";
            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(url, content);
            await EnsureSuccessStatusCodeAsync(response);

            var responseContent = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(responseContent);
        }

        private async Task EnsureSuccessStatusCodeAsync(HttpResponseMessage response)
        {
            if (response.IsSuccessStatusCode)
                return;

            var errorContent = await response.Content.ReadAsStringAsync();
            var statusCode = (int)response.StatusCode;

            switch (statusCode)
            {
                case 401:
                case 403:
                    throw new RIKAuthenticationException("Authentication failed. Check your API key.");

                case 422:
                    throw new RIKValidationException($"Validation error: {errorContent}");

                case 429:
                    throw new RIKRateLimitException("Rate limit exceeded");

                default:
                    throw new RIKAPIException($"API request failed with status {statusCode}: {errorContent}");
            }
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }

    // ========================================================================
    // RESPONSE MODELS
    // ========================================================================

    public class InvoiceProcessingResult
    {
        public string InvoiceId { get; set; }
        public string FinalAction { get; set; }
        public double ConfidenceScore { get; set; }
        public string Reasoning { get; set; }
        public int ExceptionsFound { get; set; }
        public int ExceptionsResolved { get; set; }
        public double ProcessingTimeSeconds { get; set; }
        public bool TraditionalRPAWouldFail { get; set; }
        public int SimilarCasesFound { get; set; }
        public int StrategiesSimulated { get; set; }

        public InvoiceProcessingResult(JObject data)
        {
            InvoiceId = data["invoice_id"]?.ToString();
            FinalAction = data["final_action"]?.ToString();
            ConfidenceScore = data["confidence_score"]?.ToObject<double>() ?? 0.0;
            Reasoning = data["reasoning"]?.ToString();
            ExceptionsFound = data["exceptions_found"]?.ToObject<int>() ?? 0;
            ExceptionsResolved = data["exceptions_resolved"]?.ToObject<int>() ?? 0;
            ProcessingTimeSeconds = data["processing_time_seconds"]?.ToObject<double>() ?? 0.0;
            TraditionalRPAWouldFail = data["traditional_rpa_would_fail"]?.ToObject<bool>() ?? false;
            SimilarCasesFound = data["similar_cases_found"]?.ToObject<int>() ?? 0;
            StrategiesSimulated = data["strategies_simulated"]?.ToObject<int>() ?? 0;
        }

        public bool NeedsHumanReview()
        {
            return FinalAction == "escalate" || ConfidenceScore < 0.7;
        }
    }

    public class SelectorRecoveryResult
    {
        public string RecoveredSelector { get; set; }
        public string SelectorType { get; set; }
        public double ConfidenceScore { get; set; }
        public string Reasoning { get; set; }
        public double ProcessingTimeSeconds { get; set; }
        public List<string> FallbackStrategies { get; set; }

        public SelectorRecoveryResult(JObject data)
        {
            RecoveredSelector = data["recovered_selector"]?.ToString();
            SelectorType = data["selector_type"]?.ToString();
            ConfidenceScore = data["confidence_score"]?.ToObject<double>() ?? 0.0;
            Reasoning = data["reasoning"]?.ToString();
            ProcessingTimeSeconds = data["processing_time_seconds"]?.ToObject<double>() ?? 0.0;
            FallbackStrategies = data["fallback_strategies"]?.ToObject<List<string>>() ?? new List<string>();
        }
    }

    public class SelectorTestResult
    {
        public bool Success { get; set; }
        public int ElementCount { get; set; }
        public string SampleText { get; set; }

        public SelectorTestResult(JObject data)
        {
            Success = data["success"]?.ToObject<bool>() ?? false;
            ElementCount = data["element_count"]?.ToObject<int>() ?? 0;
            SampleText = data["sample_text"]?.ToString();
        }
    }

    public class TaskResult
    {
        public string Task { get; set; }
        public string Result { get; set; }
        public string Reasoning { get; set; }
        public double ProcessingTimeSeconds { get; set; }

        public TaskResult(JObject data)
        {
            Task = data["task"]?.ToString();
            Result = data["result"]?.ToString();
            Reasoning = data["reasoning"]?.ToString();
            ProcessingTimeSeconds = data["processing_time_seconds"]?.ToObject<double>() ?? 0.0;
        }
    }

    public class HealthStatus
    {
        public string Status { get; set; }
        public Dictionary<string, bool> Subsystems { get; set; }

        public HealthStatus(JObject data)
        {
            Status = data["status"]?.ToString();
            Subsystems = data["subsystems"]?.ToObject<Dictionary<string, bool>>() ?? new Dictionary<string, bool>();
        }

        public bool IsHealthy()
        {
            return Status == "healthy" || Status == "alive";
        }
    }

    public class MetricsResponse
    {
        public double Efficiency { get; set; }
        public int TotalEpisodes { get; set; }
        public int SuccessfulEpisodes { get; set; }
        public int FailedEpisodes { get; set; }

        public MetricsResponse(JObject data)
        {
            var metrics = data["metrics"] ?? data;
            Efficiency = metrics["efficiency"]?.ToObject<double>() ?? 0.0;
            TotalEpisodes = metrics["total_episodes"]?.ToObject<int>() ?? 0;
            SuccessfulEpisodes = metrics["successful_episodes"]?.ToObject<int>() ?? 0;
            FailedEpisodes = metrics["failed_episodes"]?.ToObject<int>() ?? 0;
        }
    }

    public class InvoiceStats
    {
        public int TotalInvoicesProcessed { get; set; }
        public int InvoicesWithExceptions { get; set; }
        public int ExceptionsAutoResolved { get; set; }
        public int ExceptionsEscalated { get; set; }
        public double AutomationRate { get; set; }
        public double TraditionalRPAAutomationRate { get; set; }
        public double AnnualSavingsUSD { get; set; }
        public string AutomationImprovement { get; set; }

        public InvoiceStats(JObject data)
        {
            var stats = data["stats"] ?? data;
            TotalInvoicesProcessed = stats["total_invoices_processed"]?.ToObject<int>() ?? 0;
            InvoicesWithExceptions = stats["invoices_with_exceptions"]?.ToObject<int>() ?? 0;
            ExceptionsAutoResolved = stats["exceptions_auto_resolved"]?.ToObject<int>() ?? 0;
            ExceptionsEscalated = stats["exceptions_escalated"]?.ToObject<int>() ?? 0;
            AutomationRate = stats["automation_rate"]?.ToObject<double>() ?? 0.0;
            TraditionalRPAAutomationRate = stats["traditional_rpa_automation_rate"]?.ToObject<double>() ?? 0.0;
            AnnualSavingsUSD = stats["annual_savings_usd"]?.ToObject<double>() ?? 0.0;
            AutomationImprovement = stats["automation_improvement"]?.ToString();
        }
    }

    public class VersionInfo
    {
        public string Version { get; set; }
        public string Environment { get; set; }

        public VersionInfo(JObject data)
        {
            Version = data["version"]?.ToString();
            Environment = data["environment"]?.ToString();
        }
    }

    // ========================================================================
    // EXCEPTION CLASSES
    // ========================================================================

    public class RIKException : Exception
    {
        public RIKException(string message) : base(message) { }
        public RIKException(string message, Exception innerException) : base(message, innerException) { }
    }

    public class RIKAPIException : RIKException
    {
        public RIKAPIException(string message) : base(message) { }
    }

    public class RIKAuthenticationException : RIKAPIException
    {
        public RIKAuthenticationException(string message) : base(message) { }
    }

    public class RIKValidationException : RIKAPIException
    {
        public RIKValidationException(string message) : base(message) { }
    }

    public class RIKRateLimitException : RIKAPIException
    {
        public RIKRateLimitException(string message) : base(message) { }
    }
}
