"""Catalog Application Service.

Encapsulates all use-cases relating to the PSI microgravity experiment catalog:
filtering, comparative analysis, apparatus deep dives, and evidence tabulation.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
from insights.catalog import (
    load_catalog,
    filter_catalog,
    compare as compare_entries,
    evidence_matrix,
    gravity_class as cat_gravity,
    TYPES as CAT_TYPES,
    STATUSES as CAT_STATUSES,
    GEOMETRY_KEYWORDS,
    FUEL_CATEGORIES,
    SENSOR_CATEGORIES,
    _rng,
)
from domain.models import CatalogFilterCriteria

class CatalogService:
    """Application service for querying and inspecting microgravity experiments."""

    @staticmethod
    def get_all_entries() -> List[Dict[str, Any]]:
        """Retrieve all catalog records."""
        return load_catalog()

    @staticmethod
    def filter_experiments(
        criteria: CatalogFilterCriteria,
        rows: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Filter investigations based on multi-parameter criteria."""
        if rows is None:
            rows = load_catalog()
        return filter_catalog(
            rows,
            types=criteria.types or None,
            gravity=criteria.gravity or None,
            status=criteria.status or None,
            text=criteria.text,
            verified_only=criteria.verified_only,
            geometry=criteria.geometry or None,
            fuel_cat=criteria.fuel_cat or None,
            sensor_cat=criteria.sensor_cat or None,
        )

    @staticmethod
    def compare_investigations(
        ids: List[str],
        rows: Optional[List[Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """Generate side-by-side comparison table for selected investigations."""
        if rows is None:
            rows = load_catalog()
        return compare_entries(rows, ids)

    @staticmethod
    def get_evidence_matrix_dataframe(
        rows: Optional[List[Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """Generate gravity x status evidence count matrix."""
        if rows is None:
            rows = load_catalog()
        return evidence_matrix(rows)

