import os
import json
import requests
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain.tools import tool
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize tools
scrape_tool = ScrapeWebsiteTool()
tavily_tool = SerperDevTool()

# Basic calculator tool
@tool("Calculator")
def calculate(operation: str):
    """Perform basic arithmetic calculations"""
    try:
        return eval(operation)
    except:
        return "Invalid calculation"

# --- COMPANY NAME / TICKER RESOLVER ---
def get_default_dates(years_back=5):
    """Default to 5 years of data for most analyses"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back*365)).strftime("%Y-%m-%d")
    return start_date, end_date

def get_recent_dates(days_back=90):
    """Default to recent 90 days for news/insiders"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return start_date, end_date

def parse_financial_data(response):
    """Safely parse API responses"""
    if isinstance(response, dict) and 'data' in response:
        return response['data']
    return response

def resolve_company_to_ticker(company_or_ticker: str) -> str:
    """Universal company-to-ticker resolver"""
    company_or_ticker = company_or_ticker.upper().strip()
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
    return tavily_tool.run(query)

@tool("Get Yahoo Finance News")
def yahoo_finance_news(ticker: str, max_results: int = 10):
    """Get latest news from Yahoo Finance"""
    ticker = resolve_company_to_ticker(ticker)
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:max_results]
        return news
    except Exception as e:
        return f"Error fetching news: {str(e)}"

# --- CONFIGURATION ---
API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY")
HEADERS = {"X-API-KEY": API_KEY}
BASE_URL = "https://api.financialdatasets.ai"

# --- FINANCIAL DATA TOOLS (REDUCED LIMITS FOR CONTEXT OPTIMIZATION) ---

@tool("Get Stock Prices")
def get_stock_prices(ticker: str, start_date: str = None, end_date: str = None):
    """Get historical stock price data"""
    ticker = resolve_company_to_ticker(ticker)
    default_start, default_end = get_default_dates()
    if not start_date:
        start_date = default_start
    if not end_date:
        end_date = default_end
    
    url = f"{BASE_URL}/prices"
    params = {"ticker": ticker, "start_date": start_date, "end_date": end_date}
    response = requests.get(url, headers=HEADERS, params=params).json()
    return response

@tool("Get Company Facts")
def get_company_facts(ticker: str):
    """Get company profile, sector, industry, etc."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/company-facts"
    params = {"ticker": ticker}
    response = requests.get(url, headers=HEADERS, params=params).json()
    return response

@tool("Get Financial Metrics")
def get_financial_metrics(ticker: str, period: str = "quarterly", limit: int = 8):
    """Get key financial ratios (P/E, margins, ROE, etc.). Defaults to quarterly, last 8 quarters (2 years)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/financial-metrics"
    params = {"ticker": ticker, "period": period, "limit": limit}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Financial Metrics Snapshot")
def get_financial_metrics_snapshot(ticker: str):
    """Get CURRENT valuation metrics (P/E, EV/EBITDA, etc.)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/financial-metrics/snapshot"
    params = {"ticker": ticker}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Financial Statements")
def get_financial_statements(ticker: str, period: str = "quarterly", limit: int = 8):
    """Get income statement, balance sheet, cash flow. Defaults to quarterly, last 8 quarters (2 years)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/financials"
    params = {"ticker": ticker, "period": period, "limit": limit}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Segmented Revenues")
def get_segmented_revenues(ticker: str, period: str = "quarterly", limit: int = 20):
    """Get revenue by business segment (Auto/Energy for Tesla, etc.)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/segmented-revenue"
    params = {"ticker": ticker, "period": period, "limit": limit}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Recent Insider Trades")
def get_insider_trades(ticker: str, limit: int = 20, filing_date_gte: str = None):
    """Get recent insider trading (defaults to last year, 20 most recent)."""
    ticker = resolve_company_to_ticker(ticker)
    default_start, _ = get_recent_dates(days_back=365)
    if not filing_date_gte:
        filing_date_gte = default_start
    
    url = f"{BASE_URL}/insider-trades"
    params = {"ticker": ticker, "limit": limit, "filing_date_gte": filing_date_gte}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Institutional Ownership")
def get_institutional_ownership(ticker: str, limit: int = 20, report_period_gte: str = None):
    """Get top institutional holders and ownership changes (20 largest)."""
    ticker = resolve_company_to_ticker(ticker)
    default_start, _ = get_recent_dates(days_back=365)
    if not report_period_gte:
        report_period_gte = default_start
    
    url = f"{BASE_URL}/institutional-ownership"
    params = {"ticker": ticker, "limit": limit, "report_period_gte": report_period_gte}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Earnings Press Releases")
def get_earnings_press_releases(ticker: str, limit: int = 4):
    """Get management commentary from earnings calls (last 4 quarters)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/earnings/press-releases"
    params = {"ticker": ticker, "limit": limit}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Analyst Estimates")
def get_analyst_estimates(ticker: str):
    """Get consensus price targets, revenue/EPS estimates."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/analyst-estimates"
    params = {"ticker": ticker}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Company Filings")
def get_company_filings(ticker: str, limit: int = 10):
    """Get SEC filings (10 most recent)."""
    ticker = resolve_company_to_ticker(ticker)
    url = f"{BASE_URL}/filings"
    params = {"ticker": ticker, "limit": limit}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Stock Screener")
def stock_screener(query_params: dict):
    """Screen stocks based on criteria (market cap, P/E, sector, etc.)."""
    url = f"{BASE_URL}/screener"
    return requests.get(url, headers=HEADERS, params=query_params).json()

@tool("Get Financial Media News")
def get_media_news(ticker: str, limit: int = 10, start_date: str = None, end_date: str = None):
    """Get recent financial news (defaults to 30 days, 10 articles)."""
    ticker = resolve_company_to_ticker(ticker)
    default_start, default_end = get_recent_dates(days_back=30)
    if not start_date:
        start_date = default_start
    if not end_date:
        end_date = default_end
    
    url = f"{BASE_URL}/news"
    params = {"ticker": ticker, "limit": limit, "start_date": start_date, "end_date": end_date}
    return requests.get(url, headers=HEADERS, params=params).json()

@tool("Get Marketaux News")
def get_marketaux_news(symbols: str, limit: int = 10):
    """
    Get financial news from Marketaux API for given stock symbols.
    
    Args:
        symbols (str): Stock symbols separated by comma (e.g., 'AAPL,TSLA' or 'INFY.NS')
        limit (int): Number of news articles to fetch (default: 10, max: 50)
    
    Returns:
        dict: News articles with metadata
    """
    import http.client
    import urllib.parse
    
    api_token = os.getenv("MARKETAUX_API_KEY")
    if not api_token:
        return {"error": "MARKETAUX_API_KEY not found in environment variables"}
    
    try:
        conn = http.client.HTTPSConnection('api.marketaux.com')
        
        params = urllib.parse.urlencode({
            'api_token': api_token,
            'symbols': symbols,
            'limit': min(limit, 50),  # Cap at 50
        })
        
        conn.request('GET', '/v1/news/all?{}'.format(params))
        res = conn.getresponse()
        data = res.read()
        
        conn.close()
        
        # Parse JSON response
        import json
        return json.loads(data.decode('utf-8'))
        
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
        
        # Get financials for calculated ratios
        try:
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow
            income_stmt = stock.income_stmt
        except:
            balance_sheet = None
            cashflow = None
            income_stmt = None
        
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

# --- UNIVERSAL COMPOSITE TOOL (WORKS FOR ANY COMPANY) ---

@tool("Get Complete Stock Analysis")
def get_complete_stock_analysis(company_or_ticker: str, years_back: int = 3, recent_days: int = 90):
    """
    COMPLETE investment analysis for ANY company:
    - Financials (quarterly/annual)
    - Valuation metrics
    - Insider trades (recent)
    - News (recent 90 days)
    - Institutional ownership
    """
    ticker = resolve_company_to_ticker(company_or_ticker)
    
    # Safe API caller
    def safe_call(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {"error": str(e)}
    
    # Gather all data
    data = {
        "ticker": ticker,
        "company_facts": safe_call(get_company_facts, ticker),
        "financial_metrics": safe_call(get_financial_metrics, ticker, period="quarterly", limit=12),
        "financial_statements": safe_call(get_financial_statements, ticker, period="quarterly", limit=8),
        "insider_trades": safe_call(get_insider_trades, ticker, limit=20),
        "institutional_ownership": safe_call(get_institutional_ownership, ticker, limit=20),
        "recent_news": safe_call(get_media_news, ticker, limit=10),
        "analyst_estimates": safe_call(get_analyst_estimates, ticker),
    }
    
    return data
