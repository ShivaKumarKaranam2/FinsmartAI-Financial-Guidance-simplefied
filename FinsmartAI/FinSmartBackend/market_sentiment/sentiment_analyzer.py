"""
Sentiment Analysis Module
Computes market mood, fear-greed index, and aggregates sentiment data
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

from .config import Config, ThresholdConfig


class MarketMood(Enum):
    """Market mood classification"""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"
    SIDEWAYS = "Sideways"


class FearGreedLevel(Enum):
    """Fear-Greed index classification"""
    EXTREME_FEAR = "Extreme Fear"
    FEAR = "Fear"
    NEUTRAL = "Neutral"
    GREED = "Greed"
    EXTREME_GREED = "Extreme Greed"


@dataclass
class SentimentResult:
    """Container for sentiment analysis results"""
    average_score: float
    market_mood: MarketMood
    fear_greed: FearGreedLevel
    total_articles: int
    positive_count: int
    negative_count: int
    neutral_count: int
    sentiment_variance: float


class SentimentAnalyzer:
    """
    Analyzes sentiment data from news articles
    Computes market mood and fear-greed indicators
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize sentiment analyzer
        
        Args:
            config: Configuration with threshold values
        """
        self.config = config or Config()
        self.thresholds = self.config.thresholds
    
    def aggregate_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate sentiment scores across all articles
        
        Args:
            articles: List of articles with sentiment_score field
            
        Returns:
            Dictionary with aggregated statistics
        """
        if not articles:
            return {
                'average_score': 0.0,
                'total_articles': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'variance': 0.0,
                'scores': []
            }
        
        scores = [a.get('sentiment_score', 0) for a in articles]
        
        # Count sentiment categories
        positive_count = sum(1 for s in scores if s >= 0.1)
        negative_count = sum(1 for s in scores if s <= -0.1)
        neutral_count = len(scores) - positive_count - negative_count
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores)
        variance = statistics.variance(scores) if len(scores) > 1 else 0.0
        
        return {
            'average_score': round(avg_score, 4),
            'total_articles': len(articles),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'variance': round(variance, 4),
            'scores': scores
        }
    
    def compute_market_mood(self, aggregated_data: Dict[str, Any]) -> MarketMood:
        """
        Determine overall market mood based on aggregated sentiment
        
        Logic:
        - Avg Sentiment ≥ +0.20 → Bullish
        - Avg Sentiment ≤ -0.20 → Bearish
        - Between -0.20 and +0.20 → Neutral
        - High variance with mixed sentiment → Sideways
        
        Args:
            aggregated_data: Dictionary from aggregate_sentiment()
            
        Returns:
            MarketMood enum value
        """
        avg_score = aggregated_data.get('average_score', 0)
        variance = aggregated_data.get('variance', 0)
        total = aggregated_data.get('total_articles', 0)
        positive = aggregated_data.get('positive_count', 0)
        negative = aggregated_data.get('negative_count', 0)
        
        # Check for insufficient data
        if total < self.thresholds.MIN_ARTICLES_FOR_MOOD:
            return MarketMood.SIDEWAYS
        
        # Check for high variance (mixed signals) → Sideways
        # Sideways: when there's roughly equal positive and negative news
        if variance >= self.thresholds.SENTIMENT_VARIANCE_THRESHOLD:
            if positive > 0 and negative > 0:
                ratio = min(positive, negative) / max(positive, negative)
                if ratio >= 0.5:  # At least 50% balance between positive/negative
                    return MarketMood.SIDEWAYS
        
        # Apply threshold logic
        if avg_score >= self.thresholds.BULLISH_THRESHOLD:
            return MarketMood.BULLISH
        elif avg_score <= self.thresholds.BEARISH_THRESHOLD:
            return MarketMood.BEARISH
        else:
            return MarketMood.NEUTRAL
    
    def compute_fear_greed(self, avg_score: float) -> FearGreedLevel:
        """
        Compute Fear-Greed index based on average sentiment score
        
        Score Range → Indicator:
        - ≤ -0.40 → Extreme Fear
        - -0.40 to -0.10 → Fear
        - -0.10 to +0.10 → Neutral
        - +0.10 to +0.40 → Greed
        - ≥ +0.40 → Extreme Greed
        
        Args:
            avg_score: Average sentiment score
            
        Returns:
            FearGreedLevel enum value
        """
        if avg_score <= self.thresholds.EXTREME_FEAR_THRESHOLD:
            return FearGreedLevel.EXTREME_FEAR
        elif avg_score <= self.thresholds.FEAR_THRESHOLD:
            return FearGreedLevel.FEAR
        elif avg_score <= self.thresholds.NEUTRAL_UPPER:
            return FearGreedLevel.NEUTRAL
        elif avg_score <= self.thresholds.GREED_THRESHOLD:
            return FearGreedLevel.GREED
        else:
            return FearGreedLevel.EXTREME_GREED
    
    def extract_top_news(
        self, 
        articles: List[Dict[str, Any]], 
        count: int = 5
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract top bullish and bearish news articles
        
        Args:
            articles: List of articles with sentiment scores
            count: Number of top articles to extract (default: 5)
            
        Returns:
            Tuple of (top_bullish_news, top_bearish_news)
        """
        if not articles:
            return [], []
        
        # Sort by sentiment score
        sorted_articles = sorted(
            articles, 
            key=lambda x: x.get('sentiment_score', 0),
            reverse=True
        )
        
        # Top bullish (highest positive scores)
        top_bullish = [
            {
                'title': a['title'],
                'source': a['source'],
                'sentiment_score': a['sentiment_score'],
                'published_at': a['published_at']
            }
            for a in sorted_articles[:count]
            if a.get('sentiment_score', 0) > 0
        ]
        
        # Top bearish (lowest negative scores)
        top_bearish = [
            {
                'title': a['title'],
                'source': a['source'],
                'sentiment_score': a['sentiment_score'],
                'published_at': a['published_at']
            }
            for a in reversed(sorted_articles[-count:])
            if a.get('sentiment_score', 0) < 0
        ]
        
        return top_bullish[:count], top_bearish[:count]
    
    def generate_summary_note(
        self, 
        mood: MarketMood, 
        fear_greed: FearGreedLevel,
        aggregated_data: Dict[str, Any]
    ) -> str:
        """
        Generate a human-readable summary of market sentiment
        
        Args:
            mood: Market mood classification
            fear_greed: Fear-greed level
            aggregated_data: Aggregated sentiment statistics
            
        Returns:
            Summary note string
        """
        avg_score = aggregated_data.get('average_score', 0)
        positive = aggregated_data.get('positive_count', 0)
        negative = aggregated_data.get('negative_count', 0)
        total = aggregated_data.get('total_articles', 0)
        
        if total == 0:
            return "Insufficient data to determine market sentiment."
        
        # Determine sentiment strength
        if abs(avg_score) < 0.1:
            strength = "marginally"
        elif abs(avg_score) < 0.3:
            strength = "moderately"
        else:
            strength = "strongly"
        
        # Build note based on mood
        if mood == MarketMood.BULLISH:
            note = f"Market sentiment is {strength} bullish with {positive} positive articles out of {total}."
        elif mood == MarketMood.BEARISH:
            note = f"Market sentiment is {strength} bearish with {negative} negative articles out of {total}."
        elif mood == MarketMood.SIDEWAYS:
            note = f"Market shows mixed signals with {positive} positive and {negative} negative articles, indicating sideways movement."
        else:
            note = f"Market sentiment is neutral with balanced positive ({positive}) and negative ({negative}) coverage."
        
        # Add fear-greed context
        if fear_greed in [FearGreedLevel.EXTREME_FEAR, FearGreedLevel.EXTREME_GREED]:
            note += f" The Fear-Greed indicator shows {fear_greed.value}, suggesting extreme market conditions."
        
        return note
    
    def analyze(self, articles: List[Dict[str, Any]]) -> SentimentResult:
        """
        Perform complete sentiment analysis on articles
        
        Args:
            articles: List of articles with sentiment data
            
        Returns:
            SentimentResult dataclass with all analysis results
        """
        aggregated = self.aggregate_sentiment(articles)
        mood = self.compute_market_mood(aggregated)
        fear_greed = self.compute_fear_greed(aggregated['average_score'])
        
        return SentimentResult(
            average_score=aggregated['average_score'],
            market_mood=mood,
            fear_greed=fear_greed,
            total_articles=aggregated['total_articles'],
            positive_count=aggregated['positive_count'],
            negative_count=aggregated['negative_count'],
            neutral_count=aggregated['neutral_count'],
            sentiment_variance=aggregated['variance']
        )
