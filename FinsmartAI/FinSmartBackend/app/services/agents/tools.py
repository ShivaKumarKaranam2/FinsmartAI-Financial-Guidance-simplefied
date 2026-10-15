import os
import re
import json
import requests
from functools import lru_cache
from crewai_tools import ScrapeWebsiteTool
from crewai.tools import tool
import yfinance as yf
from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv

from app.core.logging import setup_logger

logger = setup_logger(__name__)

load_dotenv()

# Global HTTP timeout for all external API requests (seconds)
API_TIMEOUT = 10

# Initialize tools
scrape_tool = ScrapeWebsiteTool()

# Basic calculator tool
@tool("Calculator")
def calculate(operation: str):
    """Perform basic arithmetic calculations"""
    try:
        return eval(operation)
    except:
        return "Invalid calculation"

# --- COMPANY NAME / TICKER RESOLVER ---
def get_default_dates(years_back=1):
    """Default to 1 year of data (reduced from 5 for performance)"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back*365)).strftime("%Y-%m-%d")
    return start_date, end_date

def get_recent_dates(days_back=30):
    """Default to recent 30 days for news/insiders"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return start_date, end_date

def parse_financial_data(response):
    """Safely parse API responses"""
    if isinstance(response, dict):
        if 'note' in response:
            return f"Data Note: {response['note']}"
        if 'error' in response:
            return f"API Data Error: {response['error']} - {response.get('message', '')}. Proceed with qualitative analysis and alternative data."
        if 'data' in response:
            return response['data']
    return response

# Regex for valid ticker formats: AAPL, INFY.NS, BRK-B, etc.
_TICKER_RE = re.compile(r'^[A-Z]{1,5}([.-][A-Z]{1,3})?$')

# Cache resolved tickers to avoid repeated yfinance API calls
# During a single crew run the same ticker is resolved 15-30+ times
@lru_cache(maxsize=64)
def resolve_company_to_ticker(company_or_ticker: str) -> str:
    """Universal company-to-ticker resolver with caching.
    
    Skips the expensive yfinance lookup if the input already
    looks like a valid ticker symbol (e.g. AAPL, INFY.NS).
    """
    company_or_ticker = company_or_ticker.upper().strip()
    
    # If it already looks like a ticker, return immediately
    if _TICKER_RE.match(company_or_ticker):
        return company_or_ticker
    
    # Only do the expensive yfinance lookup for company names
    try:
        ticker_obj = yf.Ticker(company_or_ticker)
        info = ticker_obj.info
        if info and 'symbol' in info:
            return info['symbol']
    except:
        pass
    return company_or_ticker

# --- SEARCH & WEB TOOLS ---

@tool("Search the internet")
def search_internet(query: str):
    """Search the internet for information"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Search Error: TAVILY_API_KEY not found."
    try:
        url = "https://api.tavily.com/search"
        resp = requests.post(url, json={"api_key": api_key, "query": query, "search_depth": "basic"}, timeout=API_TIMEOUT)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return [{"title": r.get("title"), "content": r.get("content")[:500]} for r in results[:3]]
        return f"Search failed: {resp.text[:200]}"
    except Exception as e:
        return f"Search exception: {str(e)}"

@tool("Get Yahoo Finance News")
def yahoo_finance_news(ticker: str, max_results: int = 5):
    """Get latest news from Yahoo Finance (max 5 articles)"""
    ticker = resolve_company_to_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:max_results]
        # Return only essential fields to reduce context size
        simplified = []
        for n in news:
            simplified.append({
                "title": n.get("title", ""),
                "publisher": n.get("publisher", ""),
                "link": n.get("link", ""),
                "type": n.get("type", "")
            })
        return simplified
    except Exception as e:
        return f"Error fetching news: {str(e)}"

# --- CONFIGURATION ---
BASE_URL = "https://api.financialdatasets.ai"


def get_fd_headers() -> dict:
    """Dynamically get the Financial Datasets API key from environment."""
    key = os.getenv("FINANCIAL_DATASETS_API_KEY", "")
    return {"X-API-KEY": key} if key else {}


def fetch_financial_data(endpoint: str, params: dict = None) -> Any:
    """
    Safely call financialdatasets.ai with active API key, error handling, and qualitative fallbacks.
    """
    headers = get_fd_headers()
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    params = params or {}

    if not headers.get("X-API-KEY"):
        logger.warning(f"Financial Datasets API key missing for {endpoint}. Using fallback qualitative data.")
        return {"note": "Financial datasets API key missing. Using available market qualitative data."}

    logger.info(f"📊 [TOOL INPUT] financialdatasets.ai {endpoint} with params={params}")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"✅ [TOOL OUTPUT] financialdatasets.ai {endpoint} returned 200 OK")
            return data
        elif resp.status_code == 402:
            logger.warning(f"Financial Datasets credit balance is $0 (402). Falling back to qualitative data.")
            return {"note": "Financial datasets credits exhausted ($0 balance). Proceeding with qualitative financial analysis and public feeds."}
        elif resp.status_code == 401:
            logger.warning(f"Financial Datasets API key invalid (401). Falling back to qualitative data.")
            return {"note": "Financial datasets API key invalid. Proceeding with qualitative financial analysis."}
        else:
            logger.warning(f"Financial Datasets returned HTTP {resp.status_code} for {endpoint}.")
            return {"note": f"Financial datasets returned {resp.status_code}. Using qualitative market research."}
    except requests.Timeout:
        logger.warning(f"Financial Datasets {endpoint} timed out.")
        return {"error": f"Financial datasets '{endpoint}' timed out"}
    except Exception as e:
        logger.error(f"Financial Datasets {endpoint} error: {e}")
        return {"error": str(e)}


# --- FINANCIAL DATA TOOLS (REDUCED LIMITS FOR CONTEXT OPTIMIZATION) ---

@tool("Get Stock Prices")
def get_stock_prices(ticker: str, start_date: str = None, end_date: str = None):
    """Get historical stock price data (last 6 months by default)"""
    ticker = resolve_company_to_ticker(ticker)
    default_start, default_end = get_default_dates(years_back=0.5)
    if not start_date:
        start_date = default_start
    if not end_date:
        end_date = default_end
    
    params = {"ticker": ticker, "interval": "day", "start_date": start_date, "end_date": end_date}
    response = fetch_financial_data("prices", params=params)
    if isinstance(response, dict) and 'prices' in response:
        response['prices'] = response['prices'][-30:]
    return response

@tool("Get Company Facts")
def get_company_facts(ticker: str):
    """Get company profile, sector, industry, etc."""
    ticker = resolve_company_to_ticker(ticker)
    return fetch_financial_data("company/facts", params={"ticker": ticker})

@tool("Get Financial Metrics")
def get_financial_metrics(ticker: str, period: str = "quarterly", limit: int = 4):
    """Get key financial ratios (P/E, margins, ROE, etc.). Defaults to quarterly, last 4 quarters (1 year)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("financial-metrics", params={"ticker": ticker, "period": period, "limit": limit})
    return parse_financial_data(data)

@tool("Get Financial Metrics Snapshot")
def get_financial_metrics_snapshot(ticker: str):
    """Get CURRENT valuation metrics (P/E, EV/EBITDA, etc.)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("financial-metrics/snapshot", params={"ticker": ticker})
    return parse_financial_data(data)

@tool("Get Financial Statements")
def get_financial_statements(ticker: str, period: str = "quarterly", limit: int = 4):
    """Get income statement, balance sheet, cash flow. Defaults to quarterly, last 4 quarters (1 year)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("financials", params={"ticker": ticker, "period": period, "limit": limit})
    return parse_financial_data(data)

@tool("Get Segmented Revenues")
def get_segmented_revenues(ticker: str, period: str = "quarterly", limit: int = 8):
    """Get revenue by business segment (Auto/Energy for Tesla, etc.)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("financials/income-statements/segments", params={"ticker": ticker, "period": period, "limit": limit})
    return parse_financial_data(data)

@tool("Get Recent Insider Trades")
def get_insider_trades(ticker: str, limit: int = 10, filing_date_gte: str = None):
    """Get recent insider trading (defaults to last 90 days, 10 most recent)."""
    ticker = resolve_company_to_ticker(ticker)
    default_start, _ = get_recent_dates(days_back=90)
    if not filing_date_gte:
        filing_date_gte = default_start
    
    data = fetch_financial_data("insider-trades", params={"ticker": ticker, "limit": limit, "filing_date_gte": filing_date_gte})
    return parse_financial_data(data)

@tool("Get Institutional Ownership")
def get_institutional_ownership(ticker: str, limit: int = 10, report_period_gte: str = None):
    """Get top institutional holders and ownership changes (10 largest)."""
    ticker = resolve_company_to_ticker(ticker)
    default_start, _ = get_recent_dates(days_back=180)
    if not report_period_gte:
        report_period_gte = default_start
    
    data = fetch_financial_data("institutional-holdings", params={"ticker": ticker, "limit": limit, "report_period_gte": report_period_gte})
    return parse_financial_data(data)

@tool("Get Earnings Press Releases")
def get_earnings_press_releases(ticker: str, limit: int = 2):
    """Get management commentary from earnings calls (last 2 quarters)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("earnings", params={"ticker": ticker, "limit": limit})
    return parse_financial_data(data)

@tool("Get Analyst Estimates")
def get_analyst_estimates(ticker: str):
    """Get consensus price targets, revenue/EPS estimates."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("analyst-estimates", params={"ticker": ticker})
    return parse_financial_data(data)

@tool("Get Company Filings")
def get_company_filings(ticker: str, limit: int = 5):
    """Get SEC filings (5 most recent)."""
    ticker = resolve_company_to_ticker(ticker)
    data = fetch_financial_data("filings", params={"ticker": ticker, "limit": limit})
    return parse_financial_data(data)

@tool("Stock Screener")
def stock_screener(query_params: dict):
    """Screen stocks based on criteria (market cap, P/E, sector, etc.)."""
    data = fetch_financial_data("financials/search/screener/filters", params=query_params)
    return parse_financial_data(data)

@tool("Get Financial Media News")
def get_media_news(ticker: str, limit: int = 5, start_date: str = None, end_date: str = None):
    """Get recent financial news (max 10 articles)."""
    ticker = resolve_company_to_ticker(ticker)
    params = {"ticker": ticker, "limit": min(limit, 10)}
    data = fetch_financial_data("news", params=params)
    return parse_financial_data(data)


@tool("Get Marketaux News")
def get_marketaux_news(symbols: str, limit: int = 5):
    """
    Get financial news from Marketaux API for given stock symbols.
    
    Args:
        symbols (str): Stock symbols separated by comma (e.g., 'AAPL,TSLA' or 'INFY.NS')
        limit (int): Number of news articles to fetch (default: 5)
    
    Returns:
        dict: News articles with metadata
    """
    import http.client
    import urllib.parse
    
    api_token = os.getenv("MARKETAUX_API_KEY")
    if not api_token:
        return {"error": "MARKETAUX_API_KEY not found in environment variables"}
    
    try:
        conn = http.client.HTTPSConnection('api.marketaux.com', timeout=API_TIMEOUT)
        
        params = urllib.parse.urlencode({
            'api_token': api_token,
            'symbols': symbols,
            'limit': min(limit, 10),
        })
        
        conn.request('GET', '/v1/news/all?{}'.format(params))
        res = conn.getresponse()
        data = res.read()
        
        conn.close()
        
        result = json.loads(data.decode('utf-8'))
        # Trim article content to reduce context size
        if 'data' in result and isinstance(result['data'], list):
            for article in result['data']:
                if 'description' in article and article['description']:
                    article['description'] = article['description'][:300]
        return result
        
    except Exception as e:
        return {"error": f"Failed to fetch news from Marketaux: {str(e)}"}

@tool("Get Key Financial Ratios")
def get_key_financial_ratios(ticker: str):
    """
    Get comprehensive financial ratios for a stock including:
    - PE Ratio, PS Ratio, PB Ratio
    - P/FCF Ratio, EV/FCF Ratio, Debt/FCF Ratio
    - Quick Ratio, Current Ratio, Payout Ratio
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'INFY.NS')
    
    Returns:
        dict: Dictionary with all key financial ratios
    """
    ticker = resolve_company_to_ticker(ticker)
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        ratios = {
            "ticker": ticker,
            "company_name": info.get('longName', 'N/A'),
            
            # Valuation Ratios
            "pe_ratio": info.get('trailingPE') or info.get('forwardPE'),
            "ps_ratio": info.get('priceToSalesTrailing12Months'),
            "pb_ratio": info.get('priceToBook'),
            
            # Cash Flow Based Ratios
            "price_to_fcf": None,  # Will calculate
            "ev_to_fcf": None,  # Will calculate
            "debt_to_fcf": None,  # Will calculate
            
            # Liquidity Ratios
            "quick_ratio": info.get('quickRatio'),
            "current_ratio": info.get('currentRatio'),
            
            # Dividend Ratio
            "payout_ratio": info.get('payoutRatio'),
            
            # Additional useful metrics
            "market_cap": info.get('marketCap'),
            "enterprise_value": info.get('enterpriseValue'),
            "total_debt": info.get('totalDebt'),
            "free_cash_flow": info.get('freeCashflow'),
        }
        
        # Calculate P/FCF if data available
        if ratios['market_cap'] and ratios['free_cash_flow'] and ratios['free_cash_flow'] > 0:
            ratios['price_to_fcf'] = ratios['market_cap'] / ratios['free_cash_flow']
        
        # Calculate EV/FCF if data available
        if ratios['enterprise_value'] and ratios['free_cash_flow'] and ratios['free_cash_flow'] > 0:
            ratios['ev_to_fcf'] = ratios['enterprise_value'] / ratios['free_cash_flow']
        
        # Calculate Debt/FCF if data available
        if ratios['total_debt'] and ratios['free_cash_flow'] and ratios['free_cash_flow'] > 0:
            ratios['debt_to_fcf'] = ratios['total_debt'] / ratios['free_cash_flow']
        
        # Format the output
        formatted_ratios = {
            "ticker": ratios['ticker'],
            "company_name": ratios['company_name'],
            "valuation_ratios": {
                "PE_ratio": round(ratios['pe_ratio'], 2) if ratios['pe_ratio'] else None,
                "PS_ratio": round(ratios['ps_ratio'], 2) if ratios['ps_ratio'] else None,
                "PB_ratio": round(ratios['pb_ratio'], 2) if ratios['pb_ratio'] else None,
                "P_FCF_ratio": round(ratios['price_to_fcf'], 2) if ratios['price_to_fcf'] else None,
            },
            "enterprise_ratios": {
                "EV_FCF_ratio": round(ratios['ev_to_fcf'], 2) if ratios['ev_to_fcf'] else None,
                "Debt_FCF_ratio": round(ratios['debt_to_fcf'], 2) if ratios['debt_to_fcf'] else None,
            },
            "liquidity_ratios": {
                "quick_ratio": round(ratios['quick_ratio'], 2) if ratios['quick_ratio'] else None,
                "current_ratio": round(ratios['current_ratio'], 2) if ratios['current_ratio'] else None,
            },
            "dividend_ratios": {
                "payout_ratio": round(ratios['payout_ratio'], 4) if ratios['payout_ratio'] else None,
            }
        }
        
        return formatted_ratios
        
    except Exception as e:
        return {"error": f"Failed to fetch financial ratios: {str(e)}"}

# Note: Composite tool removed — individual tools are used by the crew agents directly.
