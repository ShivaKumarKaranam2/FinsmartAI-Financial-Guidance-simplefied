"""Portfolio, stock analysis, and investment advisor schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    company: str = Field(
        ..., 
        description="Stock ticker symbol (e.g., 'AAPL', 'INFY.NS')",
        example="INFY.NS"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "INFY.NS"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for CrewAI multi-agent stock analysis."""
    status: str = Field(..., description="Status of the analysis")
    company: str = Field(..., description="Company ticker analyzed")
    analysis: str = Field(..., description="Full analysis report in markdown")
    timestamp: str = Field(..., description="Analysis timestamp")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Structured data for frontend chart visualizations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "company": "INFY.NS",
                "analysis": "# Investment Analysis Report...",
                "timestamp": "2026-02-11T21:53:00+05:30",
                "chart_data": None
            }
        }


class AllocationItem(BaseModel):
    """Recommended asset allocation entry."""
    instrument: str
    allocation_percent: float
    risk_level: str
    reason: str


class RecommendationRequest(BaseModel):
    """Request model for savings-based portfolio recommendation."""
    savings_amount: float = Field(..., description="Current savings amount in INR", example=50000.0)


class RecommendationResponse(BaseModel):
    """Response model for savings-based portfolio recommendation."""
    input_savings: float
    investment_strategy: str
    recommended_allocation: List[Dict[str, Any]]
    advisor_notes: List[str]


class AIAdvisorRequest(BaseModel):
    """Request model for persona-driven AI investment guidance."""
    cash_flow_summary: Dict[str, Any] = Field(..., description="Cash flow summary with income, expenses, and savings")
    financial_goals: Optional[str] = Field("wealth building and financial security", description="User financial goals")
    risk_tolerance: Optional[str] = Field("moderate", description="User risk profile (low, moderate, high)")


class AIAdvisorResponse(BaseModel):
    """Response model for AI investment guidance."""
    guidance: str
