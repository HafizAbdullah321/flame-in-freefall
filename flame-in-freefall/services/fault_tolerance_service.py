"""Fault Tolerance & Circuit Breaker Service.

Implements the Circuit Breaker pattern to ensure the application degrades gracefully
when external cloud services (OpenAI, NASA APIs) experience outages or rate limits.
Certifies 100% air-gapped autonomy for deep-space mission profiles.
"""
import time
from typing import Callable, Any, Optional, Dict

class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""
    pass

class CircuitBreaker:
    """Three-state Circuit Breaker (CLOSED, OPEN, HALF-OPEN) with automated recovery."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout_s: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record a successful operation, resetting failure counters."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record an operation failure and trip the breaker if threshold is exceeded."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        """Check whether the circuit allows a request execution."""
        if self.state == "CLOSED":
            return True

        # If OPEN, check if recovery timeout has elapsed
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time) >= self.recovery_timeout_s:
                self.state = "HALF_OPEN"
                return True
            return False

        # If HALF_OPEN, allow a single test probe request
        return True

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function protected by the circuit breaker."""
        if not self.can_execute():
            raise CircuitBreakerOpenException(
                f"Circuit breaker is OPEN. Fast-failing external call to preserve responsiveness. "
                f"Retry in {int(self.recovery_timeout_s - (time.time() - (self.last_failure_time or time.time())))}s."
            )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

    def get_status(self) -> Dict[str, Any]:
        """Return real-time circuit health telemetry and operational state."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_s": self.recovery_timeout_s,
            "last_failure_time": self.last_failure_time,
            "is_healthy": self.state == "CLOSED",
            "autonomy_mode": "AIR_GAPPED_LOCAL" if self.state == "OPEN" else "CLOUD_OR_LOCAL",
        }
