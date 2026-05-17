#!/usr/bin/env python
from crewai import Crew, Process
from agents import StockAnalysisAgents
from tasks import StockAnalysisTasks
import os

# Initialize Agents and Tasks
agents = StockAnalysisAgents()
tasks = StockAnalysisTasks()

# Instantiate Agents
financial_analyst_agent = agents.financial_analyst()
research_analyst_agent = agents.research_analyst()
investment_advisor_agent = agents.investment_advisor()


# Instantiate Tasks
research_task = tasks.research(research_analyst_agent)
financial_task = tasks.financial_analysis(financial_analyst_agent)
filings_task = tasks.filings_analysis(financial_analyst_agent)
recommend_task = tasks.recommend(investment_advisor_agent)

# Tasks for the Crew
tasks_list = [
    research_task,
    financial_task,
    filings_task,
    recommend_task
]

# Forming the crew
crew = Crew(
  agents=[
      financial_analyst_agent,
      research_analyst_agent,
      investment_advisor_agent
  ],
  tasks=tasks_list,
  process=Process.sequential,
  memory=False,
  cache=False,
  max_rpm=100,
  share_crew=True,
  # Context management optimizations
  embedder={
      "provider": "openai",
      "config": {
          "model": "text-embedding-3-small"
      }
  },
  full_output=False,  # Reduce output verbosity
  max_iter=15  # Limit iterations per task
)


# Start the task execution
result = crew.kickoff(inputs={"company": "Infosys.NS"})
print(result)
