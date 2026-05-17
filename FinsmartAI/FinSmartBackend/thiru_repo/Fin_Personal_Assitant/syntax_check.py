try:
    import model_loader
    print("model_loader imported")
    import expenses_categorizer
    print("expenses_categorizer imported")
    import savings_analysis
    print("savings_analysis imported")
    import budget_recommendation
    print("budget_recommendation imported")
    import investment_advisor
    print("investment_advisor imported")
    import streamlit_app
    print("streamlit_app imported")
    print("✅ All modules syntax checked.")
except Exception as e:
    print(f"❌ Syntax/Import Error: {e}")
