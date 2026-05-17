import re
import math

def calculate_deterministic_emi(query: str):
    """
    Attempts to extract Loan Amount, Rate, and Tenure to calculate EMI deterministically.
    """
    try:
        # Normalize text
        text = query.lower().replace(",", "")
        
        # Extract Principal (e.g. 25 lakh, 2500000)
        principal = 0
        p_match_lakh = re.search(r"(\d+(\.\d+)?)\s*lakh", text)
        p_match_num = re.search(r"(\d+)\s*(?:home|loan|rupees|rs)", text)
        
        if p_match_lakh:
            principal = float(p_match_lakh.group(1)) * 100000
        elif p_match_num:
            # Simple heuristic: ignore small numbers like "15 years", "8%"
            nums = [float(x) for x in re.findall(r"(\d+)", text)]
            possible_ps = [x for x in nums if x > 1000] # Principal usually > 1000
            if possible_ps: principal = max(possible_ps)
            
        # Extract Rate (e.g. 8%, 8.5 interest)
        rate = 0
        r_match = re.search(r"(\d+(\.\d+)?)%", text)
        if not r_match:
            r_match = re.search(r"(\d+(\.\d+)?)\s*interest", text)
        if r_match:
            rate = float(r_match.group(1))
            
        # Extract Tenure (e.g. 15 years, 180 months)
        years = 0
        y_match = re.search(r"(\d+(\.\d+)?)\s*year", text)
        if y_match:
            years = float(y_match.group(1))
            
        # Calculate
        if principal > 0 and rate > 0 and years > 0:
            r = rate / (12 * 100) # Monthly rate
            n = years * 12 # Months
            
            emi = principal * r * ((1 + r)**n) / (((1 + r)**n) - 1)
            
            return f"""
            🧮 **EMI Calculator**
            
            - **Principal:** ₹{principal:,.0f}
            - **Rate:** {rate}%
            - **Tenure:** {years} Years ({int(n)} Months)
            
            ### ✅ Monthly EMI: ₹{emi:,.2f}
            
            *(Calculated deterministically)*
            """
    except Exception as e:
        print(f"Regex EMI Error: {e}")
        return None
        
    return None
