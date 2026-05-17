
from crewai import Task
from textwrap import dedent
from tools import (
    scrape_tool,
    calculate,
    get_company_filings,
    search_internet,
    yahoo_finance_news,
    get_stock_prices,
    get_company_facts,
    get_financial_metrics,
    get_financial_statements,
    get_insider_trades,
    get_institutional_ownership,
    stock_screener,
    get_media_news,
    get_key_financial_ratios
)

class StockAnalysisTasks():
  def research(self, agent):
    return Task(description=dedent(f"""
        Collect and summarize recent news articles, press
        releases, and market analyses related to the stock and
        its industry.
        Pay special attention to any significant events, market
        sentiments, and analysts' opinions. Also include upcoming 
        events like earnings and others.
  
        Your final answer MUST be a report that includes a
        comprehensive summary of the latest news, any notable
        shifts in market sentiment, and potential impacts on 
        the stock.
        Also make sure to return the stock ticker.
        
        IMPORTANT: DO NOT include a main title like "## Market Research" at the beginning of your text. Just provide the substantive content.
        
        EFFICIENCY RULES:
        - Use at most 2-3 tool calls total
        - Do NOT call search_internet more than once
        - Do NOT scrape websites, just use the search and news tools
        
        {self.__tip_section()}
  
        Make sure to use the most recent data as possible.
  
        Selected company by the customer: {{company}}
      """),
      expected_output="A comprehensive report summarizing latest news, market sentiment, and potential impacts on the stock.",
      tools=[
        search_internet,
        yahoo_finance_news,
        get_media_news,
        get_company_facts
      ],
      agent=agent
    )
    
  def financial_analysis(self, agent): 
    return Task(description=dedent(f"""
        Conduct a COMPREHENSIVE QUANTITATIVE analysis of the stock's financial health.
        
        1. **Valuation Ratios** (Focus only on the target company, provide exact numbers):
           - P/E Ratio
           - P/S Ratio (Price-to-Sales)
           - P/B Ratio (Price-to-Book)
           - EV/EBITDA
        
        2. **Profitability Metrics**:
           - Gross Margin %
           - Operating Margin %
           - Net Profit Margin %
           - ROE (Return on Equity) %
        
        3. **Growth & Health Metrics**:
           - Revenue Growth % (YoY)
           - Earnings Growth % (YoY)
           - Current Ratio
           - Debt-to-Equity Ratio
        
        Provide the data in simple, clean markdown tables for the target company ONLY. Make sure every cell in your tables contains actual data or 'N/A'.
        
        IMPORTANT RULES:
        1. DO NOT include a main title like "## Financial Analysis" at the beginning of your text. Just provide the substantive content.
        2. DO NOT prematurely assume a company is completely private without data. Search extensively for any publicly reported revenues, margins, or valuations (e.g., funding rounds, press releases). If traditional stock metics are unavailable, provide the metrics you CAN find in a clean format rather than a wall of "N/A"s.
        3. ALWAYS format markdown tables with proper newlines. Every row of the table MUST be on a new line. Do NOT output table rows on a single continuous line.
        
        EFFICIENCY RULES:
        - Use at most 3 tool calls total
        - Start with get_key_financial_ratios which gives you most data in one call
        - Only call additional tools if critical data is still missing
        
        {self.__tip_section()}

        Use the most recent quarterly and annual data.
      """),
      expected_output="A comprehensive quantitative financial analysis with detailed tables of all key metrics, ratios, growth rates, and peer comparisons.",
      tools=[
        calculate,
        get_financial_metrics,
        get_financial_statements,
        get_stock_prices,
        get_key_financial_ratios
      ],
      agent=agent
    )

  def filings_analysis(self, agent):
    return Task(description=dedent(f"""
        Analyze the latest company filings, annual reports, quarterly earnings reports, 
        and official disclosures for the stock in question. 
        Focus on key sections like Management's Discussion and
        Analysis, financial statements, insider trading activity, 
        and any disclosed risks.
        Extract relevant data and insights that could influence
        the stock's future performance.

        Your final answer must be an expanded report highlighting significant findings from these filings,
        including any red flags or positive indicators for the customer.
        
        IMPORTANT RULES:
        1. DO NOT include a main title like "## SEC Filings & Earnings Analysis" at the beginning.
        2. DO NOT use bold text like "**SEC Filings & Earnings Analysis**" for the main section title. Just write the findings normally.
        3. If the company is foreign (e.g. Indian companies on NSE/BSE) they DO NOT file with the US SEC. Do NOT state that filings are unavailable just because they aren't on EDGAR. Search for their local equivalent filings or earnings press releases instead! Only state filings are unavailable if the company is completely private with zero public financial disclosures.
        
        EFFICIENCY RULES:
        - Use at most 2 tool calls total
        - Start with get_company_filings for filings data
        - Do NOT scrape external websites

        {self.__tip_section()}        
      """),
      expected_output="An expanded report highlighting significant findings from SEC filings, including red flags and positive indicators.",
      tools=[
        get_company_filings
      ],
      agent=agent
    )

  def recommend(self, agent):
    return Task(description=dedent(f"""
        Create a DETAILED, COMPREHENSIVE PROFESSIONAL INVESTMENT REPORT with rich numerical data and analysis.
        This should be a premium-quality report worthy of a Wall Street analyst.
        
        IMPORTANT: Use the data and context from the PREVIOUS tasks (research, financial analysis, filings).
        Only make additional tool calls if absolutely critical data is missing.
        
        Your report MUST include ALL of these sections with EXACT NUMBERS and DETAILED ANALYSIS:
        
        ## 1. Executive Summary & Rating
        - Clear BUY/HOLD/SELL recommendation with confidence level
        - Current Price and Target Price (12-month) with upside/downside %
        - Risk Rating (Low/Medium/High) with justification
        - One-paragraph investment thesis summary
        
        ## 2. Company Overview
        - Brief description of what the company does
        - Key products/services and revenue segments
        - Market position and competitive advantages (moat)
        - Industry and sector classification
        
        ## 3. Valuation Summary
        
        | Metric | Current Value | Industry Avg | Assessment |
        |--------|---------------|--------------|------------|
        | P/E Ratio | X | Y | Overvalued/Fair/Undervalued |
        | P/S Ratio | X | Y | ... |
        | P/B Ratio | X | Y | ... |
        | EV/EBITDA | X | Y | ... |
        | P/FCF | X | Y | ... |
        
        ## 4. Financial Performance
        
        | Metric | Value | YoY Change |
        |--------|-------|------------|
        | Revenue | $X | +X% |
        | Net Income | $X | +X% |
        | Gross Margin | X% | +X bps |
        | Operating Margin | X% | +X bps |
        | Net Margin | X% | +X bps |
        | ROE | X% | ... |
        | ROA | X% | ... |
        
        ## 5. Financial Health Scorecard
        
        | Metric | Value | Status |
        |--------|-------|--------|
        | Current Ratio | X | Healthy/Warning/Critical |
        | Quick Ratio | X | ... |
        | Debt/Equity | X | ... |
        | Interest Coverage | X | ... |
        | Free Cash Flow | $X | ... |
        
        ## 6. Growth Analysis
        - Revenue Growth: Quarterly and Annual trends
        - Earnings Growth: Recent quarters performance
        - Provide specific numbers for recent 4 quarters if available
        - Future growth catalysts and projections
        
        ## 7. Insider Activity & Institutional Ownership
        - Recent insider buying/selling activity with amounts
        - Top institutional holders with % ownership
        - Any notable changes in institutional positions
        
        ## 8. Market Sentiment & News Impact
        - Summary of recent news sentiment (Bullish/Bearish/Neutral)
        - Key recent developments affecting the stock
        - Analyst consensus and price targets (High/Low/Mean)
        
        ## 9. Risk Assessment
        
        | Risk Factor | Impact Level | Likelihood | Details |
        |-------------|-------------|------------|---------|
        | Risk 1 | High/Med/Low | High/Med/Low | Brief description |
        | Risk 2 | ... | ... | ... |
        (List 4-6 key risks)
        
        ## 10. Investment Thesis & Recommendation
        - Detailed bull case (3-4 points with supporting data)
        - Detailed bear case (2-3 points with supporting data)
        - Final recommendation with clear reasoning
        - Suggested position sizing (conservative/moderate/aggressive)
        
        ---
        
        AFTER the report, you MUST include a data section wrapped in triple backticks with the label "chartdata".
        This data will be used for visualizations. Format it EXACTLY like this:
        
        ```chartdata
        {{{{
          "recommendation": "BUY",
          "confidence": 78,
          "currentPrice": 150.25,
          "targetPrice": 185.00,
          "riskLevel": "Medium",
          "scores": {{{{
            "valuation": 72,
            "growth": 85,
            "profitability": 80,
            "financial_health": 75,
            "momentum": 68
          }}}},
          "metrics": {{{{
            "pe_ratio": 25.4,
            "ps_ratio": 8.2,
            "pb_ratio": 12.1,
            "roe": 35.2,
            "gross_margin": 45.8,
            "operating_margin": 30.1,
            "net_margin": 25.5,
            "current_ratio": 1.8,
            "debt_equity": 1.2,
            "revenue_growth": 12.5,
            "earnings_growth": 15.3
          }}}}
        }}}}
        ```
        
        Replace all values with ACTUAL data for the company. Use reasonable estimates if exact data is unavailable.
        
        FORMATTING RULES:
        1. DO NOT include a main title like "## Investment Recommendation" at the beginning. Start with "## 1. Executive Summary & Rating".
        2. ALWAYS format markdown tables with PROPER NEWLINES. Each row MUST be on its own line. NEVER combine rows.
        3. ALWAYS use actual numbers. Do NOT use placeholders like "X" in the final output.
        4. Make the report DETAILED and COMPREHENSIVE — at least 1500 words of analysis.
        5. Use bold text for key numbers and important findings.
        6. Include specific data points, not generic statements.
        
        EFFICIENCY RULES:
        - Use at most 2-3 tool calls total
        - Most data should already be available from previous tasks
        - Do NOT re-fetch data that previous agents already gathered

        {self.__tip_section()}
      """),
      expected_output="A comprehensive, detailed professional investment report with rich tables, metrics, chart data, and data-driven recommendations in MARKDOWN format, followed by a chartdata JSON block.",
      tools=[
        calculate,
        get_key_financial_ratios,
        get_insider_trades,
        get_institutional_ownership
      ],
      agent=agent,
      output_file='new-blog-post.md'
    )

  def __tip_section(self):
    return "If you do your BEST WORK, I'll give you a ₹10,000 commission!"
