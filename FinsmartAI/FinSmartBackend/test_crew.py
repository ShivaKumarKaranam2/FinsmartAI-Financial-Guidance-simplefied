"""Quick test to see what's happening with the crew"""
import sys, os, time, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Agent'))
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("STEP 1: Testing NVIDIA API connection...")
print("=" * 60)

try:
    from crewai.llm import LLM
    llm = LLM(
        model="meta/llama-3.3-70b-instruct",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.getenv("NVIDIA_API_KEY"),
        temperature=0.5,
        max_tokens=100
    )
    start = time.time()
    response = llm.call("Say hello in one sentence.")
    elapsed = time.time() - start
    print(f"LLM Response ({elapsed:.1f}s): {response[:200]}")
except Exception as e:
    print(f"LLM ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 2: Testing tool imports...")
print("=" * 60)

try:
    from tools import (
        search_internet, yahoo_finance_news, get_media_news,
        get_company_facts, get_key_financial_ratios, get_financial_metrics,
        get_company_filings, get_insider_trades, get_institutional_ownership,
        calculate, get_marketaux_news, get_stock_prices, get_financial_statements
    )
    print("All tools imported OK")
except Exception as e:
    print(f"Tool import ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 3: Testing a quick tool call...")
print("=" * 60)

try:
    start = time.time()
    result = get_key_financial_ratios.run("AAPL")
    elapsed = time.time() - start
    print(f"get_key_financial_ratios AAPL ({elapsed:.1f}s): {str(result)[:300]}")
except Exception as e:
    print(f"Tool call ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 4: Testing agent creation...")
print("=" * 60)

try:
    from agents import StockAnalysisAgents
    from tasks import StockAnalysisTasks
    agents = StockAnalysisAgents()
    tasks = StockAnalysisTasks()
    
    fa = agents.financial_analyst()
    ra = agents.research_analyst()
    ia = agents.investment_advisor()
    print(f"Agents created OK: {fa.role}, {ra.role}, {ia.role}")
except Exception as e:
    print(f"Agent creation ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 5: Running a SINGLE task with ONE agent...")
print("=" * 60)

try:
    from crewai import Crew, Process
    
    # Just run one simple task to see if it completes
    research_task = tasks.research(ra)
    
    mini_crew = Crew(
        agents=[ra],
        tasks=[research_task],
        process=Process.sequential,
        memory=False,
        cache=True,
        max_rpm=100,
        verbose=True,
        max_iter=5  # Very limited
    )
    
    start = time.time()
    print("Starting single-task mini crew for AAPL...")
    result = mini_crew.kickoff(inputs={"company": "AAPL"})
    elapsed = time.time() - start
    
    result_text = str(result)
    print(f"\nMini crew completed in {elapsed:.1f}s")
    print(f"Result length: {len(result_text)} chars")
    print(f"Result preview: {result_text[:500]}")
    
except Exception as e:
    print(f"Mini crew ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
