from typing import List, Dict, Optional
from langchain_core.documents import Document
from finrag.astradb_vectorstore import FinRAGVectorStore

class FinRAGRetriever:
    def __init__(self, vectorstore: FinRAGVectorStore):
        self.vectorstore = vectorstore

    def retrieve(self, query: str, user_id: str, session_id: str) -> List[Document]:
        """
        Step 5: Context Retrieval.
        Strictly filters by user identity and session.
        """
        print(f"Retrieval Request | Query: '{query}' | User: {user_id}")
        
        # Consistent Retrieval Setting
        # Increased k=5 for better context coverage with Nemotron
        k = 5
        score_threshold = 0.0 # Disabled strict threshold, let Vector DB sort by top k natively
        
        # Metadata Filters (LangChain requires root level keys for top-level metadata)
        filter_dict = {
            "user_id": user_id,
            "session_id": session_id
        }
        
        # Step 6: Context Validation
        results_with_scores = self.vectorstore.similarity_search_with_score(query, k=k, filter=filter_dict)
        
        validated_docs = []
        rejected_count = 0
        
        for doc, score in results_with_scores:
            if score >= score_threshold:
                # Inject relevance score for transparency (optional, depending on if prompt uses it)
                doc.metadata["relevance_score"] = score 
                validated_docs.append(doc)
            else:
                rejected_count += 1
                
        if rejected_count > 0:
             print(f"Validation: Rejected {rejected_count} chunks below threshold {score_threshold}")
        
        return validated_docs
