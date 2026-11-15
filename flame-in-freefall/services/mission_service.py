"""Mission Insights & Scenario Evaluation Application Service.

Encapsulates human exploration scenario evaluations, evidence coverage mapping,
ranking of published NASA findings, and risk card generation.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
from insights.scenarios import SCENARIOS, Scenario, evaluate
from insights.findings import load_findings, rank_findings
from insights.risk_cards import build_cards, STATES as RISK_STATES
from insights.brief import build_brief
from insights.si_brief import build_inputs as brief_inputs, generate_brief
from insights.coverage_map import coverage_figure, coverage_table, atmosphere_status, ppo2_gap, STATUS_TEXT
from domain.safety import evaluate_safety_officer_verdict
from domain.models import SafetyOfficerVerdict

class MissionService:
    """Service orchestrating mission environment risk assessment."""

    @staticmethod
    def get_standard_scenarios() -> Dict[str, Scenario]:
        """Return predefined human space exploration target environments."""
        return SCENARIOS

    @staticmethod
    def evaluate_scenario(
        scenario: Scenario,
        predictor_instance: Any,
        experiments_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Evaluate experimental coverage, predictions, and physical gaps."""
        return evaluate(scenario, predictor_instance, experiments_df)

    @staticmethod
    def rank_nasa_findings(
        findings: List[Dict[str, Any]],
        g: float,
        o2_pct: float,
        pressure_kpa: float,
        tags: tuple = (),
    ) -> List[Dict[str, Any]]:
        """Rank published research by gravity, atmosphere, and topic relevance."""
        return rank_findings(findings, g, o2_pct, pressure_kpa, tags)

    @staticmethod
    def get_safety_officer_assessment(
        eval_result: Dict[str, Any],
        scenario_name: str,
    ) -> SafetyOfficerVerdict:
        """Evaluate operational Go/No-Go flight safety limits."""
        return evaluate_safety_officer_verdict(eval_result, scenario_name)

    @staticmethod
    def build_risk_cards(
        eval_result: Dict[str, Any],
        ranked_findings: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Synthesize topic-by-topic risk state and cited evidence."""
        return build_cards(eval_result, ranked_findings)

    @staticmethod
    def compile_rule_brief(
        eval_result: Dict[str, Any],
        ranked_findings: List[Dict[str, Any]],
    ) -> str:
        """Compile deterministic fact-grounded mission safety brief."""
        return build_brief(eval_result, ranked_findings)

