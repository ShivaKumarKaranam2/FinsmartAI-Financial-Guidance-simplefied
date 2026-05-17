# FinSmartAI

Professional stock analysis using AI agents powered by CrewAI and Nvidia LLMs.

## Features

- **Comprehensive Financial Analysis** - Detailed quantitative metrics (P/E, ROE, margins, growth rates)
- **AI-Powered Research** - Multi-agent system for research, analysis, and recommendations
- **Professional Reports** - Investment reports with buy/hold/sell ratings and target prices
- **REST API** - FastAPI backend for easy frontend integration
- **Real-time Data** - Integration with Yahoo Finance, Financial Datasets API, and Marketaux News

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure Environment
Create a `.env` file with your API keys:
```bash
NVIDIA_API_KEY=your_nvidia_api_key
FINANCIAL_DATASETS_API_KEY=your_fd_api_key
MARKETAUX_API_KEY=your_marketaux_key
SERPAPI_API_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_key
```

### 3. Run Analysis
```bash
uv run ./Agent/crew.py
```

### 4. Start API Server
```bash
./start_api.sh
```

Visit http://localhost:8000/docs for API documentation.

## Project Structure

```
FinSmartAI/
├── Agent/                 # AI agents and tools
│   ├── agents.py         # Agent definitions
│   ├── tasks.py          # Task specifications
│   ├── crew.py           # Crew orchestration
│   └── tools.py          # Financial data tools
├── api/                   # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── models.py         # Request/response models
│   └── crew_service.py   # Crew integration
├── pyproject.toml        # Project dependencies
└── .env                  # API keys (not in git)
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/v1/analyze` - Run stock analysis
- `GET /docs` - Interactive API documentation

## Example Usage

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"company": "INFY.NS"}
)
print(response.json()["analysis"])
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company": "INFY.NS"}'
```

## Technologies

- **AI Framework:** CrewAI, LangChain
- **LLM:** Nvidia AI (Llama 3.3 70B)
- **Financial Data:** yfinance, Financial Datasets API, Marketaux
- **Web Framework:** FastAPI
- **Package Manager:** uv

## License

MIT
