"""
Crew Service wrapper for asynchronous stock analysis orchestration.
Coordinates StockAnalysisAgents, StockAnalysisTasks, and Crew execution in a non-blocking thread pool.
"""

import sys
import os
import re
import asyncio
import logging
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Tuple, Optional, Dict

from app.core.logging import setup_logger

logger = setup_logger(__name__)

# Dedicated thread pool for crew execution (prevents blocking FastAPI event loop)
_crew_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="crew")
CREW_TIMEOUT = 300  # 5 minutes max


def _extract_chart_data(text: str) -> tuple:
    """
    Extract chartdata JSON block from the analysis text.
    
    Returns:
        tuple: (cleaned_text, chart_data_dict_or_None)
    """
    chart_data = None
    cleaned_text = text
    
    pattern = r'```chartdata\s*\n(.*?)\n\s*```'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_str = match.group(1).strip()
        try:
            chart_data = json.loads(json_str)
            logger.info(f"Successfully extracted chart data: {list(chart_data.keys())}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse chartdata JSON: {e}")
            try:
                fixed = re.sub(r',\s*}', '}', json_str)
                fixed = re.sub(r',\s*]', ']', fixed)
                chart_data = json.loads(fixed)
                logger.info("Parsed chart data after fixing JSON syntax")
            except Exception:
                logger.warning("Could not parse chart data even after syntax fix")
        
        cleaned_text = text[:match.start()].rstrip() + text[match.end():].lstrip()
    
    return cleaned_text, chart_data


def _normalize_markdown_tables(text: str) -> str:
    """
    Fix common markdown table formatting issues from LLM output.
    """
    if not text:
        return text
    
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') > 5:
            parts = re.split(r'\|\s*\|', stripped)
            if len(parts) > 2:
                rows = []
                for part in parts:
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
        
    final_result = []
    for line in result:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            chars = set(stripped.replace('|', '').replace(' ', ''))
            if chars == {'-'} or not chars:
                final_result.append(line)
                continue
                
            cells = [c.strip().upper() for c in stripped.split('|')[1:-1]]
            if any(c in ['N/A', 'NA', 'NONE', 'NULL', '-'] for c in cells):
                continue
                
        final_result.append(line)
        
    return '\n'.join(final_result)


class CrewService:
    """Service for executing stock analysis crew asynchronously."""
    
    def __init__(self):
        """Initialize agents and tasks factories lazily."""
        self._agents_factory = None
        self._tasks_factory = None

    @property
    def agents_factory(self):
        if self._agents_factory is None:
            from app.services.agents.agents import StockAnalysisAgents
            self._agents_factory = StockAnalysisAgents()
        return self._agents_factory

    @property
    def tasks_factory(self):
        if self._tasks_factory is None:
            from app.services.agents.tasks import StockAnalysisTasks
            self._tasks_factory = StockAnalysisTasks()
        return self._tasks_factory
    
    def _run_crew_sync(self, company: str) -> Any:
        """Synchronous crew execution (runs in thread pool)."""
        from crewai import Crew, Process
        financial_analyst = self.agents_factory.financial_analyst()
        research_analyst = self.agents_factory.research_analyst()
        investment_advisor = self.agents_factory.investment_advisor()
        
        research_task = self.tasks_factory.research(research_analyst)
        financial_task = self.tasks_factory.financial_analysis(financial_analyst)
        filings_task = self.tasks_factory.filings_analysis(financial_analyst)
        recommend_task = self.tasks_factory.recommend(investment_advisor)
        
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
            cache=True,
            max_rpm=100,
            share_crew=False,
            full_output=True,
            max_iter=10,
            verbose=True
        )
        
        logger.info(f"Starting crew kickoff for {company}")
        result = crew.kickoff(inputs={"company": company})
        logger.info(f"Crew kickoff completed for {company}")
        return result
    
    async def analyze_stock(self, company: str) -> dict:
        """
        Run stock analysis crew asynchronously.
        """
        try:
            import io
            if hasattr(sys.stdout, "encoding") and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
                try:
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                except Exception:
                    pass

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(_crew_executor, self._run_crew_sync, company)
            
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
            
            if not analysis_text or len(analysis_text) < 500:
                if hasattr(result, 'raw') and result.raw:
                    analysis_text = result.raw
                else:
                    analysis_text = str(result)
            
            analysis_text = _normalize_markdown_tables(analysis_text)
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
