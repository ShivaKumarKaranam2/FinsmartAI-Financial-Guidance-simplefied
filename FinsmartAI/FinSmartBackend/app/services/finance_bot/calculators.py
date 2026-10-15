"""
Deterministic Financial Calculators.
Provides exact mathematical formula calculations (EMI, etc.) without relying on probabilistic LLMs.
"""

import re
import math
from typing import Optional


def calculate_deterministic_emi(query: str) -> Optional[str]:
    """
    Attempts to extract Loan Amount, Rate, and Tenure to calculate EMI deterministically.
    
    Args:
        query: User text potentially containing loan parameters
        
    Returns:
        Formatted markdown calculation string if parameters are found, else None
    """
    try:
        text = query.lower().replace(",", "")
        
        # Extract Principal (e.g., 25 lakh, 2500000)
        principal = 0.0
        p_match_lakh = re.search(r"(\d+(?:\.\d+)?)\s*lakh", text)
        p_match_num = re.search(r"(\d+)\s*(?:home|loan|rupees|rs)", text)
        
        if p_match_lakh:
            principal = float(p_match_lakh.group(1)) * 100000.0
        elif p_match_num:
            nums = [float(x) for x in re.findall(r"(\d+)", text)]
            possible_ps = [x for x in nums if x > 1000]
            if possible_ps:
                principal = max(possible_ps)
            
        # Extract Interest Rate (e.g., 8%, 8.5 interest)
        rate = 0.0
        r_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if not r_match:
            r_match = re.search(r"(\d+(?:\.\d+)?)\s*interest", text)
        if r_match:
            rate = float(r_match.group(1))
            
        # Extract Tenure (e.g., 15 years, 180 months)
        years = 0.0
        y_match = re.search(r"(\d+(?:\.\d+)?)\s*year", text)
        if y_match:
            years = float(y_match.group(1))
        else:
            m_match = re.search(r"(\d+(?:\.\d+)?)\s*month", text)
            if m_match:
                years = float(m_match.group(1)) / 12.0
            
        # Calculate EMI using standard formula: P * r * (1+r)^n / ((1+r)^n - 1)
        if principal > 0 and rate > 0 and years > 0:
            r = rate / (12 * 100)  # Monthly rate
            n = years * 12         # Months
            
            emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            total_payment = emi * n
            total_interest = total_payment - principal
            
            return f"""🧮 **EMI Calculator**

- **Principal:** ₹{principal:,.0f}
- **Annual Rate:** {rate}%
- **Tenure:** {years:g} Years ({int(n)} Months)
- **Total Interest:** ₹{total_interest:,.2f}
- **Total Amount Payable:** ₹{total_payment:,.2f}

### ✅ Monthly EMI: ₹{emi:,.2f}

*(Calculated deterministically)*"""
    except Exception as e:
        return None
        
    return None
