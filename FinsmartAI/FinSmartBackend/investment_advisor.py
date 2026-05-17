from model_loader import call_llm

def investment_advisor_json(input_data: dict) -> dict:
    """
    FinSmart AI - Investment Recommendation Engine (JSON-based)

    Input:
    {
        "savings_amount": <int or float>
    }

    Output:
    Structured investment recommendations (JSON)
    """

    # ---------- Input Validation ----------
    if "savings_amount" not in input_data:
        return {
            "error": "Missing required field: savings_amount"
        }

    try:
        savings = float(input_data["savings_amount"])
    except (TypeError, ValueError):
        return {
            "error": "Invalid savings_amount. Must be a number."
        }

    if savings <= 0:
        return {
            "error": "Savings amount must be greater than zero."
        }

    # ---------- Base Response Structure ----------
    response = {
        "input_savings": savings,
        "investment_strategy": "",
        "recommended_allocation": [],
        "advisor_notes": []
    }

    # ---------- Recommendation Logic ----------

    # Tier 1: Very Low Savings
    if savings < 10000:
        response["investment_strategy"] = "Capital Protection & Liquidity"
        response["recommended_allocation"] = [
            {
                "instrument": "Savings Account",
                "allocation_percent": 100,
                "risk_level": "Low",
                "reason": "Ensure emergency liquidity before investing"
            }
        ]
        response["advisor_notes"].append(
            "Build an emergency fund before moving to market-linked investments."
        )

    # Tier 2: Low Savings
    elif 10000 <= savings < 50000:
        response["investment_strategy"] = "Low Risk with Market Introduction"
        response["recommended_allocation"] = [
            {
                "instrument": "Fixed Deposit / Recurring Deposit",
                "allocation_percent": 60,
                "risk_level": "Low",
                "reason": "Capital safety with predictable returns"
            },
            {
                "instrument": "Liquid Mutual Fund",
                "allocation_percent": 20,
                "risk_level": "Low",
                "reason": "Better liquidity than FD"
            },
            {
                "instrument": "Nifty 50 Index Fund",
                "allocation_percent": 20,
                "risk_level": "Medium",
                "reason": "Initial exposure to equity markets"
            }
        ]
        response["advisor_notes"].append(
            "Start equity exposure slowly to understand market behavior."
        )

    # Tier 3: Medium Savings
    elif 50000 <= savings < 200000:
        response["investment_strategy"] = "Balanced Growth & Stability"
        response["recommended_allocation"] = [
            {
                "instrument": "PPF / Bank FD",
                "allocation_percent": 30,
                "risk_level": "Low",
                "reason": "Long-term capital protection"
            },
            {
                "instrument": "Index Fund (Nifty / Sensex)",
                "allocation_percent": 30,
                "risk_level": "Medium",
                "reason": "Market-linked growth with diversification"
            },
            {
                "instrument": "Large Cap Equity Mutual Fund",
                "allocation_percent": 20,
                "risk_level": "Medium",
                "reason": "Stable companies with growth potential"
            },
            {
                "instrument": "Gold ETF / Sovereign Gold Bond",
                "allocation_percent": 20,
                "risk_level": "Medium",
                "reason": "Hedge against inflation and volatility"
            }
        ]
        response["advisor_notes"].append(
            "Balanced portfolio reduces risk while improving long-term returns."
        )

    # Tier 4: High Savings
    else:
        response["investment_strategy"] = "Diversified Wealth Creation"
        response["recommended_allocation"] = [
            {
                "instrument": "PPF / Government Bonds",
                "allocation_percent": 20,
                "risk_level": "Low",
                "reason": "Foundation of capital safety"
            },
            {
                "instrument": "Index Funds",
                "allocation_percent": 25,
                "risk_level": "Medium",
                "reason": "Low-cost market participation"
            },
            {
                "instrument": "Mid & Large Cap Equity Funds",
                "allocation_percent": 25,
                "risk_level": "High",
                "reason": "Higher growth potential"
            },
            {
                "instrument": "REITs / InvITs",
                "allocation_percent": 15,
                "risk_level": "Medium",
                "reason": "Income-generating real assets"
            },
            {
                "instrument": "Gold / SGB",
                "allocation_percent": 10,
                "risk_level": "Medium",
                "reason": "Portfolio hedge"
            },
            {
                "instrument": "High-Risk Bucket (Direct Stocks / Crypto)",
                "allocation_percent": 5,
                "risk_level": "High",
                "reason": "Optional high-growth exposure"
            }
        ]
        response["advisor_notes"].append(
            "High-risk exposure is capped to protect overall portfolio."
        )

    # ---------- Final Notes ----------
    response["advisor_notes"].append(
        "Review allocation annually or after major life events."
    )

    return response

def generate_investment_guidance(
    cash_flow_summary: dict,
    financial_goals: str = "wealth building and financial security",
    risk_tolerance: str = "moderate"
) -> str:
    """
    Generates budget, savings, and investment recommendations using LLM.
    """

    total_income = cash_flow_summary["total_income"]
    total_expenses = cash_flow_summary["total_expenses"]
    net_savings = cash_flow_summary["net_savings"]
    savings_percentage = cash_flow_summary["savings_percentage"]
    expenses_by_category = cash_flow_summary["expenses_by_category"]

    expenses_breakdown = "\n".join(
        [f"- {cat}: ₹{amt}" for cat, amt in expenses_by_category.items()]
    )

    # Dynamic Persona Selection
    if savings_percentage < 20:
        persona = "You are a Strict Financial Coach. The user is struggling to save. Be direct, urgent, and focus on cutting costs."
        tone_instruction = "Use a warning tone. Prioritize the 50/30/20 rule. highlight 'Needs' vs 'Wants'."
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
    - Monthly Income: ₹{total_income}
    - Total Expenses: ₹{total_expenses}
    - Net Savings: ₹{net_savings}
    - Savings Rate: {savings_percentage}%

    ### Expense Breakdown
    {expenses_breakdown}

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

    return call_llm(prompt)
