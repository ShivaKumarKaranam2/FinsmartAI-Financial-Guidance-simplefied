"""
Budget Advice Generator Service.
Generates structured, actionable financial advice based on 50/30/20 rule and spending breakdown.
"""

from typing import Dict, List, Any
from app.core.llm_provider import call_llm
from app.core.logging import setup_logger

logger = setup_logger(__name__)


def generate_financial_advice(analysis: Dict[str, Any], expenses: List[Dict[str, Any]]) -> str:
    """
    Generate personalized financial advice using AI based on budget analysis.
    """
    income = analysis.get("income", 0)
    total_exp = analysis.get("total_expenses", 0)
    savings = analysis.get("savings", 0)
    savings_pct = analysis.get("savings_percentage", 0)
    breakdown = analysis.get("expense_breakdown_by_category", {})

    # Build expense details string
    expense_details = "\n".join([f"- {cat}: ₹{amt:,.0f}" for cat, amt in breakdown.items()])

    prompt = f"""You are a certified financial planner in India. Analyze this person's monthly budget and give SPECIFIC, ACTIONABLE advice.

BUDGET DATA:
- Monthly Income: ₹{income:,.0f}
- Total Expenses: ₹{total_exp:,.0f}
- Net Savings: ₹{savings:,.0f} ({savings_pct}% of income)

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
Show an ideal allocation of their ₹{income:,.0f} income using the 50/30/20 rule:
- Needs (50%): ₹{income * 0.5:,.0f} — rent, utilities, groceries
- Wants (30%): ₹{income * 0.3:,.0f} — dining, entertainment, travel
- Savings (20%): ₹{income * 0.2:,.0f} — investments, emergency fund

### 🎯 Investment Suggestions
Based on their savings capacity, suggest 2-3 specific investment options suitable for Indian investors (SIP, PPF, FD, etc.) with amounts.

Keep the response concise but data-driven. Use actual numbers from their budget."""

    try:
        advice = call_llm(prompt, max_tokens=1000)
        return advice
    except Exception as e:
        logger.error(f"Failed to generate budget advice: {e}")
        return (
            f"### 💰 Savings Assessment\n"
            f"Monthly Income: ₹{income:,.0f} | Expenses: ₹{total_exp:,.0f} | Savings: ₹{savings:,.0f} ({savings_pct}%).\n\n"
            f"### 📊 50/30/20 Target\n"
            f"- Needs: ₹{income * 0.5:,.0f}\n"
            f"- Wants: ₹{income * 0.3:,.0f}\n"
            f"- Savings: ₹{income * 0.2:,.0f}"
        )
