"""
Portfolio and Investment Advisory domain package.
Exports rules-based advisor, AI guidance generator, and CrewService.
"""

from app.services.portfolio.advisor_rules import investment_advisor_json
from app.services.portfolio.ai_guidance import generate_investment_guidance
from app.services.portfolio.crew_service import CrewService, _extract_chart_data, _normalize_markdown_tables

__all__ = [
    "investment_advisor_json",
    "generate_investment_guidance",
    "CrewService",
    "_extract_chart_data",
    "_normalize_markdown_tables",
]
