"""FastAPI application for stock analysis crew"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from models import AnalysisRequest, AnalysisResponse, ErrorResponse
from crew_service import CrewService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinSmartAI Stock Analysis API",
    description="Professional stock analysis using AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize crew service
crew_service = CrewService()


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "FinSmartAI Stock Analysis API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
    tags=["Analysis"],
    summary="Analyze stock",
    description="Run comprehensive stock analysis using AI agents"
)
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock and generate investment report
    
    - **company**: Stock ticker symbol (e.g., AAPL, INFY.NS)
    
    Returns comprehensive investment analysis with:
    - Valuation ratios and metrics
    - Financial health assessment
    - Growth analysis
    - Investment recommendation
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


@app.get("/api/v1/test", tags=["Testing"])
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
