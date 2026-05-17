from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load Env Vars — local .env first (has all keys including AstraDB),
# then FinRAG/.env as fallback for any extras. override=False means
# the first-loaded value wins, so local .env takes priority.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "thiru_repo/FinRAG/.env"), override=False)

# Import Routers AFTER loading env
from routers import rag_routes, finance_routes, sentiment_routes, budget_routes, portfolio_routes

app = FastAPI(
    title="FinSmart AI Backend",
    description="Unified API integrating Sentiment, RAG, Budget, and Portfolio Analysis",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(rag_routes.router, prefix="/api/rag", tags=["FinRAG (Document QA)"])
app.include_router(finance_routes.router, prefix="/api/finance_rag", tags=["Personal Finance Assistant (RAG)"])
app.include_router(sentiment_routes.router, prefix="/api/sentiment", tags=["Market Sentiment"])
app.include_router(budget_routes.router, prefix="/api/budget", tags=["Budget Recommendations"])
app.include_router(portfolio_routes.router, prefix="/api/portfolio", tags=["Investment Advisor"])

@app.get("/")
async def root():
    return {"message": "FinSmart AI Backend is Running 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
