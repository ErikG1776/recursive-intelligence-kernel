"""
RIK Python SDK
==============

Official Python client library for the Recursive Intelligence Kernel (RIK).

Example:
    >>> from rik_sdk import RIKClient
    >>> client = RIKClient("http://localhost:8000")
    >>> result = client.process_invoice(pdf_content="...", invoice_id="INV-001")
    >>> print(result.final_action)  # "approve" or "reject" or "escalate"

For more examples, see the examples/ directory.
"""

__version__ = "1.0.0"
__author__ = "RIK Team"

from rik_sdk.client import RIKClient
from rik_sdk.exceptions import (
    RIKError,
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

__all__ = [
    # Client
    "RIKClient",

    # Exceptions
    "RIKError",
    "RIKConnectionError",
    "RIKAPIError",
    "RIKAuthenticationError",
    "RIKValidationError",
    "RIKTimeoutError",
    "RIKRateLimitError",

    # Models
    "InvoiceProcessingResult",
    "SelectorRecoveryResult",
    "HealthStatus",
    "MetricsResponse",
    "InvoiceStats",
    "TaskResult",
]
