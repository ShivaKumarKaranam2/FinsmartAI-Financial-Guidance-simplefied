"""
Market News Engine
Main orchestrator that combines API client and sentiment analyzer
Produces final structured JSON output
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .config import Config
from .api_client import MarketauxClient, MarketauxAPIError
from .sentiment_analyzer import SentimentAnalyzer, MarketMood, FearGreedLevel

logger = logging.getLogger(__name__)


class MarketNewsEngine:
    """
    Main engine for market news and sentiment analysis
    Orchestrates data fetching, analysis, and response building
    """
    
    def __init__(self, config: Optional[Config] = None, api_key: Optional[str] = None):
        """
        Initialize the market news engine
        
        Args:
            config: Configuration object (optional)
            api_key: API key override (optional)
        """
        if config:
            self.config = config
        elif api_key:
            self.config = Config.from_env(api_key)
        else:
            self.config = Config()
        
        self.client = MarketauxClient(self.config)
        self.analyzer = SentimentAnalyzer(self.config)
    
    def fetch_news(self, limit: Optional[int] = None, **kwargs) -> list:
        """
        Fetch news articles with sentiment data
        
        Args:
            limit: Number of articles to fetch
            **kwargs: Additional filters for API
            
        Returns:
            List of processed articles
        """
        return self.client.fetch_news_with_sentiment(
            limit=limit or self.config.DEFAULT_LIMIT,
            **kwargs
        )
    
    def aggregate_sentiment(self, articles: list) -> Dict[str, Any]:
        """
        Aggregate sentiment across articles
        
        Args:
            articles: List of articles with sentiment data
            
        Returns:
            Aggregated sentiment statistics
        """
        return self.analyzer.aggregate_sentiment(articles)
    
    def compute_market_mood(self, aggregated_data: Dict[str, Any]) -> str:
        """
        Compute market mood classification
        
        Args:
            aggregated_data: Aggregated sentiment data
            
        Returns:
            Market mood string (Bullish/Bearish/Neutral/Sideways)
        """
        mood = self.analyzer.compute_market_mood(aggregated_data)
        return mood.value
    
    def compute_fear_greed(self, avg_score: float) -> str:
        """
        Compute fear-greed index
        
        Args:
            avg_score: Average sentiment score
            
        Returns:
            Fear-greed level string
        """
        level = self.analyzer.compute_fear_greed(avg_score)
        return level.value
    
    def extract_top_news(
        self, 
        articles: list, 
        count: Optional[int] = None
    ) -> tuple:
        """
        Extract top bullish and bearish news
        
        Args:
            articles: List of articles
            count: Number of articles per category
            
        Returns:
            Tuple of (top_bullish, top_bearish)
        """
        return self.analyzer.extract_top_news(
            articles, 
            count=count or self.config.TOP_NEWS_COUNT
        )
    
    def build_final_response(
        self,
        articles: list,
        aggregated_data: Dict[str, Any],
        market_mood: str,
        fear_greed: str,
        top_bullish: list,
        top_bearish: list,
        include_all_articles: bool = False
    ) -> Dict[str, Any]:
        """
        Build the final structured JSON response
        
        Args:
            articles: All processed articles
            aggregated_data: Sentiment aggregation results
            market_mood: Market mood string
            fear_greed: Fear-greed index string
            top_bullish: Top bullish news list
            top_bearish: Top bearish news list
            include_all_articles: Whether to include all articles in response
            
        Returns:
            Complete response dictionary
        """
        # Generate summary note
        mood_enum = MarketMood(market_mood)
        fg_enum = FearGreedLevel(fear_greed)
        summary_note = self.analyzer.generate_summary_note(
            mood_enum, 
            fg_enum, 
            aggregated_data
        )
        
        response = {
            "market_mood": market_mood,
            "fear_greed_index": fear_greed,
            "average_sentiment_score": aggregated_data['average_score'],
            "top_bullish_news": top_bullish,
            "top_bearish_news": top_bearish,
            "summary_note": summary_note,
            "metadata": {
                "total_articles_analyzed": aggregated_data['total_articles'],
                "positive_articles": aggregated_data['positive_count'],
                "negative_articles": aggregated_data['negative_count'],
                "neutral_articles": aggregated_data['neutral_count'],
                "sentiment_variance": aggregated_data['variance'],
                "analysis_timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if include_all_articles:
            response["all_articles"] = articles
        
        return response
    
    def run(
        self, 
        limit: Optional[int] = None,
        include_all_articles: bool = False,
        as_json: bool = False,
        **kwargs
    ) -> Dict[str, Any] | str:
        """
        Execute the complete news and sentiment analysis pipeline
        
        Args:
            limit: Number of articles to fetch (default: 20)
            include_all_articles: Include all articles in response
            as_json: Return as JSON string instead of dict
            **kwargs: Additional API filters
            
        Returns:
            Complete analysis result as dict or JSON string
        """
        try:
            # Step 1: Fetch news
            logger.info("Fetching news articles...")
            articles = self.fetch_news(limit=limit, **kwargs)
            
            if not articles:
                return self._empty_response(as_json)
            
            # Step 2: Aggregate sentiment
            logger.info("Aggregating sentiment data...")
            aggregated = self.aggregate_sentiment(articles)
            
            # Step 3: Compute market mood
            logger.info("Computing market mood...")
            market_mood = self.compute_market_mood(aggregated)
            
            # Step 4: Compute fear-greed index
            logger.info("Computing fear-greed index...")
            fear_greed = self.compute_fear_greed(aggregated['average_score'])
            
            # Step 5: Extract top news
            logger.info("Extracting top bullish and bearish news...")
            top_bullish, top_bearish = self.extract_top_news(articles)
            
            # Step 6: Build final response
            logger.info("Building final response...")
            response = self.build_final_response(
                articles=articles,
                aggregated_data=aggregated,
                market_mood=market_mood,
                fear_greed=fear_greed,
                top_bullish=top_bullish,
                top_bearish=top_bearish,
                include_all_articles=include_all_articles
            )
            
            if as_json:
                return json.dumps(response, indent=2, ensure_ascii=False)
            
            return response
            
        except MarketauxAPIError as e:
            logger.error(f"API Error: {e.message}")
            error_response = {
                "error": True,
                "message": e.message,
                "status_code": e.status_code
            }
            return json.dumps(error_response, indent=2) if as_json else error_response
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            error_response = {
                "error": True,
                "message": f"Analysis failed: {str(e)}"
            }
            return json.dumps(error_response, indent=2) if as_json else error_response
    
    def _empty_response(self, as_json: bool) -> Dict[str, Any] | str:
        """Generate empty response when no articles found"""
        response = {
            "market_mood": "Neutral",
            "fear_greed_index": "Neutral",
            "average_sentiment_score": 0.0,
            "top_bullish_news": [],
            "top_bearish_news": [],
            "summary_note": "No news articles found for analysis.",
            "metadata": {
                "total_articles_analyzed": 0,
                "positive_articles": 0,
                "negative_articles": 0,
                "neutral_articles": 0,
                "sentiment_variance": 0.0,
                "analysis_timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        }
        return json.dumps(response, indent=2) if as_json else response
