"""
Marketaux API Client
Handles all HTTP communication with the Marketaux news API
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketauxAPIError(Exception):
    """Custom exception for Marketaux API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class MarketauxClient:
    """
    Client for Marketaux API
    Fetches news articles with sentiment data for Indian markets
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Marketaux API client
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'MarketSentimentAnalyzer/1.0'
        })
    
    def fetch_news(
        self,
        limit: Optional[int] = None,
        countries: Optional[str] = None,
        language: Optional[str] = None,
        filter_entities: Optional[bool] = None,
        symbols: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Marketaux API
        
        Args:
            limit: Number of articles to fetch (default: 20)
            countries: Country filter (default: 'in' for India)
            language: Language filter (default: 'en')
            filter_entities: Whether to filter entities (default: True)
            symbols: Comma-separated stock symbols to filter
            search: Search term for articles
            
        Returns:
            List of article dictionaries with sentiment data
            
        Raises:
            MarketauxAPIError: If API request fails
        """
        # Build request parameters
        params = {
            'api_token': self.config.API_KEY,
            'countries': countries or self.config.DEFAULT_COUNTRY,
            'language': language or self.config.DEFAULT_LANGUAGE,
            'filter_entities': str(filter_entities if filter_entities is not None else self.config.FILTER_ENTITIES).lower(),
            'limit': limit or self.config.DEFAULT_LIMIT
        }
        
        # Add optional parameters
        if symbols:
            params['symbols'] = symbols
        if search:
            params['search'] = search
        
        # Construct full URL
        url = f"{self.config.BASE_URL}{self.config.NEWS_ENDPOINT}"
        
        try:
            logger.info(f"Fetching news from Marketaux API: {url}")
            response = self.session.get(url, params=params, timeout=30)
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                logger.info(f"Successfully fetched {len(articles)} articles")
                return articles
            else:
                error_data = response.json() if response.text else {}
                raise MarketauxAPIError(
                    message=f"API request failed: {error_data.get('error', {}).get('message', 'Unknown error')}",
                    status_code=response.status_code,
                    response=error_data
                )
                
        except requests.exceptions.Timeout:
            raise MarketauxAPIError("API request timed out")
        except requests.exceptions.ConnectionError:
            raise MarketauxAPIError("Failed to connect to Marketaux API")
        except requests.exceptions.RequestException as e:
            raise MarketauxAPIError(f"Request failed: {str(e)}")
    
    # Keywords that indicate bearish market sentiment regardless of entity sentiment
    BEARISH_KEYWORDS = [
        'sheds', 'shed', 'drops', 'drop', 'dropped', 'falls', 'fall', 'fell', 
        'crash', 'crashed', 'crashes', 'plunges', 'plunge', 'plunged', 'tumbles', 
        'tumble', 'tumbled', 'sinks', 'sink', 'slumps', 'slump', 'slumped',
        'decline', 'declines', 'declined', 'loses', 'lose', 'lost', 'selloff',
        'sell-off', 'bloodbath', 'correction', 'bear', 'bearish', 'downturn',
        'outflows', 'outflow', 'weakness', 'weak', 'down', 'lower', 'lows',
        'red', 'negative', 'retreat', 'retreats', 'retreated', 'dips', 'dip', 'dipped'
    ]
    
    # Keywords that indicate bullish market sentiment
    BULLISH_KEYWORDS = [
        'gains', 'gain', 'gained', 'rises', 'rise', 'rose', 'rallies', 'rally',
        'rallied', 'surges', 'surge', 'surged', 'jumps', 'jump', 'jumped',
        'soars', 'soar', 'soared', 'climbs', 'climb', 'bull', 'bullish',
        'upturn', 'inflows', 'inflow', 'strength', 'strong', 'up', 'higher',
        'highs', 'record', 'green', 'positive', 'rebounds', 'rebound', 'rebounded',
        'advances', 'advance', 'advanced', 'recovery', 'recovers', 'boom'
    ]
    
    def _adjust_sentiment_for_market_context(self, title: str, description: str, base_sentiment: float) -> float:
        """
        Adjust sentiment based on market-specific keywords in the title/description.
        The API often misinterprets market news - e.g., 'Sensex sheds 367 points' 
        might get positive entity sentiment but is clearly bearish for the market.
        
        Args:
            title: Article title
            description: Article description
            base_sentiment: Original sentiment score from API
            
        Returns:
            Adjusted sentiment score
        """
        text = f"{title} {description}".lower()
        
        bearish_count = sum(1 for keyword in self.BEARISH_KEYWORDS if keyword in text)
        bullish_count = sum(1 for keyword in self.BULLISH_KEYWORDS if keyword in text)
        
        # If there's a clear keyword signal that contradicts the base sentiment, adjust it
        if bearish_count > bullish_count:
            # Text is bearish - if base sentiment is positive, flip it
            if base_sentiment > 0:
                # Strong bearish signal: make it negative
                adjustment = -0.3 * bearish_count  # More bearish keywords = stronger adjustment
                adjusted = min(-0.15, base_sentiment + adjustment)  # Ensure it becomes negative
                return max(-1.0, adjusted)
            else:
                # Already negative, make it stronger
                return max(-1.0, base_sentiment - 0.1 * bearish_count)
        elif bullish_count > bearish_count:
            # Text is bullish - if base sentiment is negative, flip it
            if base_sentiment < 0:
                # Strong bullish signal: make it positive
                adjustment = 0.3 * bullish_count
                adjusted = max(0.15, base_sentiment + adjustment)  # Ensure it becomes positive
                return min(1.0, adjusted)
            else:
                # Already positive, make it stronger
                return min(1.0, base_sentiment + 0.1 * bullish_count)
        
        # No clear signal, return base sentiment
        return base_sentiment
    
    def get_article_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sentiment information from a single article
        
        Args:
            article: Raw article data from API
            
        Returns:
            Dictionary with title, source, sentiment_score, sentiment_label, and published_at
        """
        # Get primary sentiment from entities if available
        entities = article.get('entities', [])
        
        if entities:
            # Calculate average sentiment from all entities
            entity_sentiments = [
                e.get('sentiment_score', 0) 
                for e in entities 
                if e.get('sentiment_score') is not None
            ]
            if entity_sentiments:
                avg_sentiment = sum(entity_sentiments) / len(entity_sentiments)
            else:
                avg_sentiment = 0
        else:
            # Fallback to article-level sentiment if no entities
            avg_sentiment = article.get('sentiment_score', 0) or 0
        
        # Apply market context adjustment to fix misclassified headlines
        title = article.get('title', '')
        description = article.get('description', '')
        adjusted_sentiment = self._adjust_sentiment_for_market_context(title, description, avg_sentiment)
        
        # Determine sentiment label
        if adjusted_sentiment >= 0.1:
            sentiment_label = 'positive'
        elif adjusted_sentiment <= -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'title': article.get('title', 'No Title'),
            'source': article.get('source', 'Unknown'),
            'sentiment_score': round(adjusted_sentiment, 4),
            'sentiment_label': sentiment_label,
            'published_at': article.get('published_at', ''),
            'url': article.get('url', ''),
            'description': article.get('description', '')
        }
    
    def fetch_news_with_sentiment(
        self,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch news and extract sentiment for each article
        
        Args:
            limit: Number of articles to fetch
            **kwargs: Additional parameters for fetch_news
            
        Returns:
            List of articles with extracted sentiment data
        """
        raw_articles = self.fetch_news(limit=limit, **kwargs)
        
        processed_articles = []
        for article in raw_articles:
            sentiment_data = self.get_article_sentiment(article)
            processed_articles.append(sentiment_data)
        
        return processed_articles
