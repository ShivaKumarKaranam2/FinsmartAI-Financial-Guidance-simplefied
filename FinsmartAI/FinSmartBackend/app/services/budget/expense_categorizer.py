"""
Expense Categorizer Service.
Handles extraction of expense items and categories from natural language text and files.
Adheres to Single Responsibility Principle (SRP).
"""

import json
from typing import List, Dict, Any
from app.core.llm_provider import call_llm
from app.core.logging import setup_logger

logger = setup_logger(__name__)


def extract_expenses_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extracts expenses with categories from text in a single structured LLM call.
    Returns list of dicts: [{"description": str, "amount": float, "category": str}]
    """
    if not text or not text.strip():
        return []

    prompt = f"""
    You are an advanced financial extractor.
    Extract all expenses from the text.
    For each expense, assign a category from: [Food, Rent, Travel, Shopping, Utilities, Subscription, Healthcare, Education, Other].

    If no expenses are found, return an empty array: [].
    Do NOT copy the example output.

    Text:
    "{text}"

    Example output:
    [
        {{ "description": "movie ticket", "amount": 300, "category": "Other" }}
    ]
    """

    try:
        response = call_llm(prompt, max_tokens=600, temperature=0.1)
        start = response.find('[')
        end = response.rfind(']') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                # Ensure each item has expected types
                results = []
                for item in parsed:
                    if isinstance(item, dict) and "amount" in item:
                        try:
                            results.append({
                                "description": str(item.get("description", "Expense")),
                                "amount": float(item.get("amount", 0)),
                                "category": str(item.get("category", "Other"))
                            })
                        except (ValueError, TypeError):
                            continue
                return results
    except Exception as e:
        logger.warning(f"Failed to extract expenses from text via LLM: {e}")

    return []


def extract_expenses_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads CSV or Excel file and returns transaction list.
    """
    import os
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    try:
        import pandas as pd
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        transactions = []
        for _, row in df.iterrows():
            desc = str(row.get("description", row.get("desc", "Expense")))
            amt = float(row.get("amount", row.get("amt", 0.0)))
            cat = str(row.get("category", "Other"))
            transactions.append({
                "description": desc,
                "amount": amt,
                "category": cat
            })
        return transactions
    except Exception as e:
        logger.error(f"Failed to read expenses file {file_path}: {e}")
        return []


def categorize_expenses(input_data: Any, input_type: str = "text") -> List[Dict[str, Any]]:
    """
    Extracts and categorizes expenses from either 'text' or 'file'.
    
    Args:
        input_data: String text or file path
        input_type: 'text' or 'file'
        
    Returns:
        List of categorized expense dictionaries
    """
    if input_type == "text":
        return extract_expenses_from_text(str(input_data))
    elif input_type == "file":
        return extract_expenses_from_file(str(input_data))
    else:
        raise ValueError(f"Invalid input type '{input_type}'. Must be 'text' or 'file'.")
