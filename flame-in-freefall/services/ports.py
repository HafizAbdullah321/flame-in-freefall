"""Ports (Interfaces) for the Hexagonal / Clean Architecture.

Defines the boundary protocols for primary and secondary adapters:
1. PredictorPort: Physical combustion ML regression and safe envelope bounds.
2. RetrieverPort: Dense vector semantic search and mathematical refusal gating.
3. AuditPort: Cryptographic SHA-256 provenance calculation and artifact tracking.
4. SecurityPort: Input sanitization, indirect prompt injection defense, and physical bounding.
5. FaultTolerancePort: Circuit breaker execution, fast-failing, and telemetry reporting.
"""
from typing import Protocol, runtime_checkable, Tuple, List, Dict, Any, Optional, Callable

@runtime_checkable
class PredictorPort(Protocol):
    """Outbound port for physical ML flame spread rate prediction."""
    def predict(self, o2_pct: float, fuel_coverage: float) -> Dict[str, Any]:
        """Predict flame front spread rate and conformal 90% bounds."""
        ...

    def safe_o2_range(self, fuel: str, g_level: float, f_star: float) -> Tuple[float, float]:
        """Return experimental tested oxygen boundaries."""
        ...

    def conditions_for(self, fuel: str, g_level: float, o2_pct: float) -> Tuple[float, float]:
        """Return derived ambient pressure (kPa) and opposed flow velocity (mm/s)."""
        ...

@runtime_checkable
class RetrieverPort(Protocol):
    """Outbound port for dense vector retrieval and calibrated refusal gating."""
    tau: float

    def answerable(self, query: str, top_k: int = 5) -> Tuple[bool, List[Dict[str, Any]]]:
        """Evaluate if query is answerable against calibrated threshold tau."""
        ...

    def load_tau(self, tau_path: Any) -> None:
        """Load calibrated refusal threshold."""
        ...

@runtime_checkable
class AuditPort(Protocol):
    """Inbound/Outbound port for cryptographic integrity audit and provenance."""
    @classmethod
    def get_provenance_report(cls, root_dir: Any) -> Dict[str, Any]:
        """Compute full SHA-256 provenance hashes across models, datasets, and indexes."""
        ...

@runtime_checkable
class SecurityPort(Protocol):
    """Inbound port for input guardrails, sanitization, and aerospace hazard defense."""
    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Strip dangerous HTML tags and zero-width characters."""
        ...

    @classmethod
    def detect_prompt_injection(cls, text: str) -> Tuple[bool, Optional[str]]:
        """Detect prompt injection patterns, indirect delimiters, or aerospace hazards."""
        ...

    @classmethod
    def validate_scenario_bounds(cls, pressure_kpa: float, o2_pct: float, gravity_g: float) -> Tuple[bool, List[str]]:
        """Validate physical parameters against aerospace atmospheric bounds."""
        ...

@runtime_checkable
class FaultTolerancePort(Protocol):
    """Inbound port for circuit breaking and flight telemetry reporting."""
    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute callable protected by failure threshold and fast-fail state."""
        ...

    def get_status(self) -> Dict[str, Any]:
        """Return health, state, and air-gapped autonomy mode."""
        ...

