"""
Routers package for FinSmart AI Backend API.
Exports budget, portfolio, rag, finance, and sentiment routers.
"""

from app.api.routers.budget_routes import router as budget_router
from app.api.routers.portfolio_routes import router as portfolio_router
from app.api.routers.rag_routes import router as rag_router
from app.api.routers.finance_routes import router as finance_router
from app.api.routers.sentiment_routes import router as sentiment_router

__all__ = [
    "budget_router",
    "portfolio_router",
    "rag_router",
    "finance_router",
    "sentiment_router",
]
