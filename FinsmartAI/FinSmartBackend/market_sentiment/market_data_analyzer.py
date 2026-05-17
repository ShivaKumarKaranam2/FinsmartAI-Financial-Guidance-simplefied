"""
Market Data Analyzer
Analyzes stock price trends, insider trading signals, and market health
Integrates with Financial Datasets API data
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PriceTrend(Enum):
    """Price trend classification"""
    STRONG_UP = "Strong Uptrend"
    UP = "Uptrend"
    NEUTRAL = "Neutral"
    DOWN = "Downtrend"
    STRONG_DOWN = "Strong Downtrend"


class InsiderSignal(Enum):
    """Insider trading signal classification"""
    STRONG_BUY = "Strong Buy Signal"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    STRONG_SELL = "Strong Sell Signal"


class MarketHealthLevel(Enum):
    """Overall market health classification"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    CRITICAL = "Critical"


@dataclass
class StockAnalysis:
    """Container for individual stock analysis results"""
    ticker: str
    price: float
    change_percent: float
    price_trend: PriceTrend
    insider_signal: InsiderSignal
    overall_score: float  # -100 to +100
    recommendation: str


class MarketDataAnalyzer:
    """
    Analyzes market data from Financial Datasets API
    Computes price trends, insider signals, and market health
    """
    
    # Thresholds for price trend classification
    STRONG_TREND_THRESHOLD = 5.0  # 5% change = strong trend
    TREND_THRESHOLD = 1.5  # 1.5% change = trend
    
    def __init__(self):
        """Initialize the market data analyzer"""
        pass
    
    # ==================== PRICE ANALYSIS ====================
    
    def analyze_price_change(self, change_percent: float) -> PriceTrend:
        """
        Determine price trend based on change percentage
        
        Args:
            change_percent: Percentage price change
            
        Returns:
            PriceTrend enum value
        """
        if change_percent >= self.STRONG_TREND_THRESHOLD:
            return PriceTrend.STRONG_UP
        elif change_percent >= self.TREND_THRESHOLD:
            return PriceTrend.UP
        elif change_percent <= -self.STRONG_TREND_THRESHOLD:
            return PriceTrend.STRONG_DOWN
        elif change_percent <= -self.TREND_THRESHOLD:
            return PriceTrend.DOWN
        else:
            return PriceTrend.NEUTRAL
    
    def analyze_historical_prices(
        self,
        prices: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze historical price data for trends
        
        Args:
            prices: List of OHLCV price records
            
        Returns:
            Analysis results with trend info
        """
        if not prices or len(prices) < 2:
            return {
                'trend': PriceTrend.NEUTRAL.value,
                'momentum': 0,
                'volatility': 0,
                'avg_volume': 0
            }
        
        # Calculate price momentum
        closes = [p.get('close', 0) for p in prices if p.get('close')]
        if len(closes) >= 2:
            first_half_avg = sum(closes[:len(closes)//2]) / (len(closes)//2)
            second_half_avg = sum(closes[len(closes)//2:]) / (len(closes) - len(closes)//2)
            momentum = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg else 0
        else:
            momentum = 0
        
        # Calculate volatility (simplified as range / average)
        if closes:
            avg_price = sum(closes) / len(closes)
            price_range = max(closes) - min(closes)
            volatility = (price_range / avg_price * 100) if avg_price else 0
        else:
            volatility = 0
        
        # Calculate average volume
        volumes = [p.get('volume', 0) for p in prices if p.get('volume')]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        
        # Determine trend
        if momentum >= 5:
            trend = PriceTrend.STRONG_UP
        elif momentum >= 2:
            trend = PriceTrend.UP
        elif momentum <= -5:
            trend = PriceTrend.STRONG_DOWN
        elif momentum <= -2:
            trend = PriceTrend.DOWN
        else:
            trend = PriceTrend.NEUTRAL
        
        return {
            'trend': trend.value,
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 2),
            'avg_volume': int(avg_volume)
        }
    
    # ==================== INSIDER TRADING ANALYSIS ====================
    
    def analyze_insider_activity(
        self,
        summary: Dict[str, Any]
    ) -> InsiderSignal:
        """
        Analyze insider trading activity to generate signal
        
        Args:
            summary: Insider trades summary from API client
            
        Returns:
            InsiderSignal enum value
        """
        signal_strength = summary.get('signal_strength', 0)
        signal_text = summary.get('signal', 'Neutral')
        
        if signal_strength >= 2:
            return InsiderSignal.STRONG_BUY
        elif signal_strength >= 1:
            return InsiderSignal.BULLISH
        elif signal_strength <= -2:
            return InsiderSignal.STRONG_SELL
        elif signal_strength <= -1:
            return InsiderSignal.BEARISH
        else:
            return InsiderSignal.NEUTRAL
    
    def get_insider_signal_score(self, signal: InsiderSignal) -> float:
        """Convert insider signal to numeric score (-50 to +50)"""
        scores = {
            InsiderSignal.STRONG_BUY: 50,
            InsiderSignal.BULLISH: 25,
            InsiderSignal.NEUTRAL: 0,
            InsiderSignal.BEARISH: -25,
            InsiderSignal.STRONG_SELL: -50
        }
        return scores.get(signal, 0)
    
    # ==================== COMBINED ANALYSIS ====================
    
    def analyze_stock(
        self,
        snapshot: Dict[str, Any],
        insider_summary: Optional[Dict[str, Any]] = None,
        historical_prices: Optional[List[Dict]] = None
    ) -> StockAnalysis:
        """
        Perform complete analysis on a single stock
        
        Args:
            snapshot: Current price snapshot
            insider_summary: Insider trading summary
            historical_prices: Historical price data
            
        Returns:
            StockAnalysis dataclass with complete results
        """
        ticker = snapshot.get('ticker', 'UNKNOWN')
        price = snapshot.get('price', 0)
        change_percent = snapshot.get('change_percent', 0)
        
        # Price trend from daily change
        price_trend = self.analyze_price_change(change_percent)
        
        # Insider signal
        if insider_summary:
            insider_signal = self.analyze_insider_activity(insider_summary)
        else:
            insider_signal = InsiderSignal.NEUTRAL
        
        # Calculate overall score (-100 to +100)
        # Price contributes up to 50 points, insider contributes up to 50 points
        price_score = min(50, max(-50, change_percent * 10))  # 5% = 50 points
        insider_score = self.get_insider_signal_score(insider_signal)
        overall_score = price_score + insider_score
        
        # Generate recommendation
        if overall_score >= 50:
            recommendation = "Strong Buy - Bullish price action with positive insider activity"
        elif overall_score >= 20:
            recommendation = "Moderate Buy - Positive signals detected"
        elif overall_score >= -20:
            recommendation = "Hold - Mixed signals, wait for clearer direction"
        elif overall_score >= -50:
            recommendation = "Moderate Sell - Bearish signals present"
        else:
            recommendation = "Strong Sell - Bearish price action with negative insider activity"
        
        return StockAnalysis(
            ticker=ticker,
            price=price,
            change_percent=change_percent,
            price_trend=price_trend,
            insider_signal=insider_signal,
            overall_score=round(overall_score, 1),
            recommendation=recommendation
        )
    
    # ==================== MARKET HEALTH ====================
    
    def analyze_market_health(
        self,
        stocks: List[Dict[str, Any]],
        news_sentiment_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze overall market health from multiple stocks
        
        Args:
            stocks: List of stock data with price changes
            news_sentiment_score: Average news sentiment score (-1 to +1)
            
        Returns:
            Market health analysis results
        """
        if not stocks:
            return {
                'health_level': MarketHealthLevel.FAIR.value,
                'health_score': 50,
                'gainers_count': 0,
                'losers_count': 0,
                'average_change': 0,
                'summary': 'Insufficient data for market health analysis'
            }
        
        # Count gainers and losers
        changes = [s.get('change_percent', 0) for s in stocks]
        gainers = sum(1 for c in changes if c > 0)
        losers = sum(1 for c in changes if c < 0)
        unchanged = len(changes) - gainers - losers
        
        # Calculate average change
        avg_change = sum(changes) / len(changes)
        
        # Calculate health score (0-100)
        base_score = 50 + (avg_change * 5)  # 1% avg change = 5 points
        
        # Add breadth component (positive if more gainers than losers)
        if len(stocks) > 0:
            breadth = ((gainers - losers) / len(stocks)) * 20
            base_score += breadth
        
        # Add sentiment component if available
        if news_sentiment_score is not None:
            sentiment_contribution = news_sentiment_score * 15  # Max +/- 15 points
            base_score += sentiment_contribution
        
        # Clamp to 0-100
        health_score = max(0, min(100, base_score))
        
        # Determine health level
        if health_score >= 80:
            health_level = MarketHealthLevel.EXCELLENT
            summary = f"Market is showing excellent health with {gainers} gainers. Average change: {avg_change:+.2f}%"
        elif health_score >= 60:
            health_level = MarketHealthLevel.GOOD
            summary = f"Market is healthy with {gainers} gainers vs {losers} losers. Average change: {avg_change:+.2f}%"
        elif health_score >= 40:
            health_level = MarketHealthLevel.FAIR
            summary = f"Market shows mixed signals with {gainers} gainers and {losers} losers."
        elif health_score >= 20:
            health_level = MarketHealthLevel.POOR
            summary = f"Market is under pressure with {losers} stocks declining. Average change: {avg_change:+.2f}%"
        else:
            health_level = MarketHealthLevel.CRITICAL
            summary = f"Market is in distress with {losers} losers. Average change: {avg_change:+.2f}%"
        
        return {
            'health_level': health_level.value,
            'health_score': round(health_score, 1),
            'gainers_count': gainers,
            'losers_count': losers,
            'unchanged_count': unchanged,
            'average_change': round(avg_change, 2),
            'summary': summary
        }
    
    # ==================== FORMATTING HELPERS ====================
    
    @staticmethod
    def format_price(price: float) -> str:
        """Format price for display"""
        if price >= 1000:
            return f"${price:,.2f}"
        return f"${price:.2f}"
    
    @staticmethod
    def format_change(change_percent: float) -> str:
        """Format percentage change with color indicator"""
        if change_percent > 0:
            return f"+{change_percent:.2f}%"
        return f"{change_percent:.2f}%"
    
    @staticmethod
    def format_volume(volume: int) -> str:
        """Format volume with K/M/B suffix"""
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.1f}K"
        return str(volume)
    
    @staticmethod
    def get_trend_emoji(trend: PriceTrend) -> str:
        """Get emoji for price trend"""
        emojis = {
            PriceTrend.STRONG_UP: "🚀",
            PriceTrend.UP: "📈",
            PriceTrend.NEUTRAL: "➡️",
            PriceTrend.DOWN: "📉",
            PriceTrend.STRONG_DOWN: "💥"
        }
        return emojis.get(trend, "📊")
    
    @staticmethod
    def get_signal_emoji(signal: InsiderSignal) -> str:
        """Get emoji for insider signal"""
        emojis = {
            InsiderSignal.STRONG_BUY: "🟢",
            InsiderSignal.BULLISH: "🔵",
            InsiderSignal.NEUTRAL: "⚪",
            InsiderSignal.BEARISH: "🟡",
            InsiderSignal.STRONG_SELL: "🔴"
        }
        return emojis.get(signal, "⚪")
