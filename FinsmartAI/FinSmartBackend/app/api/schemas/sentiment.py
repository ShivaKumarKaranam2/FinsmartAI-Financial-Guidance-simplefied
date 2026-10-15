"""Market Sentiment and Index analysis schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Nifty50Data(BaseModel):
    """Historical data for Nifty 50 index."""
    dates: List[str]
    closes: List[float]
    current: float
    change: float
    change_pct: float


class SentimentArticle(BaseModel):
    """Article data with sentiment score."""
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None
    source: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None


class MarketSentimentResponse(BaseModel):
    """Aggregated market sentiment analysis response."""
    status: str = "success"
    total_articles: int
    analyzed_articles: int
    market_mood: str
    fear_greed_index: float
    average_sentiment: float
    bullish_percentage: float
    bearish_percentage: float
    neutral_percentage: float
    top_articles: List[Dict[str, Any]] = Field(default_factory=list)
