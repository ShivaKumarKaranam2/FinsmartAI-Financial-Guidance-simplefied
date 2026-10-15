"""
Rule-Based Portfolio Investment Advisor Engine.
Maps savings tiers to structured asset allocation, risk levels, and financial notes.
Adheres to Open/Closed Principle (OCP) - easy to extend tiers without breaking interface.
"""

from typing import Dict, Any, List


def investment_advisor_json(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    FinSmart AI - Investment Recommendation Engine (JSON-based)

    Input:
    {
        "savings_amount": <int or float>
    }

    Output:
    Structured investment recommendations (JSON) matching frontend expectations.
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
    response: Dict[str, Any] = {
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
                "allocation_percent": 40,
                "risk_level": "Low",
                "reason": "Better returns than savings with high liquidity"
            }
        ]
        response["advisor_notes"].append(
            "Maintain at least 1 month of expenses in liquid funds."
        )

    # Tier 3: Moderate Savings
    elif 50000 <= savings < 150000:
        response["investment_strategy"] = "Balanced Growth & Safety"
        response["recommended_allocation"] = [
            {
                "instrument": "Fixed Deposit",
                "allocation_percent": 30,
                "risk_level": "Low",
                "reason": "Safe capital foundation"
            },
            {
                "instrument": "Index Mutual Fund (Nifty 50)",
                "allocation_percent": 40,
                "risk_level": "Medium",
                "reason": "Long-term wealth creation via index investing"
            },
            {
                "instrument": "Debt Fund / PPF",
                "allocation_percent": 30,
                "risk_level": "Low",
                "reason": "Tax-efficient stable returns"
            }
        ]
        response["advisor_notes"].append(
            "Start a Systematic Investment Plan (SIP) in index funds."
        )

    # Tier 4: High Savings
    elif 150000 <= savings < 500000:
        response["investment_strategy"] = "Diversified Wealth Accumulation"
        response["recommended_allocation"] = [
            {
                "instrument": "Large & Mid Cap Mutual Funds",
                "allocation_percent": 45,
                "risk_level": "Medium",
                "reason": "Capital appreciation over 5+ years"
            },
            {
                "instrument": "Direct Equity / Bluechip Stocks",
                "allocation_percent": 20,
                "risk_level": "High",
                "reason": "Higher returns from market leaders"
            },
            {
                "instrument": "PPF / Sovereign Gold Bond",
                "allocation_percent": 20,
                "risk_level": "Low",
                "reason": "Inflation hedge and tax saving"
            },
            {
                "instrument": "Emergency Fund (Liquid / FD)",
                "allocation_percent": 15,
                "risk_level": "Low",
                "reason": "Safety net for unexpected expenses"
            }
        ]
        response["advisor_notes"].append(
            "Diversify across asset classes and review portfolio every 6 months."
        )

    # Tier 5: Very High Savings
    else:
        response["investment_strategy"] = "Aggressive Growth & Capital Preservation"
        response["recommended_allocation"] = [
            {
                "instrument": "Diversified Equity Mutual Funds",
                "allocation_percent": 40,
                "risk_level": "Medium",
                "reason": "Core long-term growth driver"
            },
            {
                "instrument": "Direct Stock Portfolio",
                "allocation_percent": 25,
                "risk_level": "High",
                "reason": "Alpha generation through selective equity picks"
            },
            {
                "instrument": "Debt & Fixed Income (Corporate Bonds / PPF)",
                "allocation_percent": 20,
                "risk_level": "Low",
                "reason": "Income stability and risk mitigation"
            },
            {
                "instrument": "Gold / Alternative Investments",
                "allocation_percent": 15,
                "risk_level": "Medium",
                "reason": "Hedge against inflation and market volatility"
            }
        ]
        response["advisor_notes"].append(
            "Consider consulting a SEBI-registered investment advisor for tax optimization."
        )

    return response
