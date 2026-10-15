"""
Market News Engine & Sentiment Analysis Module
Multi-source market intelligence platform combining:
- Indian Markets news via Marketaux API
- Global stock data via Financial Datasets API
"""

from .config import Config, FinancialDatasetsConfig
from .api_client import MarketauxClient
from .sentiment_analyzer import SentimentAnalyzer
from .news_engine import MarketNewsEngine
from .financial_datasets_client import FinancialDatasetsClient
from .market_data_analyzer import MarketDataAnalyzer

__all__ = [
    'Config',
    'FinancialDatasetsConfig',
    'MarketauxClient',
    'SentimentAnalyzer',
    'MarketNewsEngine',
    'FinancialDatasetsClient',
    'MarketDataAnalyzer'
]
__version__ = '2.0.0'

