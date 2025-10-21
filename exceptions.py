"""
exceptions.py | Recursive Intelligence Kernel (RIK)
--------------------------------------------------------------------
Custom exception classes for better error handling and debugging
across the RIK system.
"""


class RIKException(Exception):
    """Base exception class for all RIK-specific errors."""
    pass


class MemoryException(RIKException):
    """Raised when memory operations fail."""
    pass


class SchemaValidationException(RIKException):
    """Raised when task schema validation fails."""
    pass


class ReasoningException(RIKException):
    """Raised when reasoning operations fail."""
    pass


class ExecutionException(RIKException):
    """Raised when execution operations fail."""
    pass


class RollbackException(RIKException):
    """Raised when rollback operations fail."""
    pass


class FallbackException(RIKException):
    """Raised when fallback recovery strategies fail."""
    pass


class DatabaseException(MemoryException):
    """Raised when database operations fail."""
    pass


class ConsolidationException(MemoryException):
    """Raised when episode consolidation fails."""
    pass


class AnalogValidationException(ReasoningException):
    """Raised when analogy validation fails."""
    pass


class AbstractionException(ReasoningException):
    """Raised when abstraction creation fails."""
    pass


class ConcurrencyException(ExecutionException):
    """Raised when concurrent database operations conflict."""
    pass


class VisualizationException(RIKException):
    """Raised when architecture visualization fails."""
    pass


class FitnessEvaluationException(RIKException):
    """Raised when fitness evaluation fails."""
    pass
