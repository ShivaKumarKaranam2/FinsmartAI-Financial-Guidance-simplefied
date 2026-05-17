from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from market_sentiment.news_engine import MarketNewsEngine
import yfinance as yf
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/nifty50")
async def get_nifty50_data(days: int = Query(30, description="Number of days of data")):
    """Fetch Nifty 50 index historical data for charting."""
    try:
        nifty = yf.Ticker("^NSEI")
        end = datetime.now() + timedelta(days=1)
        start = end - timedelta(days=days + 1)
        hist = nifty.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No Nifty 50 data available")
        
        dates = [d.strftime("%d %b") for d in hist.index]
        closes = [round(float(c), 2) for c in hist["Close"]]
        current = closes[-1] if closes else 0
        prev = closes[-2] if len(closes) > 1 else current
        change = round(current - prev, 2)
        change_pct = round((change / prev) * 100, 2) if prev else 0
        
        return {
            "dates": dates,
            "closes": closes,
            "current": current,
            "change": change,
            "change_pct": change_pct,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nifty 50 fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Nifty 50 data: {str(e)}")

@router.get("/market")
async def get_market_sentiment(
    limit: int = Query(20, description="Number of articles to fetch"),
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols"),
    search: Optional[str] = Query(None, description="Search term"),
    include_all: bool = Query(False, description="Include all articles in response")
):
    try:
        engine = MarketNewsEngine()
        kwargs = {}
        if symbols:
            kwargs['symbols'] = symbols
        if search:
            kwargs['search'] = search
            
        result = engine.run(
            limit=limit,
            include_all_articles=include_all,
            **kwargs
        )
        
        if 'error' in result:
             raise HTTPException(status_code=500, detail=result.get('message', 'Unknown API Error'))
             
        return result
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

