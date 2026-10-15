"""
Document Ingestion Service for FinRAG.
Handles loading (PDF, TXT, CSV), chunking with overlap, metadata enrichment, and AstraDB persistence.
"""

import os
import datetime
import uuid
from typing import Any



from app.core.config import settings
from app.core.logging import setup_logger
from app.services.rag.vectorstore import FinRAGVectorStore

logger = setup_logger(__name__)


def ingest_file(file_obj: Any, filename: str, user_id: str, session_id: str) -> int:
    """
    Ingests, chunks, enriches with metadata, and stores document chunks into AstraDB.
    
    Args:
        file_obj: File-like object or string path
        filename: Name of the uploaded file
        user_id: User identifier for access isolation
        session_id: Session identifier for context isolation
        
    Returns:
        Number of chunks stored
    """
    logger.info(f"Ingesting {filename} for User: {user_id}, Session: {session_id}")

    # Use a secure temporary file
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tmp_ingest")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{os.path.basename(filename)}")

    try:
        # Extract content
        if isinstance(file_obj, str) and os.path.exists(file_obj):
            with open(file_obj, "rb") as f_src:
                content = f_src.read()
        elif hasattr(file_obj, "getvalue"):
            content = file_obj.getvalue()
        elif hasattr(file_obj, "read"):
            content = file_obj.read()
        else:
            raise ValueError("Unsupported file object type for ingestion")

        with open(temp_path, "wb") as f_dst:
            f_dst.write(content)

        # Select appropriate document loader
        from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        elif lower_name.endswith(".txt"):
            loader = TextLoader(temp_path, encoding="utf-8", autodetect_encoding=True)
        elif lower_name.endswith(".csv"):
            loader = CSVLoader(temp_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}. Supported formats: PDF, TXT, CSV.")

        pages = loader.load()
        logger.info(f"Loaded {len(pages)} pages from {filename}")

        # Intelligent Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.astradb.chunk_size,
            chunk_overlap=settings.astradb.chunk_overlap
        )
        chunks = text_splitter.split_documents(pages)

        # Metadata Enrichment
        timestamp = datetime.datetime.now().isoformat()
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source"] = filename
            chunk.metadata["user_id"] = user_id
            chunk.metadata["session_id"] = session_id
            chunk.metadata["upload_timestamp"] = timestamp
            if "page" not in chunk.metadata:
                chunk.metadata["page"] = "Unknown"

        logger.info(f"Created {len(chunks)} chunks with metadata.")

        # Persist to Vector Store
        vectorstore = FinRAGVectorStore()
        vectorstore.delete_user_data(user_id)
        vectorstore.add_documents(chunks)

        return len(chunks)

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_path}: {e}")
