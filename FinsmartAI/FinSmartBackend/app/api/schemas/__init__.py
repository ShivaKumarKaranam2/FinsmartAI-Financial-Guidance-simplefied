"""
Schemas package for FinSmart AI Backend API.
Exports all Pydantic models for request validation and response formatting.
"""

from app.api.schemas.common import APIResponse, ErrorResponse
from app.api.schemas.budget import (
    BudgetAnalysisRequest,
    BudgetAnalysisResponse,
    ExpenseItem,
    SavingsSummary,
)
from app.api.schemas.portfolio import (
    AnalysisRequest,
    AnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    AIAdvisorRequest,
    AIAdvisorResponse,
    AllocationItem,
)
from app.api.schemas.rag import IngestResponse, QueryRequest, QueryResponse
from app.api.schemas.finance import FinanceQueryRequest, FinanceAnalysisResponse
from app.api.schemas.sentiment import Nifty50Data, MarketSentimentResponse, SentimentArticle

__all__ = [
    "APIResponse",
    "ErrorResponse",
    "BudgetAnalysisRequest",
    "BudgetAnalysisResponse",
    "ExpenseItem",
    "SavingsSummary",
    "AnalysisRequest",
    "AnalysisResponse",
    "RecommendationRequest",
    "RecommendationResponse",
    "AIAdvisorRequest",
    "AIAdvisorResponse",
    "AllocationItem",
    "IngestResponse",
    "QueryRequest",
    "QueryResponse",
    "FinanceQueryRequest",
    "FinanceAnalysisResponse",
    "Nifty50Data",
    "MarketSentimentResponse",
    "SentimentArticle",
]
