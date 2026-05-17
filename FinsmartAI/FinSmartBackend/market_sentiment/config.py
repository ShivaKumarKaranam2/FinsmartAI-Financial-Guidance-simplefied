"""
Configuration module for Market Sentiment Analysis
Stores API keys, endpoints, and threshold constants
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ThresholdConfig:
    """Thresholds for sentiment classification"""
    
    # Market Mood thresholds
    BULLISH_THRESHOLD: float = 0.20
    BEARISH_THRESHOLD: float = -0.20
    
    # Fear-Greed Index thresholds
    EXTREME_FEAR_THRESHOLD: float = -0.40
    FEAR_THRESHOLD: float = -0.10
    NEUTRAL_UPPER: float = 0.10
    GREED_THRESHOLD: float = 0.40
    
    # Mixed/Sideways detection
    SENTIMENT_VARIANCE_THRESHOLD: float = 0.3  # High variance = mixed signals
    MIN_ARTICLES_FOR_MOOD: int = 3  # Minimum articles needed for valid mood


@dataclass
class FinancialDatasetsConfig:
    """Configuration for Financial Datasets API (financialdatasets.ai)"""
    
    # API Configuration
    API_KEY: str = os.getenv('FD_API_KEY')
    BASE_URL: str = 'https://api.financialdatasets.ai'
    
    # Popular tickers to track (major US stocks)
    WATCH_TICKERS: tuple = ('AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META')
    
    # Request settings
    DEFAULT_PRICE_DAYS: int = 30
    DEFAULT_INSIDER_LIMIT: int = 20
    REQUEST_TIMEOUT: int = 30


@dataclass
class Config:
    """Main configuration for Marketaux API and module settings"""
    
    # API Configuration
    API_KEY: str = os.getenv('MARKETAUX_API_KEY')
    BASE_URL: str = 'https://api.marketaux.com/v1'
    NEWS_ENDPOINT: str = '/news/all'
    
    # Default query parameters for Indian market news
    DEFAULT_COUNTRY: str = 'in'
    DEFAULT_LANGUAGE: str = 'en'
    FILTER_ENTITIES: bool = True
    DEFAULT_LIMIT: int = 20
    
    # Output settings
    TOP_NEWS_COUNT: int = 5
    
    # Thresholds
    thresholds: ThresholdConfig = None
    
    # Financial Datasets API config
    financial_datasets: FinancialDatasetsConfig = None
    
    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = ThresholdConfig()
        if self.financial_datasets is None:
            self.financial_datasets = FinancialDatasetsConfig()
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> 'Config':
        """Create config from environment or explicit API key"""
        config = cls()
        if api_key:
            config.API_KEY = api_key
        return config
