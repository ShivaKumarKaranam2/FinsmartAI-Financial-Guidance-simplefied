"""
Portfolio and Investment Advisor Router.
Prefix: /api/portfolio
Handles stock multi-agent research, savings allocation setup, and persona-driven AI insights.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.api.schemas.portfolio import (
    AnalysisRequest,
    AnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    AIAdvisorRequest,
    AIAdvisorResponse,
)
from app.services.portfolio.crew_service import CrewService
from app.services.portfolio.advisor_rules import investment_advisor_json
from app.services.portfolio.ai_guidance import generate_investment_guidance

router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton crew service instance
_crew_service = None

def get_crew_service() -> CrewService:
    global _crew_service
    if _crew_service is None:
        _crew_service = CrewService()
    return _crew_service


@router.post("/analyze", response_model=AnalysisResponse, summary="Analyze stock via multi-agent crew")
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock and generate an investment report using CrewAI multi-agent orchestration.
    """
    try:
        logger.info(f"Starting stock analysis for ticker: {request.company}")
        crew_service = get_crew_service()
        result = await crew_service.analyze_stock(request.company)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Stock analysis failed")
            )
        
        logger.info(f"Completed stock analysis for ticker: {request.company}")
        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing stock {request.company}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/recommendation", response_model=RecommendationResponse, summary="Get portfolio asset allocation setup")
async def get_portfolio_recommendation(request: RecommendationRequest):
    """
    Returns structured asset allocation breakdown based on current savings tier.
    """
    try:
        result = investment_advisor_json({"savings_amount": request.savings_amount})
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return RecommendationResponse(
            input_savings=result["input_savings"],
            investment_strategy=result["investment_strategy"],
            recommended_allocation=result["recommended_allocation"],
            advisor_notes=result["advisor_notes"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate portfolio recommendation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(e)}")


@router.post("/ai-advisor", response_model=AIAdvisorResponse, summary="Get persona-driven investment guidance")
async def get_ai_investment_guidance(request: AIAdvisorRequest):
    """
    Generates personalized, persona-driven investment recommendations using LLM.
    """
    try:
        guidance = generate_investment_guidance(
            cash_flow_summary=request.cash_flow_summary,
            financial_goals=request.financial_goals or "wealth building",
            risk_tolerance=request.risk_tolerance or "moderate"
        )
        return AIAdvisorResponse(guidance=guidance)
    except Exception as e:
        logger.error(f"Failed to generate AI investment guidance: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate AI guidance: {str(e)}")
