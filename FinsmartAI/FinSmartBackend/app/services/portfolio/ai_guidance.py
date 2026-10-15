"""
AI Investment Guidance Service.
Generates dynamic persona-driven investment recommendations using LLM.
"""

from typing import Dict, Any
from app.core.llm_provider import call_llm
from app.core.logging import setup_logger

logger = setup_logger(__name__)


def generate_investment_guidance(
    cash_flow_summary: Dict[str, Any],
    financial_goals: str = "wealth building and financial security",
    risk_tolerance: str = "moderate"
) -> str:
    """
    Generates budget, savings, and investment recommendations using LLM.
    
    Args:
        cash_flow_summary: Standardized cash flow summary dict
        financial_goals: String describing goals
        risk_tolerance: String describing risk profile
        
    Returns:
        Structured markdown investment guidance
    """
    total_income = cash_flow_summary.get("total_income", 0)
    total_expenses = cash_flow_summary.get("total_expenses", 0)
    net_savings = cash_flow_summary.get("net_savings", 0)
    savings_percentage = cash_flow_summary.get("savings_percentage", 0)
    expenses_by_category = cash_flow_summary.get("expenses_by_category", {})

    expenses_breakdown = "\n".join(
        [f"- {cat}: ₹{amt:,.0f}" for cat, amt in expenses_by_category.items()]
    )

    # Dynamic Persona Selection based on savings rate
    if savings_percentage < 20:
        persona = "You are a Strict Financial Coach. The user is struggling to save. Be direct, urgent, and focus on cutting costs."
        tone_instruction = "Use a warning tone. Prioritize the 50/30/20 rule. Highlight 'Needs' vs 'Wants'."
    elif savings_percentage < 50:
        persona = "You are a Balanced Financial Planner. The user is doing well but can optimize. Be encouraging but analytical."
        tone_instruction = "Focus on optimizing the portfolio. Suggest better asset allocation."
    else:
        persona = "You are a Wealth Manager for High Net Worth Individuals. The user is a super-saver. Focus on aggressive growth and wealth preservation."
        tone_instruction = "Use a professional, sophisticated tone. Suggest advanced diversification."

    prompt = f"""
    {persona}
    
    Task: {tone_instruction}

    ### Financial Overview
    - Monthly Income: ₹{total_income:,.0f}
    - Total Expenses: ₹{total_expenses:,.0f}
    - Net Savings: ₹{net_savings:,.0f}
    - Savings Rate: {savings_percentage}%

    ### Expense Breakdown
    {expenses_breakdown if expenses_breakdown else "General expenses"}

    ### User Guidelines
    - Financial Goal: {financial_goals}
    - Risk Tolerance: {risk_tolerance}

    ### Required Output Sections:
    1. **Budget Analysis**: (Critique their spending habits based on your persona)
    2. **Savings Verdict**: (Is it enough? Be honest)
    3. **Investment Strategy**: (Specific to their savings tier)
    4. **Emergency Planning**: (Mandatory check)
    5. **Final Verdict**: (Summarize their health in one sentence)

    IMPORTANT RULES:
    1. Do NOT invent a "User Input" section.
    2. Do NOT hallucinate personal details.
    3. Strictly follow your assigned Persona Tone.
    """

    try:
        return call_llm(prompt, max_tokens=1200)
    except Exception as e:
        logger.error(f"Failed to generate investment guidance: {e}")
        return f"Unable to generate AI guidance at this time: {str(e)}"
