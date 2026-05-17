from .general_qa import answer_general_finance_question
from .tools import calculate_deterministic_emi
# Assuming these modules are in the parent directory (Fin_Personal_Assitant) 
# We need to make sure they are importable. 
# Ideally, we should move them into finance_bot or keep them in the parent and import them.
# For now, let's assume we will move the logic or keep the imports working.
# Actually, the user wants a clean backend. I should move the logic files into finance_bot or import them from there if they are reusable.
# Let's import them from the parent package for now, or better yet, move the files to finance_bot to make it self-contained.
# I will decide to move them to finance_bot to make it a standalone package.

import sys
import os

# quick hack to allow importing from parent directory if running as script, but we are making a package
# so we should use relative imports.

from expenses_categorizer import categorize_expenses
from savings_analysis import savings_analysis
from budget_recommendation import analyze_cash_flow_and_savings
from investment_advisor import generate_investment_guidance, investment_advisor_json
from model_loader import call_llm

def detect_user_intent(user_input: str) -> str:
    """
    Detects whether the user input is:
    - general_finance_question
    - personal_finance_data
    - unclear
    """
    # 1. Fast Keyword Check (General Questions)
    txt = user_input.lower()
    q_words = ["what is", "how", "explain", "benefit", "advantages", "disadvantage", "why", "is it better", "does it help", "difference", "calculate", "compute", "estimate"]
    
    # If it starts with a question word or specific verb, likely a question
    if any(txt.startswith(k) for k in q_words) or any(f" {k} " in f" {txt} " for k in q_words):
        return "general_finance_question"

    # 2. Fast Data Check (Financial Narratives)
    # If users mentions money/spending keywords AND numbers, it's likely data.
    data_keywords = ["income", "earn", "salary", "spent", "spend", "paid", "rupees", "rs.", "$", "expenses", "savings", "budget"]
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
    # Increased tokens to avoid cutoff, cleaned output
    response = call_llm(prompt, max_tokens=50, temperature=0.1).strip().lower()
    
    # Fallback cleanup
    if "general" in response: return "general_finance_question"
    if "personal" in response: return "personal_finance_data"
    
    return "unclear"

def fin_smart_process(user_input: str):
    """
    Refactored from fin_smart_router to return a dictionary object for the API.
    """
    intent = detect_user_intent(user_input)
    
    # Clean intent string just in case
    if "general_finance" in intent: intent = "general_finance_question"
    if "personal_finance" in intent: intent = "personal_finance_data"

    if intent == "general_finance_question":
        return {
            "type": "general_answer",
            "response": answer_general_finance_question(user_input)
        }

    elif intent == "personal_finance_data":
        # Step 1: Categorize
        categorized_expenses = categorize_expenses(user_input, "text")
        
        # Step 2: Savings Analysis
        savings_result = savings_analysis(categorized_expenses, user_input)
        
        # Step 3: Cash Flow
        cash_flow_summary = analyze_cash_flow_and_savings(savings_result)
        
        # Step 4: Advice
        investment_guidance = generate_investment_guidance(
            cash_flow_summary,
            financial_goals="wealth building",
            risk_tolerance="moderate"
        )
        
        # Step 5: Investment JSON for Charts (Optional, using rule based)
        inv_json = investment_advisor_json({"savings_amount": savings_result["savings"]})

        return {
            "type": "financial_analysis",
            "financial_summary": savings_result,
            "cash_flow_summary": cash_flow_summary,
            "investment_guidance": investment_guidance,
            "investment_json": inv_json
        }

    else:
        return {
            "type": "fallback",
            "response": "I wasn't sure if that was a financial question or data inputs. Please try rephrasing."
        }
