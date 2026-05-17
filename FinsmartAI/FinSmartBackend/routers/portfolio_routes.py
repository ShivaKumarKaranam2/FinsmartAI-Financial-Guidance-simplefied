from fastapi import APIRouter, HTTPException
import logging
from models import AnalysisRequest, AnalysisResponse, ErrorResponse
from crew_service import CrewService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize crew service
crew_service = CrewService()

@router.post("/analyze", response_model=AnalysisResponse, summary="Analyze stock")
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock and generate investment report using CrewAI.
    """
    try:
        logger.info(f"Starting analysis for {request.company}")
        
        # Execute analysis
        result = await crew_service.analyze_stock(request.company)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Analysis failed")
            )
        
        logger.info(f"Completed analysis for {request.company}")
        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {request.company}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
