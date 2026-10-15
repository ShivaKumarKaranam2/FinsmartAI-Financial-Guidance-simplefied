import os
from dotenv import load_dotenv
from crewai import Agent
from crewai.llm import LLM

# Load environment variables
load_dotenv()

try:
    from app.services.agents.tools import (
        scrape_tool,
        calculate,
        get_company_filings,
        search_internet,
        yahoo_finance_news,
        get_marketaux_news,
        get_key_financial_ratios,
        get_media_news,
        get_financial_metrics,
        get_financial_statements,
        get_stock_prices,
        get_insider_trades,
        get_institutional_ownership
    )
except ImportError:
    from tools import (
        scrape_tool,
        calculate,
        get_company_filings,
        search_internet,
        yahoo_finance_news,
        get_marketaux_news,
        get_key_financial_ratios,
        get_media_news,
        get_financial_metrics,
        get_financial_statements,
        get_stock_prices,
        get_insider_trades,
        get_institutional_ownership
    )

# LiteLLM (used by CrewAI) requires provider prefix:
_nvidia_key = os.getenv("NVIDIA_NIM_API_KEY")
_groq_key = os.getenv("GROQ_API_KEY")

if _nvidia_key:
    _raw_model = os.getenv("NVIDIA_NIM_DEFAULT_MODEL", "meta/llama-3.2-11b-vision-instruct")
    if "deepseek" in _raw_model.lower():
        _raw_model = "meta/llama-3.2-11b-vision-instruct"
    _model = _raw_model if _raw_model.startswith("openai/") else f"openai/{_raw_model}"
    llm = LLM(
        model=_model,
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=_nvidia_key,
        temperature=0.5,
        max_tokens=4096
    )
elif _groq_key:
    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=_groq_key,
        temperature=0.7,
        max_tokens=2048
    )
else:
    raise ValueError("Neither NVIDIA_NIM_API_KEY nor GROQ_API_KEY is available for CrewAI agents.")



class StockAnalysisAgents():
  def financial_analyst(self):
    return Agent(
      role='The Best Financial Analyst',
      goal="""Analyze financial data and metrics for the target stock quickly and accurately.""",
      backstory="""You are a seasoned financial analyst who efficiently gathers 
      and analyzes financial metrics. You focus on the most important data points 
      and avoid unnecessary tool calls. Always use the ticker symbol directly.""",
      verbose=True,
      llm=llm,
      tools=[
        calculate,
        get_company_filings,
        get_key_financial_ratios,
        get_financial_metrics,
        get_financial_statements,
        get_stock_prices
      ],
      allow_delegation=False,  # CRITICAL: prevent circular delegation loops
      max_iter=3  # Per-agent iteration cap
    )

  def research_analyst(self):
    return Agent(
      role='Staff Research Analyst',
      goal="""Quickly gather the most important recent news and market sentiment for the target stock.""",
      backstory="""You are a fast and efficient research analyst. You gather 
      key news and sentiment data without over-searching. Use at most 2-3 
      tool calls to gather sufficient research data.""",
      verbose=True,
      llm=llm,
      tools=[
        search_internet,
        yahoo_finance_news,
        get_media_news,
        get_marketaux_news
      ],
      allow_delegation=False,  # CRITICAL: prevent circular delegation loops
      max_iter=3  # Per-agent iteration cap
  )

  def investment_advisor(self):
    return Agent(
      role='Private Investment Advisor',
      goal="""Synthesize all research and financial analysis into a clear, 
      data-driven investment recommendation. Use the data already gathered 
      by other agents rather than making redundant API calls.""",
      backstory="""You're an experienced investment advisor who creates 
      concise, actionable investment reports. You rely primarily on the 
      context from previous tasks and only make minimal additional tool 
      calls if critical data is missing.""",
      verbose=True,
      llm=llm,
      tools=[
        calculate,
        get_key_financial_ratios,
        get_insider_trades,
        get_institutional_ownership
      ],
      allow_delegation=False,
      max_iter=3  # Per-agent iteration cap
    )
