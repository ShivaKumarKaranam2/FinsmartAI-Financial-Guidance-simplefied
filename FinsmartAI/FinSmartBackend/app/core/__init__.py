"""
Core package for FinSmart AI Backend: configuration, logging, and LLM providers.
"""

from app.core.config import settings, AppConfig
from app.core.logging import setup_logger
from app.core.llm_provider import call_llm, get_llm_client, load_model

__all__ = [
    "settings",
    "AppConfig",
    "setup_logger",
    "call_llm",
    "get_llm_client",
    "load_model",
]
