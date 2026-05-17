from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from schemas import IngestResponse, QueryRequest, QueryResponse, APIResponse
import uuid
import shutil
import os
import sys

# Ensure FinRAG and Fin_Personal_Assitant are in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../thiru_repo")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../thiru_repo/FinRAG")))

# Import FinRAG Logic
from finrag.ingest_service import ingest_file
from finrag.astradb_vectorstore import FinRAGVectorStore
from finrag.retriever import FinRAGRetriever
from finrag.model_factory import get_llm
from finrag.prompt_templates import FINRAG_PROMPT

router = APIRouter()

# ── Lazy-initialized singletons ──
_rag_components = {"vs": None, "retriever": None, "llm": None}

def _get_rag_components():
    """Lazy-init RAG components on first query (avoids startup crash)."""
    if _rag_components["retriever"] is None or _rag_components["llm"] is None:
        try:
            vs = FinRAGVectorStore()
            _rag_components["vs"] = vs
            _rag_components["retriever"] = FinRAGRetriever(vs)
            _rag_components["llm"] = get_llm()
            print("✅ RAG components initialized successfully.")
        except Exception as e:
            print(f"❌ Error initializing RAG components: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"RAG components failed to initialize: {str(e)}"
            )
    return _rag_components["retriever"], _rag_components["llm"]


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...), 
    user_id: str = Form("default_user")
):
    try:
        session_id = str(uuid.uuid4())
        
        # Save temp file
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ingest via FinRAG pipeline
        with open(temp_path, "rb") as f:
            count = ingest_file(f, file.filename, user_id, session_id)
            
        # Cleanup
        os.remove(temp_path)
        
        return IngestResponse(
            session_id=session_id,
            chunks_ingested=count,
            message="Document ingested successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Lazy-init on first query
        retriever_obj, llm = _get_rag_components()

        # Format question with history
        search_query = request.question
        if request.chat_history:
            history_str = "\n".join([f"{msg.get('role', 'user').capitalize()}: {msg.get('text', '')}" for msg in request.chat_history[-4:]])
            if history_str:
                search_query = f"Previous Conversation:\n{history_str}\n\nCurrent Question: {request.question}"

        # Retrieval
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
        
        final_answer = response if isinstance(response, str) else response.content
        final_answer = final_answer.replace("```markdown", "").replace("```", "").strip()
        
        return QueryResponse(
            answer=final_answer,
            sources=list(set(sources))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

from fastapi.responses import StreamingResponse
import json
import asyncio

@router.post("/query/stream")
async def query_document_stream(request: QueryRequest):
    """
    Streaming SSE version of /query for the document (RAG) chat mode.
    Yields chunks as Server-Sent Events: data: {"chunk": "..."}\n\n
    """
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Lazy-init on first query
        retriever_obj, llm = _get_rag_components()

        # Format question with history
        search_query = request.question
        if request.chat_history:
            history_str = "\n".join([f"{msg.get('role', 'user').capitalize()}: {msg.get('text', '')}" for msg in request.chat_history[-4:]])
            if history_str:
                search_query = f"Previous Conversation:\n{history_str}\n\nCurrent Question: {request.question}"

        # Retrieval
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
                # First send sources
                sources_list = list(set(sources))
                yield f"data: {json.dumps({'sources': sources_list})}\n\n"
                
                chain = FINRAG_PROMPT | llm
                
                # Stream chunks
                for chunk in chain.stream({"context": context_text, "question": search_query}):
                    content = chunk if isinstance(chunk, str) else chunk.content
                    if content:
                        yield f"data: {json.dumps({'chunk': content})}\n\n"
                        await asyncio.sleep(0) # Flush
                
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
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

