"""
Savings Analyzer Service.
Computes total expenses, breakdowns by category, extracts income, and calculates net savings.
"""

import json
from typing import List, Dict, Any
from app.core.llm_provider import call_llm
from app.core.logging import setup_logger

logger = setup_logger(__name__)


def extract_income_prompt(text: str) -> str:
    """Constructs prompt to extract total monthly income."""
    return f"""
    You are a financial information extractor.

    Extract ONLY the total monthly income mentioned in the text.
    Return output strictly in JSON format.

    Rules:
    - If income is mentioned, extract the numeric value as an integer.
    - Ignore expenses.
    - If no income is found, return null.

    Text:
    {text}

    Output format:
    {{"income": number_or_null}}
    """


def extract_income_from_text(text: str) -> int:
    """Extracts monthly income integer from natural language text."""
    if not text or not text.strip():
        return 0

    prompt = extract_income_prompt(text)
    try:
        response_str = call_llm(prompt, max_tokens=150, temperature=0.1)
        start = response_str.find('{')
        end = response_str.rfind('}') + 1
        if start != -1 and end != -1:
            clean_json = response_str[start:end]
            response_dict = json.loads(clean_json)
        else:
            response_dict = json.loads(response_str)

        income_val = response_dict.get("income")
        if income_val is not None:
            return int(float(income_val))
    except Exception as e:
        logger.warning(f"Could not parse income from text via LLM: {e}")

    # Fallback heuristic: check for numbers near "income", "salary", "earn"
    import re
    matches = re.findall(r"(?:earn|salary|income|take-home)[\s:]*(?:rs\.?|inr|₹)?\s*(\d[\d,]*)", text, re.IGNORECASE)
    if matches:
        try:
            return int(matches[0].replace(",", ""))
        except ValueError:
            pass

    return 0


def compute_expense_summary(categorized_expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes total expense and category breakdown from transactions."""
    total_expense = 0.0
    category_wise = {}

    for txn in categorized_expenses:
        amt = float(txn.get("amount", 0.0))
        cat = str(txn.get("category", "Other"))

        total_expense += amt
        category_wise[cat] = round(category_wise.get(cat, 0.0) + amt, 2)

    return {
        "total_expense": round(total_expense, 2),
        "category_breakdown": category_wise
    }


def savings_analysis(categorized_expenses: List[Dict[str, Any]], income_text: str) -> Dict[str, Any]:
    """
    Main savings analysis function.
    
    Args:
        categorized_expenses: List of categorized expense dictionaries
        income_text: Free-text string containing income
        
    Returns:
        Dict with income, total_expenses, savings, savings_percentage, and breakdown
    """
    income = extract_income_from_text(income_text)
    expense_summary = compute_expense_summary(categorized_expenses)
    total_expense = expense_summary["total_expense"]

    savings = round(income - total_expense, 2)

    if income > 0:
        savings_rate = round((savings / income) * 100, 2)
    else:
        savings_rate = 0.0

    return {
        "income": income,
        "total_expenses": total_expense,
        "savings": savings,
        "savings_percentage": savings_rate,
        "expense_breakdown_by_category": expense_summary["category_breakdown"]
    }
