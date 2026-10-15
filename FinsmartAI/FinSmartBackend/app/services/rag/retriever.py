"""
FinRAG Context Retriever.
Filters documents strictly by user identity and session for isolation and relevance.
"""

from typing import List, Optional
from langchain_core.documents import Document

from app.core.logging import setup_logger
from app.services.rag.vectorstore import FinRAGVectorStore

logger = setup_logger(__name__)


class FinRAGRetriever:
    """Retriever for contextual financial document search."""

    def __init__(self, vectorstore: FinRAGVectorStore):
        self.vectorstore = vectorstore

    def retrieve(self, query: str, user_id: str, session_id: str, k: int = 5) -> List[Document]:
        """
        Retrieves context documents strictly filtered by user_id and session_id.
        
        Args:
            query: The question or conversation turn
            user_id: User identifier
            session_id: Session identifier
            k: Number of top chunks to retrieve
            
        Returns:
            List of validated Document chunks
        """
        logger.info(f"Retrieval Request | Query: '{query[:80]}...' | User: {user_id} | Session: {session_id}")

        filter_dict = {
            "user_id": user_id,
            "session_id": session_id
        }

        try:
            results_with_scores = self.vectorstore.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )

            validated_docs = []
            for doc, score in results_with_scores:
                doc.metadata["relevance_score"] = score
                validated_docs.append(doc)

            return validated_docs
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            # Fallback to direct search without score
            try:
                return self.vectorstore.similarity_search(query, k=k, filter=filter_dict)
            except Exception as e2:
                logger.error(f"Fallback similarity search also failed: {e2}")
                return []
