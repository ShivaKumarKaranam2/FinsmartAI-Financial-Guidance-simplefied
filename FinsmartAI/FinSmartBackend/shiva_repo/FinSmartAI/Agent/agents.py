import os
from dotenv import load_dotenv
from crewai import Agent
from crewai.llm import LLM

# Load environment variables
load_dotenv()

from tools import (
    scrape_tool,
    tavily_tool,
    calculate,
    get_company_filings,
    search_internet,
    yahoo_finance_news,
    get_marketaux_news,
    get_key_financial_ratios
)

# Configure LLM using the new Nvidia API key
llm = LLM(
    model="meta/llama-3.3-70b-instruct",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.7,
    max_tokens=4096
)


class StockAnalysisAgents():
  def financial_analyst(self):
    return Agent(
      role='The Best Financial Analyst',
      goal="""Impress all customers with your financial data 
      and market trends analysis""",
      backstory="""The most seasoned financial analyst with 
      lots of expertise in stock market analysis and investment
      strategies that is working for a super important customer.""",
      verbose=True,
      llm=llm,
      tools=[
        scrape_tool,
        tavily_tool,
        calculate,
        get_company_filings,
        get_key_financial_ratios
      ],
      allow_delegation=True
    )

  def research_analyst(self):
    return Agent(
      role='Staff Research Analyst',
      goal="""Being the best at gathering, interpreting data and amaze
      your customer with it""",
      backstory="""Known as the BEST research analyst, you're
      skilled in sifting through news, company announcements, 
      and market sentiments. Now you're working on a super 
      important customer""",
      verbose=True,
      llm=llm,
      tools=[
        scrape_tool,
        tavily_tool,
        search_internet,
        yahoo_finance_news,
        get_company_filings,
        get_marketaux_news
      ],
      allow_delegation=True
  )

  def investment_advisor(self):
    return Agent(
      role='Private Investment Advisor',
      goal="""Impress your customers with full analyses over stocks
      and completes investment recommendations""",
      backstory="""You're the most experienced investment advisor
      and you combine various analytical insights to formulate
      strategic investment advice. You are now working for
      a super important customer you need to impress.""",
      verbose=True,
      llm=llm,
      tools=[
        scrape_tool,
        tavily_tool,
        search_internet,
        calculate,
        yahoo_finance_news,
        get_marketaux_news,
        get_key_financial_ratios
      ],
      allow_delegation=False
    )
