import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.portfolio.advisor_rules import investment_advisor_json


def test_portfolio_tier_very_low():
    res = investment_advisor_json({"savings_amount": 5000})
    assert res["input_savings"] == 5000
    assert res["investment_strategy"] == "Capital Protection & Liquidity"
    assert len(res["recommended_allocation"]) == 1
    assert res["recommended_allocation"][0]["allocation_percent"] == 100


def test_portfolio_tier_low():
    res = investment_advisor_json({"savings_amount": 25000})
    assert res["input_savings"] == 25000
    assert res["investment_strategy"] == "Low Risk with Market Introduction"
    assert len(res["recommended_allocation"]) == 2


def test_portfolio_tier_moderate():
    res = investment_advisor_json({"savings_amount": 100000})
    assert res["input_savings"] == 100000
    assert res["investment_strategy"] == "Balanced Growth & Safety"
    total_pct = sum(item["allocation_percent"] for item in res["recommended_allocation"])
    assert total_pct == 100


def test_portfolio_tier_high():
    res = investment_advisor_json({"savings_amount": 300000})
    assert res["input_savings"] == 300000
    assert res["investment_strategy"] == "Diversified Wealth Accumulation"
    total_pct = sum(item["allocation_percent"] for item in res["recommended_allocation"])
    assert total_pct == 100


def test_portfolio_tier_very_high():
    res = investment_advisor_json({"savings_amount": 1000000})
    assert res["input_savings"] == 1000000
    assert res["investment_strategy"] == "Aggressive Growth & Capital Preservation"
    total_pct = sum(item["allocation_percent"] for item in res["recommended_allocation"])
    assert total_pct == 100


def test_portfolio_invalid_inputs():
    assert "error" in investment_advisor_json({})
    assert "error" in investment_advisor_json({"savings_amount": -500})
    assert "error" in investment_advisor_json({"savings_amount": 0})
    assert "error" in investment_advisor_json({"savings_amount": "invalid"})


if __name__ == "__main__":
    test_portfolio_tier_very_low()
    test_portfolio_tier_low()
    test_portfolio_tier_moderate()
    test_portfolio_tier_high()
    test_portfolio_tier_very_high()
    test_portfolio_invalid_inputs()
    print("✅ All portfolio advisor tests passed!")
