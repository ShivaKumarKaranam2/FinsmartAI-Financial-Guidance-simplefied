"""
Cash Flow Service.
Formats and standardizes financial cash flow summaries for downstream advisors.
"""

from typing import Dict, Any


def analyze_cash_flow_and_savings(financial_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardizes savings analysis output into cash flow summary.

    Args:
        financial_summary (dict): Output from savings_analysis()

    Returns:
        dict: Standardized cash flow summary dictionary
    """
    total_income = financial_summary.get("income", 0)
    total_expenses = financial_summary.get("total_expenses", 0)
    expenses_by_category = financial_summary.get("expense_breakdown_by_category", {})
    net_savings = financial_summary.get("savings", 0)
    savings_percentage = financial_summary.get("savings_percentage", 0)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "expenses_by_category": expenses_by_category,
        "net_savings": net_savings,
        "savings_percentage": savings_percentage
    }
