"""
FinRAG Document Intelligence Router.
Prefix: /api/rag
Handles document ingestion, standard contextual question answering, and SSE streaming QA.
"""

import os
import uuid
import json
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas.rag import IngestResponse, QueryRequest, QueryResponse
from app.services.rag.ingest_service import ingest_file
from app.services.rag.vectorstore import FinRAGVectorStore
from app.services.rag.retriever import FinRAGRetriever
from app.services.rag.model_factory import get_qa_llm
from app.services.rag.prompt_templates import FINRAG_PROMPT

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy-initialized components
_rag_components = {"vs": None, "retriever": None, "llm": None}


def _get_rag_components():
    """Lazy-init RAG components on first query to prevent startup delays."""
    if _rag_components["retriever"] is None or _rag_components["llm"] is None:
        try:
            vs = FinRAGVectorStore()
            _rag_components["vs"] = vs
            _rag_components["retriever"] = FinRAGRetriever(vs)
            # Use fine-tuned Shiva-k22/gemma-FinAI for document Q&A
            _rag_components["llm"] = get_qa_llm()
            logger.info("RAG components initialized successfully (using fine-tuned QA model).")
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"RAG components failed to initialize: {str(e)}"
            )
    return _rag_components["retriever"], _rag_components["llm"]


@router.post("/ingest", response_model=IngestResponse, summary="Ingest document for RAG analysis")
async def ingest_document(
    file: UploadFile = File(...),
    user_id: str = Form("default_user")
):
    """
    Upload and index a financial document (PDF, TXT, CSV) into AstraDB vector store.
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Read file into memory and pass to service
        file_bytes = await file.read()
        import io
        file_obj = io.BytesIO(file_bytes)
        
        count = ingest_file(file_obj, file.filename, user_id, session_id)
        
        return IngestResponse(
            session_id=session_id,
            chunks_ingested=count,
            message="Document ingested successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/query", response_model=QueryResponse, summary="Query document using RAG")
async def query_document(request: QueryRequest):
    """
    Query the ingested document within session context and return factual answer with source citations.
    """
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        retriever_obj, llm = _get_rag_components()

        # Format question with recent conversation history
        search_query = request.question
        if request.chat_history:
            history_str = "\n".join([
                f"{msg.get('role', 'user').capitalize()}: {msg.get('text', '')}"
                for msg in request.chat_history[-4:]
            ])
            if history_str:
                search_query = f"Previous Conversation:\n{history_str}\n\nCurrent Question: {request.question}"

        # Context retrieval
        retrieved_docs = retriever_obj.retrieve(search_query, request.user_id, request.session_id)
        
        context_text = ""
        sources = []
        for d in retrieved_docs:
            meta = d.metadata
            source_str = f"[Doc: {meta.get('source', 'Unknown')} | Page: {meta.get('page', 'N/A')}]"
            context_text += f"{source_str}\n{d.page_content}\n\n"
            sources.append(source_str)
            
        if not context_text.strip():
            return QueryResponse(
                answer="The document does not provide this information.",
                sources=[]
            )
            
        # Generate Answer
        chain = FINRAG_PROMPT | llm
        response = chain.invoke({"context": context_text, "question": search_query})
        
        final_answer = response if isinstance(response, str) else getattr(response, "content", str(response))
        final_answer = final_answer.replace("```markdown", "").replace("```", "").strip()
        
        return QueryResponse(
            answer=final_answer,
            sources=list(set(sources))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/query/stream", summary="Stream query responses via SSE")
async def query_document_stream(request: QueryRequest):
    """
    Streaming SSE version of /query for the document (RAG) chat mode.
    Yields chunks as Server-Sent Events: data: {"chunk": "..."}\n\n
    """
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        retriever_obj, llm = _get_rag_components()

        search_query = request.question
        if request.chat_history:
            history_str = "\n".join([
                f"{msg.get('role', 'user').capitalize()}: {msg.get('text', '')}"
                for msg in request.chat_history[-4:]
            ])
            if history_str:
                search_query = f"Previous Conversation:\n{history_str}\n\nCurrent Question: {request.question}"

        retrieved_docs = retriever_obj.retrieve(search_query, request.user_id, request.session_id)
        
        context_text = ""
        sources = []
        for d in retrieved_docs:
            meta = d.metadata
            source_str = f"[Doc: {meta.get('source', 'Unknown')} | Page: {meta.get('page', 'N/A')}]"
            context_text += f"{source_str}\n{d.page_content}\n\n"
            sources.append(source_str)
            
        async def generate():
            if not context_text.strip():
                yield f"data: {json.dumps({'chunk': 'The document does not provide this information.'})}\n\n"
                yield "data: [DONE]\n\n"
                return
                
            try:
                sources_list = list(set(sources))
                yield f"data: {json.dumps({'sources': sources_list})}\n\n"
                
                chain = FINRAG_PROMPT | llm
                
                for chunk in chain.stream({"context": context_text, "question": search_query}):
                    content = chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
                    if content:
                        yield f"data: {json.dumps({'chunk': content})}\n\n"
                        await asyncio.sleep(0)  # Flush to network
                
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
