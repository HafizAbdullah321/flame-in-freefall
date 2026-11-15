"""Unit tests for the Application Services layer.

Validates catalog filtering, simulation predictions, mission evaluations,
and document searches through clean service interfaces.
"""
from pathlib import Path
import os, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from domain.models import CatalogFilterCriteria
from services.catalog_service import CatalogService
from services.simulation_service import SimulationService
from services.mission_service import MissionService
from services.document_service import DocumentService
from services.container import ServiceContainer
from services.ports import AuditPort, SecurityPort, FaultTolerancePort
from services.audit_service import AuditService
from services.security_service import SecurityService
from services.fault_tolerance_service import CircuitBreaker

def test_catalog_service():
    all_entries = CatalogService.get_all_entries()
    assert len(all_entries) >= 14

    criteria = CatalogFilterCriteria(
        geometry=["Flat sheet / sample"],
        fuel_cat=["Solid polymers (PMMA, plastics)"],
    )
    hits = CatalogService.filter_experiments(criteria, all_entries)
    assert len(hits) >= 1
    assert any("BASS" in h["name"] for h in hits)

    comp = CatalogService.compare_investigations(["E01", "E02"], all_entries)
    assert not comp.empty
    assert len(comp.columns) == 2

    matrix = CatalogService.get_evidence_matrix_dataframe(all_entries)
    assert not matrix.empty

def test_document_service():
    summaries = DocumentService.get_summaries()
    assert len(summaries) > 0

    hits = DocumentService.search_summaries(summaries, query="flame")
    assert len(hits) > 0

    topics = DocumentService.get_topics_list()
    assert "flame-spread" in topics

    syn = DocumentService.get_topic_synthesis("flame-spread")
    assert "consensus" in syn

    spinoffs = DocumentService.get_earth_spinoffs()
    assert len(spinoffs) >= 4

    incidents = DocumentService.get_flight_incidents()
    assert len(incidents) >= 4

def test_simulation_service():
    model_path = ROOT / "backend/artifacts/ff_model.joblib"
    if model_path.exists():
        sim = SimulationService(model_path)
        lo, hi = sim.get_safe_o2_range("PMMA", 0.0)
        assert lo < hi

        pred = sim.predict_spread_rate(28.0, 1.0, "PMMA", 0.0)
        assert pred["status"] == "IN"
        assert pred["rate"] > 0

        phys = sim.compute_physics_diagnostics(28.0, 100.0, 97.0, pred["rate"])
        assert phys.peclet_number > 0

def test_mission_service():
    scenarios = MissionService.get_standard_scenarios()
    assert "lunar" in scenarios
    assert "iss" in scenarios

def test_ports_and_container():
    # 1. Port Protocol adherence
    assert issubclass(AuditService, AuditPort)
    assert issubclass(SecurityService, SecurityPort)
    cb = CircuitBreaker()
    assert isinstance(cb, FaultTolerancePort)

    # 2. Service Container resolution
    cb_singleton = ServiceContainer.get_circuit_breaker()
    assert isinstance(cb_singleton, CircuitBreaker)
    assert ServiceContainer.get_security_service() is SecurityService
    assert ServiceContainer.get_audit_service() is AuditService
    assert ServiceContainer.get_catalog_service() is CatalogService
    assert ServiceContainer.get_document_service() is DocumentService

    prov = ServiceContainer.get_system_provenance(ROOT)
    assert prov["status"] == "VERIFIED_INTEGRITY"
    assert "model_sha256" in prov

if __name__ == "__main__":
    test_catalog_service()
    test_document_service()
    test_simulation_service()
    test_mission_service()
    test_ports_and_container()
    print("APPLICATION SERVICES LAYER TESTS PASSED")
