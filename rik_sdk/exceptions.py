"""
RIK SDK Exceptions
==================

Custom exception classes for the RIK Python SDK.
"""

from typing import Optional, Dict, Any


class RIKError(Exception):
    """Base exception for all RIK SDK errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class RIKConnectionError(RIKError):
    """Raised when unable to connect to RIK API."""

    def __init__(self, url: str, original_error: Optional[Exception] = None):
        message = f"Failed to connect to RIK API at {url}"
        details = {"url": url}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(message, details)
        self.url = url
        self.original_error = original_error


class RIKAPIError(RIKError):
    """Raised when RIK API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        details = {
            "status_code": status_code,
            "endpoint": endpoint,
        }
        if response_body:
            details["response_body"] = response_body
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint


class RIKAuthenticationError(RIKAPIError):
    """Raised when API authentication fails (401/403)."""

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(
            message="Authentication failed. Check your API key.",
            status_code=401,
            endpoint=endpoint,
        )


class RIKValidationError(RIKAPIError):
    """Raised when request validation fails (422)."""

    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        details = {"validation_errors": validation_errors} if validation_errors else {}
        super().__init__(
            message=f"Validation error: {message}",
            status_code=422,
        )
        if validation_errors:
            self.details.update(details)


class RIKTimeoutError(RIKError):
    """Raised when a request times out."""

    def __init__(self, timeout_seconds: float, endpoint: Optional[str] = None):
        message = f"Request timed out after {timeout_seconds}s"
        details = {"timeout_seconds": timeout_seconds, "endpoint": endpoint}
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds
        self.endpoint = endpoint


class RIKRateLimitError(RIKAPIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message=message, status_code=429)
        self.retry_after = retry_after
