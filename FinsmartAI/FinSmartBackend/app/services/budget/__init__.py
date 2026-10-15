"""
Budget Domain Package.
Contains expense categorizer, savings analyzer, cash flow, and advice generators.
"""

from app.services.budget.expense_categorizer import (
    extract_expenses_from_text,
    extract_expenses_from_file,
    categorize_expenses,
)
from app.services.budget.savings_analyzer import (
    extract_income_prompt,
    extract_income_from_text,
    compute_expense_summary,
    savings_analysis,
)
from app.services.budget.cash_flow_service import analyze_cash_flow_and_savings
from app.services.budget.advice_generator import generate_financial_advice

__all__ = [
    "extract_expenses_from_text",
    "extract_expenses_from_file",
    "categorize_expenses",
    "extract_income_prompt",
    "extract_income_from_text",
    "compute_expense_summary",
    "savings_analysis",
    "analyze_cash_flow_and_savings",
    "generate_financial_advice",
]
