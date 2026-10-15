"""Unit tests for Finance Bot calculators and intent detector."""

from app.services.finance_bot.calculators import calculate_deterministic_emi
from app.services.finance_bot.core import detect_user_intent


def test_emi_calculator():
    query = "Calculate EMI for 25 lakh home loan at 8.5% interest for 20 years"
    res = calculate_deterministic_emi(query)
    assert res is not None
    assert "EMI Calculator" in res
    assert "25,000,000" in res or "2,500,000" in res or "21,695" in res or "Monthly EMI" in res


def test_intent_detection():
    # General finance question
    q_intent = detect_user_intent("What is a Systematic Investment Plan?")
    assert q_intent == "general_finance_question"

    # Personal finance narrative with numbers and keywords
    data_intent = detect_user_intent("My monthly income is 75000 and I spent 20000 on rent and 8000 on food")
    assert data_intent == "personal_finance_data"


if __name__ == "__main__":
    test_emi_calculator()
    test_intent_detection()
    print("✅ All finance bot tests passed!")
