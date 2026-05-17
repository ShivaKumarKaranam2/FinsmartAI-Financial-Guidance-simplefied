from fastapi import APIRouter, HTTPException
from ..schemas import FinanceQueryRequest, FinanceAnalysisResponse, APIResponse
import sys
import os

# Ensure Fin_Personal_Assitant is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Fin_Personal_Assitant")))

# Import Finance Bot Logic
try:
    from Fin_Personal_Assitant.finance_bot.core import fin_smart_process
    from Fin_Personal_Assitant.model_loader import load_model
    
    # Preload Local Model if possible, or let it load on first request
    # load_model() uses streamlit cache, which might not work here.
    # We should update model_loader to be framework agnostic or rely on LRU cache
    # For now, we trust the import.
except ImportError as e:
    print(f"Error importing Finance Bot: {e}")

router = APIRouter()

@router.post("/query", response_model=FinanceAnalysisResponse)
async def finance_query(request: FinanceQueryRequest):
    try:
        # Process specific finance logic
        # fin_smart_process handles routing between General QA and Analysis
        result = fin_smart_process(request.query)
        
        return FinanceAnalysisResponse(
            type=result.get("type"),
            response=result.get("response"),
            financial_summary=result.get("financial_summary"),
            cash_flow_summary=result.get("cash_flow_summary"),
            investment_guidance=result.get("investment_guidance"),
            investment_json=result.get("investment_json")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finance processing failed: {str(e)}")
