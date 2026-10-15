"""
Budget and Expenses Analysis Router.
Prefix: /api/budget
"""

import logging
from fastapi import APIRouter, HTTPException

from app.api.schemas.budget import BudgetAnalysisRequest, BudgetAnalysisResponse
from app.services.budget.expense_categorizer import categorize_expenses
from app.services.budget.savings_analyzer import savings_analysis
from app.services.budget.advice_generator import generate_financial_advice

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=BudgetAnalysisResponse, summary="Analyze budget and expenses")
async def analyze_budget(request: BudgetAnalysisRequest):
    """
    Analyzes user income and expenses, computes savings, and generates personalized AI financial advice.
    """
    try:
        # 1. Extract and categorize expenses
        expenses = categorize_expenses(request.expenses_text, input_type="text")
        
        # 2. Extract income and compute savings
        analysis_result = savings_analysis(expenses, request.income_text)
        
        # 3. Generate AI financial advice
        advice = generate_financial_advice(analysis_result, expenses)
        
        return BudgetAnalysisResponse(
            expenses=expenses,
            analysis=analysis_result,
            advice=advice
        )
    except Exception as e:
        logger.error(f"Budget analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Budget analysis failed: {str(e)}")
