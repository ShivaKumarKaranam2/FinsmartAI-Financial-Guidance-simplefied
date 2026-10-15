"""Unit tests for Budget and Cash Flow services."""

from app.services.budget.savings_analyzer import compute_expense_summary
from app.services.budget.cash_flow_service import analyze_cash_flow_and_savings


def test_compute_expense_summary():
    expenses = [
        {"description": "Rent", "amount": 20000, "category": "Rent"},
        {"description": "Groceries", "amount": 8000, "category": "Food"},
        {"description": "Dining out", "amount": 4000, "category": "Food"},
        {"description": "Electricity", "amount": 2500, "category": "Utilities"}
    ]
    summary = compute_expense_summary(expenses)
    assert summary["total_expense"] == 34500
    assert summary["category_breakdown"]["Food"] == 12000
    assert summary["category_breakdown"]["Rent"] == 20000
    assert summary["category_breakdown"]["Utilities"] == 2500


def test_analyze_cash_flow_and_savings():
    financial_summary = {
        "income": 80000,
        "total_expenses": 34500,
        "savings": 45500,
        "savings_percentage": 56.88,
        "expense_breakdown_by_category": {
            "Rent": 20000,
            "Food": 12000,
            "Utilities": 2500
        }
    }
    cash_flow = analyze_cash_flow_and_savings(financial_summary)
    assert cash_flow["total_income"] == 80000
    assert cash_flow["total_expenses"] == 34500
    assert cash_flow["net_savings"] == 45500
    assert cash_flow["savings_percentage"] == 56.88
    assert len(cash_flow["expenses_by_category"]) == 3


if __name__ == "__main__":
    test_compute_expense_summary()
    test_analyze_cash_flow_and_savings()
    print("✅ All budget and cash flow tests passed!")
