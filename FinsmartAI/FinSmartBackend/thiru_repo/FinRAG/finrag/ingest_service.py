import os
import datetime
import uuid
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from finrag.astradb_vectorstore import FinRAGVectorStore
from config import CHUNK_SIZE, CHUNK_OVERLAP

def ingest_file(file_obj, filename: str, user_id: str, session_id: str) -> int:
    """
    Implements Step 1 (Ingestion) & Step 2 (Chunking) & Step 3 (Metadata).
    Also triggers Step 12 (Cleanup).
    """
    print(f"Ingesting {filename} for Session: {session_id}")
    
    # 1. Save temp file
    temp_path = f"temp_{filename}"
    
    # Check if file_obj is a path (str) or a file-like object
    if isinstance(file_obj, str) and os.path.exists(file_obj):
        # It's already a path, just use it (or copy it if needed)
        # But for logic consistency, let's copy to temp_path/read it
        with open(file_obj, "rb") as f_src:
            content = f_src.read()
    elif hasattr(file_obj, "getvalue"):
         # Streamlit UploadedFile
         content = file_obj.getvalue()
    elif hasattr(file_obj, "read"):
         # Python File Object
         content = file_obj.read()
    else:
         raise ValueError("Unsupported file object type")

    with open(temp_path, "wb") as f:
        f.write(content)
        
    try:
        # Step 1: Ingestion
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        elif filename.endswith(".txt"):
            loader = TextLoader(temp_path)
        elif filename.endswith(".csv"):
            loader = CSVLoader(temp_path)
        else:
            raise ValueError("Unsupported file format")
            
        pages = loader.load()
        print(f" -> Loaded {len(pages)} pages.")
        
        # Step 2: Intelligent Chunking (Optimized Size)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(pages)
        
        # Step 3: Metadata Enrichment
        # Prevents context loss and enables traceability.
        timestamp = datetime.datetime.now().isoformat()
        
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source"] = filename
            chunk.metadata["user_id"] = user_id
            chunk.metadata["session_id"] = session_id  # Traceability
            chunk.metadata["upload_timestamp"] = timestamp
            
            # Simulated "Section" metadata (page number serves as proxy)
            if "page" not in chunk.metadata:
                chunk.metadata["page"] = "Unknown"
        
        print(f" -> Created {len(chunks)} chunks with metadata.")
        
        # Step 12: Cleanup (No Waste)
        vectorstore = FinRAGVectorStore()
        vectorstore.delete_user_data(user_id)
        
        # Step 3 (Store): Embedding & Vector Storage
        vectorstore.add_documents(chunks)
        
        return len(chunks)
        
    finally:
        # Local Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
