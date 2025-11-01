"""
RIK SDK Models
==============

Type-safe data models for RIK API requests and responses.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================
# Invoice Processing
# ============================================================

@dataclass
class InvoiceProcessingResult:
    """Result of invoice processing with exception handling."""

    invoice_id: str
    final_action: str  # "approve", "reject", "escalate"
    confidence_score: float
    reasoning: str
    exceptions_found: int
    exceptions_resolved: int
    processing_time_seconds: float
    traditional_rpa_would_fail: bool
    similar_cases_found: int = 0
    strategies_simulated: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvoiceProcessingResult":
        """Create from API response dictionary."""
        return cls(
            invoice_id=data.get("invoice_id", "unknown"),
            final_action=data.get("final_action", "unknown"),
            confidence_score=data.get("confidence_score", 0.0),
            reasoning=data.get("reasoning", ""),
            exceptions_found=data.get("exceptions_found", 0),
            exceptions_resolved=data.get("exceptions_resolved", 0),
            processing_time_seconds=data.get("processing_time_seconds", 0.0),
            traditional_rpa_would_fail=data.get("traditional_rpa_would_fail", False),
            similar_cases_found=data.get("similar_cases_found", 0),
            strategies_simulated=data.get("strategies_simulated", 0),
            metadata=data.get("metadata", {}),
        )

    def is_successful(self) -> bool:
        """Check if invoice was successfully processed (approved or rejected with high confidence)."""
        return self.final_action in ["approve", "reject"] and self.confidence_score >= 0.7

    def needs_human_review(self) -> bool:
        """Check if invoice needs human review."""
        return self.final_action == "escalate" or self.confidence_score < 0.7


# ============================================================
# Selector Recovery
# ============================================================

@dataclass
class SelectorRecoveryResult:
    """Result of web scraper selector recovery."""

    recovered_selector: str
    selector_type: str  # "css" or "xpath"
    confidence_score: float
    reasoning: str
    processing_time_seconds: float
    fallback_strategies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelectorRecoveryResult":
        """Create from API response dictionary."""
        return cls(
            recovered_selector=data.get("recovered_selector", ""),
            selector_type=data.get("selector_type", "css"),
            confidence_score=data.get("confidence_score", 0.0),
            reasoning=data.get("reasoning", ""),
            processing_time_seconds=data.get("processing_time_seconds", 0.0),
            fallback_strategies=data.get("fallback_strategies", []),
            metadata=data.get("metadata", {}),
        )

    def is_confident(self) -> bool:
        """Check if recovery result is confident enough to use."""
        return self.confidence_score >= 0.8


# ============================================================
# Health Status
# ============================================================

@dataclass
class HealthStatus:
    """Health status of RIK API."""

    status: str  # "healthy", "degraded", "unhealthy"
    subsystems: Dict[str, bool] = field(default_factory=dict)
    checks: Dict[str, bool] = field(default_factory=dict)
    version: Optional[str] = None
    environment: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthStatus":
        """Create from API response dictionary."""
        return cls(
            status=data.get("status", "unknown"),
            subsystems=data.get("subsystems", {}),
            checks=data.get("checks", {}),
            version=data.get("version"),
            environment=data.get("environment"),
        )

    def is_healthy(self) -> bool:
        """Check if all subsystems are healthy."""
        return self.status == "healthy" or self.status == "alive"


# ============================================================
# Metrics (Fixed for Float + Dict Formats)
# ============================================================

@dataclass
class MetricsResponse:
    """RIK performance and efficiency metrics."""

    efficiency: float
    total_episodes: int
    successful_episodes: int
    failed_episodes: int
    avg_processing_time_seconds: float
    uptime_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricsResponse":
        """Create from API response dictionary.
        Handles both float (efficiency only) and dict formats."""
        # Case 1: API returns a single float
        if isinstance(data, float):
            return cls(
                efficiency=data,
                total_episodes=0,
                successful_episodes=0,
                failed_episodes=0,
                avg_processing_time_seconds=0.0,
            )

        # Case 2: metrics key exists and is a float
        metrics_data = data.get("metrics", data)
        if isinstance(metrics_data, float):
            return cls(
                efficiency=metrics_data,
                total_episodes=0,
                successful_episodes=0,
                failed_episodes=0,
                avg_processing_time_seconds=0.0,
            )

        # Case 3: metrics is a dict (structured response)
        return cls(
            efficiency=metrics_data.get("efficiency", 0.0),
            total_episodes=metrics_data.get("total_episodes", 0),
            successful_episodes=metrics_data.get("successful_episodes", 0),
            failed_episodes=metrics_data.get("failed_episodes", 0),
            avg_processing_time_seconds=metrics_data.get("avg_processing_time_seconds", 0.0),
            uptime_seconds=metrics_data.get("uptime_seconds"),
            metadata=data.get("metadata", {}),
        )


# ============================================================
# Invoice Statistics
# ============================================================

@dataclass
class InvoiceStats:
    """Statistics for invoice processing automation."""

    total_invoices_processed: int
    invoices_with_exceptions: int
    exceptions_auto_resolved: int
    exceptions_escalated: int
    automation_rate: float
    traditional_rpa_automation_rate: float
    annual_savings_usd: float
    automation_improvement: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvoiceStats":
        """Create from API response dictionary."""
        stats = data.get("stats", data)
        return cls(
            total_invoices_processed=stats.get("total_invoices_processed", 0),
            invoices_with_exceptions=stats.get("invoices_with_exceptions", 0),
            exceptions_auto_resolved=stats.get("exceptions_auto_resolved", 0),
            exceptions_escalated=stats.get("exceptions_escalated", 0),
            automation_rate=stats.get("automation_rate", 0.0),
            traditional_rpa_automation_rate=stats.get("traditional_rpa_automation_rate", 0.0),
            annual_savings_usd=stats.get("annual_savings_usd", 0.0),
            automation_improvement=stats.get("automation_improvement", "0%"),
        )


# ============================================================
# Task Result
# ============================================================

@dataclass
class TaskResult:
    """Result of a reasoning task."""

    task: str
    result: str
    reasoning: str
    processing_time_seconds: float
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """Create from API response dictionary."""
        return cls(
            task=data.get("task", ""),
            result=data.get("result", ""),
            reasoning=data.get("reasoning", ""),
            processing_time_seconds=data.get("processing_time_seconds", 0.0),
            confidence_score=data.get("confidence_score"),
            metadata=data.get("metadata", {}),
        )