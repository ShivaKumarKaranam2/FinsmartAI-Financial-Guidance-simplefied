import streamlit as st
import pandas as pd
import plotly.express as px
import re
import math
from model_loader import load_model, call_llm
from expenses_categorizer import categorize_expenses
from savings_analysis import savings_analysis
from budget_recommendation import analyze_cash_flow_and_savings
from investment_advisor import generate_investment_guidance, investment_advisor_json

# Page Config
st.set_page_config(
    page_title="FinSmart AI - Personal Finance Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .stApp {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    st.title("💼 FinSmart AI")
    st.caption("Your AI-powered Financial Assistant")
    st.markdown("---")
    
    # Load model
    if 'model_loaded' not in st.session_state:
        with st.spinner("Loading AI Model (Shiva-k22/gemma-FinAI)..."):
            load_model()
            st.session_state.model_loaded = True
        st.success("Model Loaded Successfully!")
    else:
        st.success("Model Active ✅")

    st.markdown("### How to use:")
    st.info(
        "1. **Ask a question** (e.g. 'What is SIP?')\n"
        "2. **Analyze finances** (e.g. 'I earn 50k, spent 5k on food...')"
    )

# --- Logic Functions (Ported from Notebook) ---

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
            # Assume principal is the largest number? Or look for context.
            # Let's trust "lakh" match first. If user typed "2500000", simpler regex:
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
        Show the formula and steps.
        """
        return call_llm(prompt, max_tokens=600, temperature=0.1)

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
        """
        return call_llm(prompt, max_tokens=400, temperature=0.1)

    # 3. General Knowledge Branch (Open)
    prompt = f"""
    You are a friendly Indian Financial Educator.
    Explain the following concept clearly to a beginner.
    
    Question: "{question}"
    
    Answer concisely (under 150 words).
    """
    return call_llm(prompt, max_tokens=300, temperature=0.7)

def fin_smart_router(user_input: str):
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
        status_text = st.empty()
        status_text.info("🔄 Identifying Expenses...")
        
        # Step 1: Categorize
        categorized_expenses = categorize_expenses(user_input, "text")
        
        status_text.info("🔄 Analyzing Savings & Income...")
        # Step 2: Savings Analysis
        savings_result = savings_analysis(categorized_expenses, user_input)
        
        status_text.info("🔄 Generating Recommendations...")
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

        status_text.empty()
        
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


# --- Main UI ---

st.title("💰 Personal Finance Assistant")

query = st.chat_input("Enter your financial query or data...")

if query:
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)

    # Process and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = fin_smart_router(query)
        
        if result["type"] == "general_answer":
            txt_response = result.get("response", "").strip()
            if not txt_response:
                txt_response = "I apologize, but I couldn't generate a response. Please check your query or try rephrasing."
            st.markdown(txt_response)
            
        elif result["type"] == "financial_analysis":
            fs = result["financial_summary"]
            cf = result["cash_flow_summary"]
            inv = result["investment_json"]
            
            # 1. Summary Metrics
            st.subheader("📊 Financial Snapshot")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Monthly Income", f"₹{fs['income']:,.0f}")
            c2.metric("Total Expenses", f"₹{fs['total_expenses']:,.0f}", delta_color="inverse")
            c3.metric("Net Savings", f"₹{fs['savings']:,.0f}")
            c4.metric("Savings Rate", f"{fs['savings_percentage']}%")
            
            # 2. Tabs
            t1, t2, t3 = st.tabs(["Expenses", "Investment Advice", "Detailed Report"])
            
            with t1:
                col_a, col_b = st.columns([2, 1])
                
                # Prepare DF
                breakdown = fs["expense_breakdown_by_category"]
                if breakdown:
                    df = pd.DataFrame(list(breakdown.items()), columns=["Category", "Amount"])
                    
                    with col_a:
                        fig = px.pie(df, names="Category", values="Amount", title="Expense Distribution", hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col_b:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No expenses found.")

            with t2:
                st.subheader("💡 AI Investment Guidance")
                st.markdown(result["investment_guidance"])
                
                st.divider()
                
                # Render Allocation Chart from Rule-Based Logic
                if "recommended_allocation" in inv and inv["recommended_allocation"]:
                    st.subheader("📈 Recommended Asset Allocation")
                    alloc_df = pd.DataFrame(inv["recommended_allocation"])
                    fig_inv = px.bar(alloc_df, x="instrument", y="allocation_percent", color="risk_level", title="Portfolio Mix")
                    st.plotly_chart(fig_inv, use_container_width=True)
                    
                    with st.expander("Why this allocation?"):
                        st.dataframe(alloc_df[["instrument", "allocation_percent", "reason"]], hide_index=True)

            with t3:
                st.subheader("📋 Detailed Financial Report")
                
                # Create a clean flat dictionary for display
                details = {
                    "Monthly Income": fs.get("income", 0),
                    "Total Expenses": fs.get("total_expenses", 0),
                    "Net Savings": fs.get("savings", 0),
                    "Savings Rate (%)": fs.get("savings_percentage", 0),
                    "Projected Annual Savings": fs.get("savings", 0) * 12
                }
                
                st.table(pd.DataFrame(list(details.items()), columns=["Metric", "Value"]))
                
                # Show expense details if any
                if fs.get("expense_breakdown_by_category"):
                    st.markdown("#### 🛒 Expense Breakdown")
                    st.table(pd.DataFrame(list(fs["expense_breakdown_by_category"].items()), columns=["Category", "Amount"]))
        
        else:
            st.warning(result["response"])
