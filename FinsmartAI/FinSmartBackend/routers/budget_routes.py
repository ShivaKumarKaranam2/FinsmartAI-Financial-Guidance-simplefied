from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from expenses_categorizer import categorize_expenses
from savings_analysis import savings_analysis
from model_loader import call_llm

router = APIRouter()
logger = logging.getLogger(__name__)

class BudgetAnalysisRequest(BaseModel):
    income_text: str
    expenses_text: str


def generate_financial_advice(analysis: dict, expenses: list) -> str:
    """Generate personalized financial advice using AI based on the budget analysis."""
    
    income = analysis.get("income", 0)
    total_exp = analysis.get("total_expenses", 0)
    savings = analysis.get("savings", 0)
    savings_pct = analysis.get("savings_percentage", 0)
    breakdown = analysis.get("expense_breakdown_by_category", {})
    
    # Build expense details string
    expense_details = "\n".join([f"- {cat}: ₹{amt:,}" for cat, amt in breakdown.items()])
    
    prompt = f"""You are a certified financial planner in India. Analyze this person's monthly budget and give SPECIFIC, ACTIONABLE advice.

BUDGET DATA:
- Monthly Income: ₹{income:,}
- Total Expenses: ₹{total_exp:,}
- Net Savings: ₹{savings:,} ({savings_pct}% of income)

EXPENSE BREAKDOWN:
{expense_details}

Provide a structured response with these sections (use markdown formatting):

### 💰 Savings Assessment
Rate their savings (Excellent >30%, Good 20-30%, Average 10-20%, Poor <10%). Be specific about how they compare to the recommended 50/30/20 rule.

### ⚠️ Spending Alerts
Identify 2-3 categories where they are overspending relative to their income. Give specific rupee amounts they should target.

### 📋 Actionable Tips
Give 4-5 personalized, practical tips to improve their finances. Each tip should mention specific amounts.

### 📊 Recommended Monthly Budget
Show an ideal allocation of their ₹{income:,} income using the 50/30/20 rule:
- Needs (50%): ₹X — rent, utilities, groceries
- Wants (30%): ₹X — dining, entertainment, travel
- Savings (20%): ₹X — investments, emergency fund

### 🎯 Investment Suggestions
Based on their savings capacity, suggest 2-3 specific investment options suitable for Indian investors (SIP, PPF, FD, etc.) with amounts.

Keep the response concise but data-driven. Use actual numbers from their budget."""

    try:
        advice = call_llm(prompt, max_tokens=1000)
        return advice
    except Exception as e:
        logger.error(f"Failed to generate advice: {e}")
        return ""


@router.post("/analyze")
async def analyze_budget(request: BudgetAnalysisRequest):
    try:
        # 1. Extract and categorize expenses
        expenses = categorize_expenses(request.expenses_text, input_type="text")
        
        # 2. Extract income and compute savings
        analysis_result = savings_analysis(expenses, request.income_text)
        
        # 3. Generate AI financial advice
        advice = generate_financial_advice(analysis_result, expenses)
        
        return {
            "expenses": expenses,
            "analysis": analysis_result,
            "advice": advice
        }
    except Exception as e:
        logger.error(f"Budget analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
