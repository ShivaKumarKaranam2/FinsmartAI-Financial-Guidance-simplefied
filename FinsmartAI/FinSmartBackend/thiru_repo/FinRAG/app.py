import streamlit as st
import uuid
import time
from finrag.astradb_vectorstore import FinRAGVectorStore
from finrag.retriever import FinRAGRetriever
from finrag.model_factory import get_llm
from finrag.ingest_service import ingest_file
from finrag.prompt_templates import FINRAG_PROMPT

# Setup
st.set_page_config(page_title="FinRAG V2", page_icon="📈", layout="wide")
st.title("📈 FinRAG: Strict Financial Analysis")

# Initialize components
@st.cache_resource
def get_system():
    vs = FinRAGVectorStore()
    retriever = FinRAGRetriever(vs)
    llm = get_llm()
    return retriever, llm

retriever_obj, llm = get_system()

# Sidebar
with st.sidebar:
    st.header("1. Document Ingestion")
    USER_ID = st.text_input("User ID", value="user_123_demo")
    
    # Session Management (Traceability)
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
        
    uploaded_file = st.file_uploader("Upload Financial Doc", type=["pdf", "csv", "xlsx", "txt"])
    
    if uploaded_file and st.button("Ingest Document"):
        with st.spinner("Step 1: Ingesting & Cleaning Storage..."):
            try:
                # Step 0: Session Creation
                new_session_id = str(uuid.uuid4())
                st.session_state.session_id = new_session_id
                
                # Clear chat history
                st.session_state.messages = [{"role": "assistant", "content": "Document Processed. Session Started."}]
                
                # Step 1 & 12: Ingestion + Cleanup
                count = ingest_file(uploaded_file, uploaded_file.name, USER_ID, new_session_id)
                st.success(f"Ingested {count} chunks. Trace ID: {new_session_id}")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")
    
    if st.session_state.session_id:
        st.info(f"Active Session: {st.session_state.session_id}")
    else:
        st.warning("No active document session.")

    st.markdown("---")
    st.caption("FinRAG v3.5 | Architecture v2 | Strict Mode")

# Main Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Upload a document to begin analysis."}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Ask a financial question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            if not st.session_state.session_id:
                 st.error("Please upload a document to start a session.")
                 st.stop()
                 
            # Step 4 & 5: Intent & Retrieval
            retrieved_docs = retriever_obj.retrieve(prompt, USER_ID, st.session_state.session_id)
            
            # Step 7: Prompt Context Injection
            context_text = ""
            for d in retrieved_docs:
                meta = d.metadata
                source_str = f"[Doc: {meta.get('source', 'Unknown')} | Page: {meta.get('page', 'N/A')}]"
                context_text += f"{source_str}\n{d.page_content}\n\n"
            
            if not context_text.strip():
                # Step 10: Explicit Disclosure (Pre-check)
                msg = "Not explicitly specified in the document."
                st.warning(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            else:
                # Step 8: Answer Generation
                try:
                    chain = FINRAG_PROMPT | llm
                    response = chain.invoke({"context": context_text, "question": prompt})
                    
                    final_answer = response if isinstance(response, str) else response.content
                    final_answer = final_answer.replace("```markdown", "").replace("```", "").strip()
                    
                    st.markdown(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                        
                except Exception as e:
                    st.error(f"System Error: {e}")
