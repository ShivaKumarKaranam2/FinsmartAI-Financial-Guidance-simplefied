"""
Personal Finance Assistant domain package.
Exports intent detector, deterministic calculators, QA engine, and main processor.
"""

from app.services.finance_bot.core import detect_user_intent, fin_smart_process
from app.services.finance_bot.general_qa import answer_general_finance_question
from app.services.finance_bot.calculators import calculate_deterministic_emi

__all__ = [
    "detect_user_intent",
    "fin_smart_process",
    "answer_general_finance_question",
    "calculate_deterministic_emi",
]
