import json
from model_loader import call_llm

def extract_income_prompt(text):
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
    prompt = extract_income_prompt(text)
    response_str = call_llm(prompt) # This returns a JSON string
    
    try:
        # Find JSON block
        start = response_str.find('{')
        end = response_str.rfind('}') + 1
        if start != -1 and end != -1:
            clean_json = response_str[start:end]
            response_dict = json.loads(clean_json)
        else:
             # Fallback: try whole string
             response_dict = json.loads(response_str)
             
    except json.JSONDecodeError:
        # If model fails to give JSON, fallback to assumption logic or error
        # In notebook it raises error, but for app robustness we might default to 0
        print(f"DEBUG: Failed to parse income JSON. Raw: {response_str}")
        return 0 

    income_value = response_dict.get("income")
    if income_value is None:
        return 0 # Default to 0 instead of raising error to keep app running

    return int(income_value)

def compute_expense_summary(categorized_expenses: list) -> dict:
    total_expense = 0
    category_wise = {}

    for txn in categorized_expenses:
        amt = txn["amount"]
        cat = txn["category"]

        total_expense += amt
        category_wise[cat] = category_wise.get(cat, 0) + amt

    return {
        "total_expense": total_expense,
        "category_breakdown": category_wise
    }

def savings_analysis(categorized_expenses: list, income_text: str) -> dict:
    # 1. Extract income using LLM
    income = extract_income_from_text(income_text)

    # 2. Compute expenses
    expense_summary = compute_expense_summary(categorized_expenses)

    total_expense = expense_summary["total_expense"]
    
    # Logic: Savings = Income - Expenses
    savings = income - total_expense
    
    # Avoid div by zero
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
