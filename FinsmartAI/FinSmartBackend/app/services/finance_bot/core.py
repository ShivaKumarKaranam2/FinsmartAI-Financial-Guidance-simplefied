"""
Core Personal Finance Bot Pipeline.
Detects user intent (knowledge vs personal financial data) and orchestrates the full pipeline.
Follows Single Responsibility (SRP) and Open/Closed (OCP) principles.
"""

from typing import Dict, Any

from app.core.llm_provider import call_llm
from app.core.logging import setup_logger
from app.services.finance_bot.general_qa import answer_general_finance_question
from app.services.budget.expense_categorizer import categorize_expenses
from app.services.budget.savings_analyzer import savings_analysis
from app.services.budget.cash_flow_service import analyze_cash_flow_and_savings
from app.services.portfolio.advisor_rules import investment_advisor_json
from app.services.portfolio.ai_guidance import generate_investment_guidance

logger = setup_logger(__name__)


def detect_user_intent(user_input: str) -> str:
    """
    Detects whether the user input is:
    - general_finance_question
    - personal_finance_data
    - unclear
    """
    txt = user_input.lower()
    
    # 1. Fast Keyword Check (General Questions)
    q_words = [
        "what is", "how", "explain", "benefit", "advantages", "disadvantage",
        "why", "is it better", "does it help", "difference", "calculate",
        "compute", "estimate"
    ]
    if any(txt.startswith(k) for k in q_words) or any(f" {k} " in f" {txt} " for k in q_words):
        return "general_finance_question"

    # 2. Fast Data Check (Financial Narratives)
    data_keywords = [
        "income", "earn", "salary", "spent", "spend", "paid", "rupees", "rs.",
        "$", "expenses", "savings", "budget"
    ]
    has_keyword = any(k in txt for k in data_keywords)
    has_number = any(c.isdigit() for c in txt)
    
    if has_keyword and has_number:
        return "personal_finance_data"
    
    # 3. Robust LLM Check (Fallback)
    prompt = f"""
    Classify the following user input.
    
    Category 1: general_finance_question (asking for definition, explanation, knowledge)
    Category 2: personal_finance_data (user providing income, expense, numbers for analysis)
    
    User input: "{user_input}"
    
    Return ONLY "general_finance_question" or "personal_finance_data" or "unclear".
    """
    try:
        response = call_llm(prompt, max_tokens=50, temperature=0.1).strip().lower()
        if "general" in response:
            return "general_finance_question"
        if "personal" in response:
            return "personal_finance_data"
    except Exception as e:
        logger.warning(f"Intent detection fallback failed: {e}")
    
    return "unclear"


def fin_smart_process(user_input: str) -> Dict[str, Any]:
    """
    Processes user input and returns a structured dictionary object for the API.
    Handles general financial Q&A or end-to-end personal budget and investment analysis.
    """
    intent = detect_user_intent(user_input)
    
    if "general_finance" in intent or intent == "unclear":
        return {
            "type": "general_answer",
            "response": answer_general_finance_question(user_input)
        }

    elif intent == "personal_finance_data":
        # Step 1: Categorize expenses
        categorized_expenses = categorize_expenses(user_input, input_type="text")
        
        # Step 2: Savings analysis
        savings_result = savings_analysis(categorized_expenses, user_input)
        
        # Step 3: Cash flow summary
        cash_flow_summary = analyze_cash_flow_and_savings(savings_result)
        
        # Step 4: AI guidance
        investment_guidance = generate_investment_guidance(
            cash_flow_summary,
            financial_goals="wealth building",
            risk_tolerance="moderate"
        )
        
        # Step 5: Investment JSON for frontend charts
        inv_json = investment_advisor_json({"savings_amount": savings_result["savings"]})

        return {
            "type": "personal_finance_data",
            "financial_summary": savings_result,
            "cash_flow_summary": cash_flow_summary,
            "investment_guidance": investment_guidance,
            "investment_json": inv_json
        }

    return {
        "type": "fallback",
        "response": answer_general_finance_question(user_input)
    }
