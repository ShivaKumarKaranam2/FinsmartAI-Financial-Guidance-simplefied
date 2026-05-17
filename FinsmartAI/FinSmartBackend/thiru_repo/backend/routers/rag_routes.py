from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from ..schemas import IngestResponse, QueryRequest, QueryResponse, APIResponse
import uuid
import shutil
import os
import sys

# Ensure FinRAG is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../FinRAG")))

# Import FinRAG Logic
# We need to handle imports carefully because FinRAG code expects config to be in path or relative
# Ideally we should refactor FinRAG to be a proper package, but for now we hack the path.
from FinRAG.finrag.ingest_service import ingest_file
from FinRAG.finrag.astradb_vectorstore import FinRAGVectorStore
from FinRAG.finrag.retriever import FinRAGRetriever
from FinRAG.finrag.model_factory import get_llm
from FinRAG.finrag.prompt_templates import FINRAG_PROMPT

router = APIRouter()

# Initialize Components
# Define as None initially to prevent NameError
vs = None
retriever_obj = None
llm = None

try:
    vs = FinRAGVectorStore()
    retriever_obj = FinRAGRetriever(vs)
    llm = get_llm() # This loads Nvidia NIM
except Exception as e:
    print(f"Error initializing FinRAG components: {e}")
    # We don't crash, but endpoints might fail

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...), 
    user_id: str = Form("default_user")
):
    # Check dependencies (ingest uses vectorstore internally via ingest_file -> FinRAGVectorStore)
    # But ingest_file imports FinRAGVectorStore class and instantiates it.
    # So we don't strictly need 'vs' here, but it's good practice to ensure DB connectivity.
    pass 

    try:
        session_id = str(uuid.uuid4())
        
        # Save temp file
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ingest
        # FinRAG ingest logic expects a file-like or path? 
        # ingest_file in FinRAG expects (file_obj, filename, user_id, session_id)
        # It reads file_obj.name. Let's check ingest_service.py signature if I could.
        # Assuming it handles file path or I can pass the opened file
        
        with open(temp_path, "rb") as f:
            # We need to mock a file object that has .name attribute if required
            # The ingest_service.py I saw earlier uses `ingest_file(uploaded_file, uploaded_file.name, ...)`
            # So I should pass the open file and explicit name
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
            
        if not retriever_obj or not llm:
             raise HTTPException(status_code=503, detail="RAG components not initialized. Check server logs.")

        # Retrieval
        retrieved_docs = retriever_obj.retrieve(request.question, request.user_id, request.session_id)
        
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
        response = chain.invoke({"context": context_text, "question": request.question})
        
        final_answer = response if isinstance(response, str) else response.content
        final_answer = final_answer.replace("```markdown", "").replace("```", "").strip()
        
        return QueryResponse(
            answer=final_answer,
            sources=list(set(sources))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
