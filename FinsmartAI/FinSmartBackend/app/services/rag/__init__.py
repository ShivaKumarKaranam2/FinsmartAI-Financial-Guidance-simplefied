"""
FinRAG Document Intelligence domain package.
Exports vectorstore, ingestion service, retriever, model factory, and prompts.
"""

from app.services.rag.vectorstore import FinRAGVectorStore
from app.services.rag.ingest_service import ingest_file
from app.services.rag.retriever import FinRAGRetriever
from app.services.rag.model_factory import get_huggingface_embeddings, get_llm
from app.services.rag.prompt_templates import (
    FINRAG_PROMPT,
    FINRAG_SYSTEM_PROMPT,
    FINRAG_USER_PROMPT,
    MAX_NEW_TOKENS,
)

__all__ = [
    "FinRAGVectorStore",
    "ingest_file",
    "FinRAGRetriever",
    "get_huggingface_embeddings",
    "get_llm",
    "FINRAG_PROMPT",
    "FINRAG_SYSTEM_PROMPT",
    "FINRAG_USER_PROMPT",
    "MAX_NEW_TOKENS",
]
