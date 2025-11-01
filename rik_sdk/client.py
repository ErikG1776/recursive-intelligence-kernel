"""
RIK Python Client
=================

Production-ready Python client for the Recursive Intelligence Kernel (RIK) API.
"""

import requests
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rik_sdk.exceptions import (
    RIKConnectionError,
    RIKAPIError,
    RIKAuthenticationError,
    RIKValidationError,
    RIKTimeoutError,
    RIKRateLimitError,
)
from rik_sdk.models import (
    InvoiceProcessingResult,
    SelectorRecoveryResult,
    HealthStatus,
    MetricsResponse,
    InvoiceStats,
    TaskResult,
)


class RIKClient:
    """
    Professional Python SDK for the Recursive Intelligence Kernel (RIK) API.

    Features:
    - Type-safe request/response models
    - Automatic retries with exponential backoff
    - Connection pooling
    - Comprehensive error handling
    - API key authentication support
    - Request timeout management

    Example:
        >>> client = RIKClient("http://localhost:8000", api_key="your-key")
        >>> result = client.process_invoice(pdf_content="...", invoice_id="INV-001")
        >>> print(result.final_action)
        "approve"
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """
        Initialize RIK client.

        Args:
            base_url: Base URL of RIK API (default: http://127.0.0.1:8000)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            verify_ssl: Verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Setup session with connection pooling and retries
        self.session = requests.Session()

        # Retry strategy: retry on connection errors and 5xx errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s, 8s...
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including API key if set."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/health")
            json_data: JSON request body
            params: URL query parameters

        Returns:
            Response JSON data

        Raises:
            RIKConnectionError: Connection failed
            RIKAuthenticationError: Authentication failed (401/403)
            RIKValidationError: Request validation failed (422)
            RIKRateLimitError: Rate limit exceeded (429)
            RIKAPIError: Other API errors
            RIKTimeoutError: Request timed out
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            # Handle specific HTTP error codes
            if response.status_code == 401 or response.status_code == 403:
                raise RIKAuthenticationError(endpoint=endpoint)

            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise RIKValidationError(
                    message=error_data.get("detail", "Validation error"),
                    validation_errors=error_data.get("errors"),
                )

            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RIKRateLimitError(
                    retry_after=int(retry_after) if retry_after else None
                )

            elif response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass

                raise RIKAPIError(
                    message=error_msg,
                    status_code=response.status_code,
                    response_body=response.text[:500],
                    endpoint=endpoint,
                )

            # Parse successful response
            return response.json() if response.content else {}

        except requests.exceptions.Timeout:
            raise RIKTimeoutError(timeout_seconds=self.timeout, endpoint=endpoint)

        except requests.exceptions.ConnectionError as e:
            raise RIKConnectionError(url=url, original_error=e)

        except (RIKConnectionError, RIKAPIError, RIKAuthenticationError,
                RIKValidationError, RIKTimeoutError, RIKRateLimitError):
            # Re-raise RIK exceptions
            raise

        except Exception as e:
            # Wrap unexpected exceptions
            raise RIKAPIError(
                message=f"Unexpected error: {str(e)}",
                status_code=0,
                endpoint=endpoint,
            )

    # ========================================================================
    # CORE ENDPOINTS
    # ========================================================================

    def run_task(self, task: str) -> TaskResult:
        """
        Execute a reasoning task.

        Args:
            task: Task description to process

        Returns:
            TaskResult with reasoning output

        Example:
            >>> result = client.run_task("Analyze this exception and suggest a solution")
            >>> print(result.reasoning)
        """
        data = self._request("POST", "/run_task", json_data={"task": task})
        return TaskResult.from_dict(data)

    def process_invoice(
        self,
        pdf_content: str,
        invoice_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> InvoiceProcessingResult:
        """
        Process invoice with intelligent exception handling.

        Args:
            pdf_content: PDF content as string or JSON
            invoice_id: Optional invoice identifier
            context: Optional additional context

        Returns:
            InvoiceProcessingResult with decision and reasoning

        Example:
            >>> import json
            >>> invoice_data = json.dumps({"invoice_number": "INV-001", "amount": 4500})
            >>> result = client.process_invoice(pdf_content=invoice_data, invoice_id="INV-001")
            >>> print(f"Action: {result.final_action}, Confidence: {result.confidence_score}")
        """
        payload = {
            "pdf_content": pdf_content,
            "invoice_id": invoice_id,
            "context": context,
        }
        data = self._request("POST", "/process_invoice", json_data=payload)
        return InvoiceProcessingResult.from_dict(data)

    def recover_selector(
        self,
        failed_selector: str,
        html: str,
        url: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SelectorRecoveryResult:
        """
        Recover broken web scraper selector.

        Args:
            failed_selector: The selector that stopped working
            html: Current HTML content
            url: URL being scraped
            context: Optional context about what should be selected

        Returns:
            SelectorRecoveryResult with new selector and reasoning

        Example:
            >>> result = client.recover_selector(
            ...     failed_selector=".old-class",
            ...     html="<html>...</html>",
            ...     url="https://example.com"
            ... )
            >>> print(f"New selector: {result.recovered_selector}")
        """
        payload = {
            "failed_selector": failed_selector,
            "html": html,
            "url": url,
            "context": context,
        }
        data = self._request("POST", "/recover_selector", json_data=payload)
        return SelectorRecoveryResult.from_dict(data)

    def test_selector(
        self,
        selector: str,
        html: str,
        selector_type: str = "css",
    ) -> Dict[str, Any]:
        """
        Test if a selector works on given HTML.

        Args:
            selector: CSS or XPath selector to test
            html: HTML content to test against
            selector_type: "css" or "xpath" (default: "css")

        Returns:
            Dict with success status and matched elements

        Example:
            >>> result = client.test_selector(".product-price", "<div class='product-price'>$10</div>")
            >>> print(result["success"])
        """
        payload = {
            "selector": selector,
            "html": html,
            "selector_type": selector_type,
        }
        return self._request("POST", "/test_selector", json_data=payload)

    # ========================================================================
    # MONITORING & ANALYTICS
    # ========================================================================

    def get_health(self) -> HealthStatus:
        """
        Get API health status.

        Returns:
            HealthStatus with subsystem health checks

        Example:
            >>> health = client.get_health()
            >>> if health.is_healthy():
            ...     print("All systems operational")
        """
        data = self._request("GET", "/health")
        return HealthStatus.from_dict(data)

    def is_alive(self) -> bool:
        """
        Check if API is alive (simple liveness check).

        Returns:
            True if API is responding

        Example:
            >>> if client.is_alive():
            ...     print("API is up")
        """
        try:
            data = self._request("GET", "/health/live")
            return data.get("status") == "alive"
        except:
            return False

    def is_ready(self) -> bool:
        """
        Check if API is ready to handle requests.

        Returns:
            True if API is ready

        Example:
            >>> if client.is_ready():
            ...     print("API is ready to accept requests")
        """
        try:
            data = self._request("GET", "/health/ready")
            return data.get("status") == "ready"
        except:
            return False

    def get_metrics(self) -> MetricsResponse:
        """
        Get performance and efficiency metrics.

        Returns:
            MetricsResponse with efficiency stats

        Example:
            >>> metrics = client.get_metrics()
            >>> print(f"Efficiency: {metrics.efficiency:.1%}")
        """
        data = self._request("GET", "/metrics")
        return MetricsResponse.from_dict(data)

    def get_invoice_stats(self) -> InvoiceStats:
        """
        Get invoice processing statistics and ROI data.

        Returns:
            InvoiceStats with automation rates and savings

        Example:
            >>> stats = client.get_invoice_stats()
            >>> print(f"Automation rate: {stats.automation_rate:.1%}")
            >>> print(f"Annual savings: ${stats.annual_savings_usd:,.2f}")
        """
        data = self._request("GET", "/invoice_stats")
        return InvoiceStats.from_dict(data)

    def get_version(self) -> Dict[str, str]:
        """
        Get API version information.

        Returns:
            Dict with version and environment

        Example:
            >>> version_info = client.get_version()
            >>> print(f"RIK v{version_info['version']}")
        """
        return self._request("GET", "/version")

    def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve episodic memory entries.

        Args:
            limit: Maximum number of entries to return (default: 10)

        Returns:
            List of memory episodes

        Example:
            >>> episodes = client.get_memory(limit=5)
            >>> for episode in episodes:
            ...     print(episode["task"])
        """
        data = self._request("GET", "/memory", params={"limit": limit})
        return data.get("episodes", [])

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def close(self):
        """Close the HTTP session and clean up resources."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.close()

    def __repr__(self):
        return f"RIKClient(base_url='{self.base_url}', authenticated={self.api_key is not None})"
