"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for stock analysis"""
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
    """Response model for stock analysis"""
    status: str = Field(..., description="Status of the analysis")
    company: str = Field(..., description="Company ticker analyzed")
    analysis: str = Field(..., description="Full analysis report in markdown")
    timestamp: str = Field(..., description="Analysis timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "company": "INFY.NS",
                "analysis": "# Investment Analysis Report...",
                "timestamp": "2026-02-11T21:53:00+05:30"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    timestamp: str
