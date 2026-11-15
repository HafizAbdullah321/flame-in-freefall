"""Lightweight Service Container & Dependency Injection Layer.

Encapsulates the instantiation and wiring of domain services and adapters,
enforcing Ports & Adapters separation and enabling mock injection for tests.
"""
from pathlib import Path
from typing import Optional, Dict, Any

from services.audit_service import AuditService
from services.security_service import SecurityService
from services.fault_tolerance_service import CircuitBreaker
from services.catalog_service import CatalogService
from services.document_service import DocumentService
from services.ports import AuditPort, SecurityPort, FaultTolerancePort

class ServiceContainer:
    """Centralized registry for application services and infrastructure adapters."""
    _circuit_breaker: Optional[CircuitBreaker] = None

    @classmethod
    def get_circuit_breaker(cls, failure_threshold: int = 3, recovery_timeout_s: float = 30.0) -> CircuitBreaker:
        """Return the shared fault-tolerance circuit breaker singleton."""
        if cls._circuit_breaker is None:
            cls._circuit_breaker = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout_s=recovery_timeout_s
            )
        return cls._circuit_breaker

    @classmethod
    def get_security_service(cls) -> type:
        """Return the security and sanitization service."""
        return SecurityService

    @classmethod
    def get_audit_service(cls) -> type:
        """Return the cryptographic audit and provenance service."""
        return AuditService

    @classmethod
    def get_catalog_service(cls) -> type:
        """Return the PSI catalog aggregation service."""
        return CatalogService

    @classmethod
    def get_document_service(cls) -> type:
        """Return the document corpus and synthesis service."""
        return DocumentService

    @classmethod
    def get_system_provenance(cls, root_dir: Path) -> Dict[str, Any]:
        """Convenience method for retrieving verified SHA-256 provenance."""
        return cls.get_audit_service().get_provenance_report(root_dir)

    @classmethod
    def reset(cls) -> None:
        """Reset singletons (primarily for unit testing isolation)."""
        cls._circuit_breaker = None

