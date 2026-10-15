"""Budget and cash flow analysis request and response schemas."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BudgetAnalysisRequest(BaseModel):
    """Request model for budget and expenses analysis."""
    income_text: str = Field(..., description="Text containing monthly income details")
    expenses_text: str = Field(..., description="Text containing expenses breakdown")

    class Config:
        json_schema_extra = {
            "example": {
                "income_text": "I earn 80000 rupees a month",
                "expenses_text": "Rent: 20000, Groceries: 12000, Dining: 5000, Electricity: 3000"
            }
        }


class ExpenseItem(BaseModel):
    """Individual categorized expense item."""
    description: str
    amount: float
    category: str


class SavingsSummary(BaseModel):
    """Detailed summary of savings and expenses."""
    income: float
    total_expenses: float
    savings: float
    savings_percentage: float
    expense_breakdown_by_category: Dict[str, float]


class BudgetAnalysisResponse(BaseModel):
    """Response containing categorized expenses, numerical analysis, and AI advice."""
    expenses: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    advice: str
