"""Crew service wrapper for stock analysis"""
import sys
import os
from datetime import datetime

# Add Agent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agent'))

from agents import StockAnalysisAgents
from tasks import StockAnalysisTasks
from crewai import Crew, Process


class CrewService:
    """Service for executing stock analysis crew"""
    
    def __init__(self):
        """Initialize agents and tasks"""
        self.agents = StockAnalysisAgents()
        self.tasks = StockAnalysisTasks()
        
        # Initialize agents
        self.financial_analyst = self.agents.financial_analyst()
        self.research_analyst = self.agents.research_analyst()
        self.investment_advisor = self.agents.investment_advisor()
    
    async def analyze_stock(self, company: str) -> dict:
        """
        Run stock analysis crew
        
        Args:
            company: Stock ticker symbol
            
        Returns:
            dict with analysis results
        """
        try:
            # Create tasks
            research_task = self.tasks.research(self.research_analyst)
            financial_task = self.tasks.financial_analysis(self.financial_analyst)
            filings_task = self.tasks.filings_analysis(self.financial_analyst)
            recommend_task = self.tasks.recommend(self.investment_advisor)
            
            # Create crew
            crew = Crew(
                agents=[
                    self.financial_analyst,
                    self.research_analyst,
                    self.investment_advisor
                ],
                tasks=[
                    research_task,
                    financial_task,
                    filings_task,
                    recommend_task
                ],
                process=Process.sequential,
                memory=False,
                cache=False,
                max_rpm=100,
                share_crew=True,
                full_output=False,
                max_iter=15
            )
            
            # Execute crew
            result = crew.kickoff(inputs={"company": company})
            
            return {
                "status": "success",
                "company": company,
                "analysis": str(result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "company": company,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
