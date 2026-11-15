"""Document & Knowledge Application Service.

Encapsulates publication summaries, topic consensus synthesis, terrestrial spin-offs,
and historic spaceflight incident analyses.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
from rag.summaries import load_summaries, filter_summaries
from insights.synthesis import synthesize_topic, get_available_topics
from insights.terrestrial import get_terrestrial_spinoffs, filter_spinoffs, get_spinoff_comparison_dataframe
from insights.historic_incidents import get_historic_incidents, get_incident_comparison_table

class DocumentService:
    """Service orchestrating technical documents and historical lessons."""

    @staticmethod
    def get_summaries() -> Dict[str, Dict[str, Any]]:
        """Retrieve executive summaries of harvested NASA STI papers."""
        return load_summaries()

    @staticmethod
    def search_summaries(
        summaries: Dict[str, Dict[str, Any]],
        query: str = "",
        sti_type: str = "All",
    ) -> List[Dict[str, Any]]:
        """Filter reports by query string and publication category."""
        return filter_summaries(summaries, query=query, sti_type=sti_type)

    @staticmethod
    def get_topic_synthesis(topic: str) -> Dict[str, Any]:
        """Synthesize verified findings and consensus across research papers."""
        return synthesize_topic(topic)

    @staticmethod
    def get_topics_list() -> List[str]:
        """Return all synthesis-supported fire safety topics."""
        return get_available_topics()

    @staticmethod
    def get_earth_spinoffs(category: str = None, query: str = None) -> List[Dict[str, Any]]:
        """Retrieve terrestrial fire safety spin-offs derived from space research."""
        return filter_spinoffs(category=category, query=query)

    @staticmethod
    def get_spinoff_comparison_table() -> pd.DataFrame:
        """Return side-by-side dataframe of space flight origins and commercial impact."""
        return get_spinoff_comparison_dataframe()

    @staticmethod
    def get_flight_incidents() -> List[Dict[str, Any]]:
        """Retrieve historical spacecraft fire emergency records."""
        return get_historic_incidents()

    @staticmethod
    def get_incidents_comparison_table() -> pd.DataFrame:
        """Return summary comparison matrix of historic spacecraft incidents."""
        return get_incident_comparison_table()

