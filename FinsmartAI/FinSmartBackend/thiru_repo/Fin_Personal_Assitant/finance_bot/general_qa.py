from .tools import calculate_deterministic_emi
from model_loader import call_llm

def answer_general_finance_question(question: str) -> str:
    q_lower = question.lower()
    
    # 1. Math / Calculation Branch
    if any(k in q_lower for k in ["calculate", "compute", "emi", "interest", "amount", "math"]):
        # Try Deterministic Logic first
        math_result = calculate_deterministic_emi(question)
        if math_result: return math_result
        
        # Fallback to LLM Math
        prompt = f"""
        You are a financial calculator.
        Task: Perform the requested calculation.
        Question: "{question}"
        
        STRICT OUTPUT FORMAT:
        Summary: (The final answer in plain text)
        
        Key Steps:
        (Explain the calculation in simple sentences)
        
        Note:
        (Any assumptions in plain text)
        
        CRITICAL: Do NOT use markdown, code blocks, or bold text. Write as normal paragraph text.
        """
        return call_llm(prompt, max_tokens=800, temperature=0.1)

    # 2. Tax / Context Branch (RAG)
    tax_keywords = ["tax", "slab", "regime", "deduction", "section", "80c", "old", "new"]
    if any(k in q_lower for k in tax_keywords):
        context = """
        CURRENT INDIAN FINANCIAL FACTS (FY 2024-25):
        - **New Tax Regime (Default):**
          - Up to ₹3 Lakh: Nil
          - ₹3 Lakh - ₹7 Lakh: 5% (Rebate u/s 87A available up to ₹7 Lakh income, so effective tax is 0)
          - ₹7 Lakh - ₹10 Lakh: 10%
          - ₹10 Lakh - ₹12 Lakh: 15%
          - ₹12 Lakh - ₹15 Lakh: 20%
          - Above ₹15 Lakh: 30%
        - **Old Tax Regime:** High exemptions but different slabs (0-2.5L Nil, 2.5-5L 5%, 5-10L 20%, >10L 30%).
        - **Standard Deduction:** ₹75,000 (New Regime proposed FY25).
        """
        prompt = f"""
        You are an Indian Tax Expert.
        Use the CONTEXT to answer.
        
        CONTEXT:
        {context}
        
        Question: "{question}"
        
        STRICT OUTPUT FORMAT:
        Summary: (Direct answer in plain text)
        
        Key Details:
        (Explain the rule using simple bullet points without markdown symbols like **)
        
        Advice:
        (Practical tip in plain text)
        
        CRITICAL: Do NOT use markdown, code blocks, or bold text. Write as normal paragraph text.
        """
        return call_llm(prompt, max_tokens=800, temperature=0.1)

    # 3. Comparison / Difference Branch
    if any(k in q_lower for k in ["difference", "vs", "compare", "better", "versus"]):
        prompt = f"""
        You are a Financial Advisor.
        Compare the following concepts nicely in plain text.
        
        Question: "{question}"
        
        STRICT OUTPUT FORMAT:
        Summary: (Short simple overview of the major difference)
        
        Comparison:
        - (Point 1 comparison)
        - (Point 2 comparison)
        - (Point 3 comparison)
        
        Decision:
        (Practical takeaway on which one to choose)
        
        CRITICAL: Do NOT use markdown tables or code blocks. Use simple bullet points.
        """
        return call_llm(prompt, max_tokens=600, temperature=0.3)

    # 4. Relationship / Impact Branch
    if any(k in q_lower for k in ["relationship", "affect", "impact", "effect", "link", "correlation", "cause"]):
        prompt = f"""
        You are a Financial Educator.
        Explain the relationship or cause-and-effect link.
        
        Question: "{question}"
        
        STRICT OUTPUT FORMAT:
        Summary: (One-line summary of the connection)
        
        Mechanism:
        - (Step 1 -> Step 2: Explain the flow using '->' or similar indicators)
        - (Cause -> Effect: Clear directional logic)
        
        Takeaway:
        (Practical implication for the user in plain text)
        
        CRITICAL: Use '->' to show flow. Do NOT use markdown code blocks.
        """
        return call_llm(prompt, max_tokens=600, temperature=0.3)

    # 5. General Knowledge Branch (Open)
    prompt = f"""
    You are a friendly Indian Financial Educator.
    Explain the following concept clearly to a beginner.
    
    Question: "{question}"
    
    STRICT OUTPUT FORMAT:
    Summary: (Clear definition in plain text)
    
    Key Points:
    (Explain the concept using simple dashes for lists. Do not use bold/markdown)
    
    Advice:
    (Actionable tip in plain text)
    
    CRITICAL: Do NOT use markdown, code blocks, or bold text. Write as normal paragraph text.
    """
    return call_llm(prompt, max_tokens=800, temperature=0.5)
