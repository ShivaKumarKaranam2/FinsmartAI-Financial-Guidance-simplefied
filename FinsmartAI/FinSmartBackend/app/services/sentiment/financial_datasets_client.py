"""
Financial Datasets API Client
Provides access to stock prices, insider trades, and financial statements
from financialdatasets.ai
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinancialDatasetsAPIError(Exception):
    """Custom exception for Financial Datasets API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class FinancialDatasetsClient:
    """
    Client for Financial Datasets API
    Provides access to stock prices, insider trades, and financial data
    """
    
    BASE_URL = 'https://api.financialdatasets.ai'
    
    # Default tickers to track (major US stocks)
    DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META']
    
    def __init__(self, api_key: str):
        """
        Initialize the Financial Datasets API client
        
        Args:
            api_key: API key for authentication
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-KEY': api_key,
            'Accept': 'application/json',
            'User-Agent': 'MarketSentimentDashboard/2.0'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP GET request to API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            FinancialDatasetsAPIError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.info(f"Fetching from Financial Datasets: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise FinancialDatasetsAPIError("Invalid API key", status_code=401)
            elif response.status_code == 429:
                raise FinancialDatasetsAPIError("Rate limit exceeded", status_code=429)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                raise FinancialDatasetsAPIError(error_msg, status_code=response.status_code)
                
        except requests.exceptions.Timeout:
            raise FinancialDatasetsAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise FinancialDatasetsAPIError("Connection failed")
        except requests.exceptions.RequestException as e:
            raise FinancialDatasetsAPIError(f"Request error: {str(e)}")
    
    # ==================== STOCK PRICES ====================
    
    def get_price_snapshot(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time price snapshot for a single ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Price snapshot data or None if not found
        """
        try:
            data = self._make_request('/prices/snapshot', {'ticker': ticker})
            snapshot = data.get('snapshot')
            
            if snapshot:
                return {
                    'ticker': ticker,
                    'price': snapshot.get('price', 0),
                    'open': snapshot.get('open', 0),
                    'high': snapshot.get('high', 0),
                    'low': snapshot.get('low', 0),
                    'close': snapshot.get('close', 0),
                    'volume': snapshot.get('volume', 0),
                    'change': snapshot.get('change', 0),
                    'change_percent': snapshot.get('change_percent', 0),
                    'time': snapshot.get('time', '')
                }
            return None
            
        except FinancialDatasetsAPIError as e:
            logger.warning(f"Failed to get price snapshot for {ticker}: {e.message}")
            return None
    
    def get_multiple_snapshots(self, tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get price snapshots for multiple tickers
        
        Args:
            tickers: List of ticker symbols (uses default if None)
            
        Returns:
            List of price snapshot dictionaries
        """
        tickers = tickers or self.DEFAULT_TICKERS
        snapshots = []
        
        for ticker in tickers:
            snapshot = self.get_price_snapshot(ticker)
            if snapshot:
                snapshots.append(snapshot)
        
        return snapshots
    
    def get_historical_prices(
        self,
        ticker: str,
        days: int = 30,
        interval: str = 'day'
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of history
            interval: Time interval ('day', 'week', 'month')
            
        Returns:
            List of OHLCV price records
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            data = self._make_request('/prices/', {
                'ticker': ticker,
                'interval': interval,
                'interval_multiplier': 1,
                'start_date': start_date,
                'end_date': end_date,
                'limit': min(days, 5000)
            })
            
            prices = data.get('prices', [])
            return [
                {
                    'date': p.get('time', ''),
                    'open': p.get('open', 0),
                    'high': p.get('high', 0),
                    'low': p.get('low', 0),
                    'close': p.get('close', 0),
                    'volume': p.get('volume', 0)
                }
                for p in prices
            ]
            
        except FinancialDatasetsAPIError as e:
            logger.warning(f"Failed to get historical prices for {ticker}: {e.message}")
            return []
    
    # ==================== INSIDER TRADES ====================
    
    def get_insider_trades(
        self,
        ticker: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent insider trades for a ticker
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of trades to return
            
        Returns:
            List of insider trade records
        """
        try:
            data = self._make_request('/insider-trades', {
                'ticker': ticker,
                'limit': limit
            })
            
            trades = data.get('insider_trades', [])
            return [
                {
                    'ticker': ticker,
                    'insider_name': t.get('owner', 'Unknown'),
                    'insider_title': t.get('relationship', ''),
                    'transaction_type': t.get('transaction_type', ''),
                    'shares': t.get('shares', 0),
                    'price_per_share': t.get('price_per_share', 0),
                    'total_value': t.get('value', 0),
                    'filing_date': t.get('filing_date', ''),
                    'transaction_date': t.get('transaction_date', ''),
                    'is_buy': 'purchase' in str(t.get('transaction_type', '')).lower() or 
                              'buy' in str(t.get('transaction_type', '')).lower() or
                              'acquisition' in str(t.get('transaction_type', '')).lower()
                }
                for t in trades
            ]
            
        except FinancialDatasetsAPIError as e:
            logger.warning(f"Failed to get insider trades for {ticker}: {e.message}")
            return []
    
    def get_insider_trades_summary(
        self,
        ticker: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get summary of insider trading activity
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of trades to analyze
            
        Returns:
            Summary with buy/sell counts and signals
        """
        trades = self.get_insider_trades(ticker, limit)
        
        if not trades:
            return {
                'ticker': ticker,
                'total_trades': 0,
                'buy_count': 0,
                'sell_count': 0,
                'buy_value': 0,
                'sell_value': 0,
                'signal': 'Neutral',
                'signal_strength': 0
            }
        
        buys = [t for t in trades if t['is_buy']]
        sells = [t for t in trades if not t['is_buy']]
        
        buy_value = sum(t['total_value'] for t in buys if t['total_value'])
        sell_value = sum(t['total_value'] for t in sells if t['total_value'])
        
        # Calculate signal
        if len(buys) > len(sells) * 2:
            signal = 'Strong Buy'
            strength = 2
        elif len(buys) > len(sells):
            signal = 'Bullish'
            strength = 1
        elif len(sells) > len(buys) * 2:
            signal = 'Strong Sell'
            strength = -2
        elif len(sells) > len(buys):
            signal = 'Bearish'
            strength = -1
        else:
            signal = 'Neutral'
            strength = 0
        
        return {
            'ticker': ticker,
            'total_trades': len(trades),
            'buy_count': len(buys),
            'sell_count': len(sells),
            'buy_value': buy_value,
            'sell_value': sell_value,
            'signal': signal,
            'signal_strength': strength,
            'recent_trades': trades[:5]  # Most recent 5 trades
        }
    
    # ==================== FINANCIAL STATEMENTS ====================
    
    def get_income_statement(
        self,
        ticker: str,
        period: str = 'ttm'
    ) -> Optional[Dict[str, Any]]:
        """
        Get income statement data
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual', 'quarterly', or 'ttm' (trailing twelve months)
            
        Returns:
            Income statement data or None
        """
        try:
            data = self._make_request('/financials/income-statements', {
                'ticker': ticker,
                'period': period,
                'limit': 1
            })
            
            statements = data.get('income_statements', [])
            if statements:
                s = statements[0]
                return {
                    'ticker': ticker,
                    'period': period,
                    'report_period': s.get('report_period', ''),
                    'revenue': s.get('revenue', 0),
                    'gross_profit': s.get('gross_profit', 0),
                    'operating_income': s.get('operating_income', 0),
                    'net_income': s.get('net_income', 0),
                    'eps': s.get('basic_earnings_per_share', 0),
                    'gross_margin': self._calculate_margin(
                        s.get('gross_profit', 0), s.get('revenue', 0)
                    ),
                    'operating_margin': self._calculate_margin(
                        s.get('operating_income', 0), s.get('revenue', 0)
                    ),
                    'net_margin': self._calculate_margin(
                        s.get('net_income', 0), s.get('revenue', 0)
                    )
                }
            return None
            
        except FinancialDatasetsAPIError as e:
            logger.warning(f"Failed to get income statement for {ticker}: {e.message}")
            return None
    
    def _calculate_margin(self, numerator: float, denominator: float) -> float:
        """Calculate percentage margin safely"""
        if denominator and denominator != 0:
            return round((numerator / denominator) * 100, 2)
        return 0.0
    
    # ==================== COMPANY NEWS ====================
    
    def get_company_news(
        self,
        ticker: str,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get recent news for a specific company
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of articles
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            data = self._make_request('/news/', {
                'ticker': ticker,
                'start_date': start_date,
                'end_date': end_date,
                'limit': min(limit, 100)
            })
            
            news = data.get('news', [])
            return [
                {
                    'ticker': ticker,
                    'title': n.get('title', ''),
                    'description': n.get('description', ''),
                    'url': n.get('url', ''),
                    'source': n.get('source', ''),
                    'published_at': n.get('published_at', '')
                }
                for n in news
            ]
            
        except FinancialDatasetsAPIError as e:
            logger.warning(f"Failed to get news for {ticker}: {e.message}")
            return []
    
    # ==================== AGGREGATED MARKET DATA ====================
    
    def get_market_overview(
        self,
        tickers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market overview for multiple tickers
        
        Args:
            tickers: List of ticker symbols to analyze
            
        Returns:
            Complete market overview with prices, trends, and signals
        """
        tickers = tickers or self.DEFAULT_TICKERS[:5]  # Limit to 5 for performance
        
        overview = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'tickers_analyzed': len(tickers),
            'stocks': [],
            'market_trend': 'Neutral',
            'gainers': [],
            'losers': []
        }
        
        stocks_data = []
        
        for ticker in tickers:
            snapshot = self.get_price_snapshot(ticker)
            if snapshot:
                stock_info = {
                    'ticker': ticker,
                    'price': snapshot.get('price', 0),
                    'change_percent': snapshot.get('change_percent', 0),
                    'volume': snapshot.get('volume', 0)
                }
                stocks_data.append(stock_info)
        
        overview['stocks'] = stocks_data
        
        # Determine market trend
        if stocks_data:
            positive = sum(1 for s in stocks_data if s['change_percent'] > 0)
            negative = sum(1 for s in stocks_data if s['change_percent'] < 0)
            
            if positive > negative * 2:
                overview['market_trend'] = 'Bullish'
            elif negative > positive * 2:
                overview['market_trend'] = 'Bearish'
            else:
                overview['market_trend'] = 'Mixed'
            
            # Get top gainers and losers
            sorted_stocks = sorted(stocks_data, key=lambda x: x['change_percent'], reverse=True)
            overview['gainers'] = sorted_stocks[:3]
            overview['losers'] = sorted_stocks[-3:][::-1]
        
        return overview
