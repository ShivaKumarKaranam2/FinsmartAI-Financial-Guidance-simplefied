"""
Central configuration for FinSmart AI Backend.
Adheres to Single Responsibility Principle (SRP) by centralizing environment and application settings.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple
from dotenv import load_dotenv

# Load .env file from the backend root or parent directories
load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM providers (NVIDIA NIM primary, Groq fallback)."""
    api_key: str = field(default_factory=lambda: os.getenv("NVIDIA_NIM_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    default_model: str = field(default_factory=lambda: os.getenv("NVIDIA_NIM_DEFAULT_MODEL", "meta/llama-3.2-11b-vision-instruct"))
    rag_model: str = field(default_factory=lambda: os.getenv("NVIDIA_NIM_RAG_MODEL", "meta/llama-3.2-11b-vision-instruct"))
    # Fine-tuned HuggingFace model for RAG document Q&A (primary tier)
    qa_model: str = field(default_factory=lambda: os.getenv("QA_HF_MODEL", "Shiva-k22/gemma-FinAI"))
    hf_token: str = field(default_factory=lambda: os.getenv("HF_TOKEN", ""))
    gemma_space_url: str = field(default_factory=lambda: os.getenv("GEMMA_FINAI_SPACE_URL", "https://shiva-k22-gemma-finai-demo.hf.space"))
    gemma_space_fn: str = field(default_factory=lambda: os.getenv("GEMMA_FINAI_SPACE_FN", "/bot_reply"))
    temperature: float = 0.3
    max_tokens: int = 15000


@dataclass
class AstraDBConfig:
    """Configuration for AstraDB Vector Store."""
    api_endpoint: str = field(default_factory=lambda: os.getenv("ASTRA_DB_API_ENDPOINT", ""))
    application_token: str = field(default_factory=lambda: os.getenv("ASTRA_DB_APPLICATION_TOKEN", ""))
    collection_name: str = field(default_factory=lambda: os.getenv("ASTRA_DB_COLLECTION_NAME", "finrag_nvidia_v1"))
    embedding_model: str = field(default_factory=lambda: os.getenv("ASTRA_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    hf_token: str = field(default_factory=lambda: os.getenv("HF_TOKEN", ""))
    chunk_size: int = 512
    chunk_overlap: int = 50


@dataclass
class MarketSentimentConfig:
    """Configuration for Market News and Sentiment Analysis."""
    marketaux_api_key: str = field(default_factory=lambda: os.getenv("MARKETAUX_API_KEY", ""))
    marketaux_base_url: str = "https://api.marketaux.com/v1"
    marketaux_news_endpoint: str = "/news/all"
    default_country: str = "in"
    default_language: str = "en"

    financial_datasets_api_key: str = field(default_factory=lambda: os.getenv("FINANCIAL_DATASETS_API_KEY", ""))
    fd_base_url: str = "https://api.financialdatasets.ai"
    watch_tickers: Tuple[str, ...] = ("AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN", "META")
    default_price_days: int = 30
    default_insider_limit: int = 20
    request_timeout: int = 30

    # Sentiment threshold constants
    bullish_threshold: float = 0.20
    bearish_threshold: float = -0.20
    extreme_fear_threshold: float = -0.40
    fear_threshold: float = -0.10
    neutral_upper: float = 0.10
    greed_threshold: float = 0.40
    sentiment_variance_threshold: float = 0.3
    min_articles_for_mood: int = 3


@dataclass
class AppConfig:
    """Global Application Configuration."""
    title: str = "FinSmart AI Unified Backend"
    description: str = "Unified API integrating Market Sentiment, RAG Document QA, Budget Analysis, and Portfolio AI"
    version: str = "2.0.0"
    cors_origins: list = field(default_factory=lambda: ["*"])
    upload_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"))

    llm: LLMConfig = field(default_factory=LLMConfig)
    astradb: AstraDBConfig = field(default_factory=AstraDBConfig)
    sentiment: MarketSentimentConfig = field(default_factory=MarketSentimentConfig)


settings = AppConfig()
