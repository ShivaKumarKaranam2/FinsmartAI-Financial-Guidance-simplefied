"""Personal Finance Assistant schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FinanceQueryRequest(BaseModel):
    """Request model for personal finance chatbot queries."""
    query: str = Field(..., description="User query or financial narrative")
    user_id: Optional[str] = Field("user_default", description="User identifier")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Recent conversation turns")


class FinanceAnalysisResponse(BaseModel):
    """Response containing either direct financial answer or full personal cash flow analysis."""
    type: str  # "general_answer" | "personal_finance_data" | "fallback"
    response: Optional[str] = None
    financial_summary: Optional[Dict[str, Any]] = None
    cash_flow_summary: Optional[Dict[str, Any]] = None
    investment_guidance: Optional[str] = None
    investment_json: Optional[Dict[str, Any]] = None
