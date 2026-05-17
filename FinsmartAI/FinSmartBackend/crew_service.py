"""Crew service wrapper for stock analysis"""
import sys
import os
import re
import asyncio
import logging
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Add Agent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Agent'))

from agents import StockAnalysisAgents
from tasks import StockAnalysisTasks
from crewai import Crew, Process

# Dedicated thread pool for crew execution (prevents blocking the event loop)
_crew_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="crew")

# Maximum time to wait for crew analysis (seconds)
CREW_TIMEOUT = 300  # 5 minutes max


def _extract_chart_data(text: str) -> tuple:
    """Extract chartdata JSON block from the analysis text.
    
    Returns:
        tuple: (cleaned_text, chart_data_dict_or_None)
    """
    chart_data = None
    cleaned_text = text
    
    # Look for ```chartdata ... ``` block
    pattern = r'```chartdata\s*\n(.*?)\n\s*```'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_str = match.group(1).strip()
        try:
            chart_data = json.loads(json_str)
            logger.info(f"Successfully extracted chart data: {list(chart_data.keys())}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse chartdata JSON: {e}")
            # Try to fix common JSON issues (trailing commas, etc.)
            try:
                # Remove trailing commas before closing braces
                fixed = re.sub(r',\s*}', '}', json_str)
                fixed = re.sub(r',\s*]', ']', fixed)
                chart_data = json.loads(fixed)
                logger.info("Parsed chart data after fixing JSON")
            except:
                logger.warning("Could not parse chart data even after fixing")
        
        # Remove the chartdata block from the analysis text
        cleaned_text = text[:match.start()].rstrip() + text[match.end():].lstrip()
    
    return cleaned_text, chart_data


def _normalize_markdown_tables(text: str) -> str:
    """Fix common markdown table formatting issues from LLM output.
    
    - Ensures table rows are on separate lines
    - Fixes missing separator rows
    - Normalizes pipe alignment
    """
    if not text:
        return text
    
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        # A concatenated table line: starts & ends with |, has many pipes
        if stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') > 5:
            # Split on the pattern where a row ends and another begins: "| |"
            # We look for | followed by whitespace then | (without content between)
            parts = re.split(r'\|\s*\|', stripped)
            if len(parts) > 2:
                rows = []
                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:
                        continue
                    if not part.startswith('|'):
                        part = '| ' + part
                    if not part.endswith('|'):
                        part = part + ' |'
                    rows.append(part)
                if len(rows) > 1:
                    result.extend(rows)
                    continue
        result.append(line)
        
    # Second pass: remove rows where any cell is "N/A"
    final_result = []
    for line in result:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            # Don't filter out markdown separator rows like |---|---|
            chars = set(stripped.replace('|', '').replace(' ', ''))
            if chars == {'-'} or not chars:
                final_result.append(line)
                continue
                
            cells = [c.strip().upper() for c in stripped.split('|')[1:-1]]
            if any(c in ['N/A', 'NA', 'NONE', 'NULL', '-'] for c in cells):
                continue  # Skip this row entirely
                
        final_result.append(line)
        
    return '\n'.join(final_result)


class CrewService:
    """Service for executing stock analysis crew"""
    
    def __init__(self):
        """Initialize agents and tasks factories"""
        self.agents_factory = StockAnalysisAgents()
        self.tasks_factory = StockAnalysisTasks()
    
    def _run_crew_sync(self, company: str) -> dict:
        """Synchronous crew execution (runs in thread pool)"""
        # Create FRESH agents and tasks for each run to avoid state leakage
        financial_analyst = self.agents_factory.financial_analyst()
        research_analyst = self.agents_factory.research_analyst()
        investment_advisor = self.agents_factory.investment_advisor()
        
        research_task = self.tasks_factory.research(research_analyst)
        financial_task = self.tasks_factory.financial_analysis(financial_analyst)
        filings_task = self.tasks_factory.filings_analysis(financial_analyst)
        recommend_task = self.tasks_factory.recommend(investment_advisor)
        
        # Create crew with optimized settings
        crew = Crew(
            agents=[
                financial_analyst,
                research_analyst,
                investment_advisor
            ],
            tasks=[
                research_task,
                financial_task,
                filings_task,
                recommend_task
            ],
            process=Process.sequential,
            memory=False,
            cache=True,  # Enable caching to avoid duplicate tool calls within the run
            max_rpm=100,
            share_crew=False,
            full_output=True,
            max_iter=10,  # Reduced from 15 — prevent runaway iterations
            verbose=True
        )
        
        logger.info(f"Starting crew kickoff for {company}")
        result = crew.kickoff(inputs={"company": company})
        logger.info(f"Crew kickoff completed for {company}")
        return result
    
    async def analyze_stock(self, company: str) -> dict:
        """
        Run stock analysis crew without timeout protection as requested
        """
        try:
            # Fix windows console UnicodeEncodeError for emojis during crew execution
            import sys
            import io
            if sys.stdout.encoding.lower() != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

            loop = asyncio.get_event_loop()
            
            # Run crew in thread pool without timeout
            result = await loop.run_in_executor(_crew_executor, self._run_crew_sync, company)
            
            # Build the full report from ALL task outputs
            analysis_text = ""
            section_names = [
                "Market Research & News Analysis",
                "Financial Analysis & Metrics",
                "SEC Filings & Earnings Analysis",
                "Investment Recommendation"
            ]
            
            if hasattr(result, 'tasks_output') and result.tasks_output:
                sections = []
                for i, task_output in enumerate(result.tasks_output):
                    task_raw = ""
                    if hasattr(task_output, 'raw') and task_output.raw:
                        task_raw = task_output.raw
                    elif hasattr(task_output, 'output') and task_output.output:
                        task_raw = task_output.output
                    else:
                        task_raw = str(task_output)
                    
                    if task_raw and len(task_raw.strip()) > 50:
                        header = section_names[i] if i < len(section_names) else f"Section {i+1}"
                        sections.append(f"## {header}\n\n{task_raw.strip()}")
                
                if sections:
                    analysis_text = f"# Investment Report: {company}\n\n" + "\n\n---\n\n".join(sections)
            
            # Fallback to single .raw output if tasks_output didn't work
            if not analysis_text or len(analysis_text) < 500:
                if hasattr(result, 'raw') and result.raw:
                    analysis_text = result.raw
                else:
                    analysis_text = str(result)
            
            # Normalize markdown tables to fix formatting issues
            analysis_text = _normalize_markdown_tables(analysis_text)
            
            # Extract chart data from the analysis
            analysis_text, chart_data = _extract_chart_data(analysis_text)
                
            logger.info(f"Final analysis length: {len(analysis_text)} chars, chart_data: {'yes' if chart_data else 'no'}")
            
            response = {
                "status": "success",
                "company": company,
                "analysis": analysis_text,
                "timestamp": datetime.now().isoformat()
            }
            
            if chart_data:
                response["chart_data"] = chart_data
            
            return response
            
        except Exception as e:
            logger.error(f"Stock analysis failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "company": company,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

