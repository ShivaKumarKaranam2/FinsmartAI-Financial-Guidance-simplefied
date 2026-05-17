from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# --- Generic Response ---
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# --- FinRAG Schemas ---
class IngestResponse(BaseModel):
    session_id: str
    chunks_ingested: int
    message: str

class QueryRequest(BaseModel):
    session_id: str
    question: str
    user_id: Optional[str] = "user_default"

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- Personal Assistant Schemas ---
class FinanceQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = "user_default"

class FinanceAnalysisResponse(BaseModel):
    type: str # "general_answer" | "financial_analysis" | "fallback"
    response: Optional[str] = None
    financial_summary: Optional[Dict[str, Any]] = None
    cash_flow_summary: Optional[Dict[str, Any]] = None
    investment_guidance: Optional[str] = None
    investment_json: Optional[Dict[str, Any]] = None
