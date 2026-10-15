"""
AstraDB Vector Store Service for FinRAG.
Handles vector storage, collection lifecycle, metadata filtering, and similarity search.
"""

from typing import List, Dict, Optional, Any, Tuple
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import setup_logger
from app.services.rag.model_factory import get_huggingface_embeddings

logger = setup_logger(__name__)


class FinRAGVectorStore:
    """
    Embedding and Vector Storage interface backed by DataStax AstraDB.
    Auto-creates the collection if it doesn't already exist.
    """

    def __init__(self):
        try:
            from langchain_astradb import AstraDBVectorStore
        except ImportError as e:
            logger.error("langchain_astradb is not installed. Please install langchain-astradb.")
            raise RuntimeError("langchain-astradb is required for AstraDB vector operations.") from e

        self.embedding = get_huggingface_embeddings()
        self.collection_name = settings.astradb.collection_name
        self.api_endpoint = settings.astradb.api_endpoint
        self.token = settings.astradb.application_token

        # Ensure collection exists
        self._ensure_collection_exists()

        # Initialize LangChain vectorstore wrapper
        self.vectorstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name=self.collection_name,
            api_endpoint=self.api_endpoint,
            token=self.token,
            content_field="content",
        )


    def _ensure_collection_exists(self):
        """Create the AstraDB collection if it doesn't already exist."""
        try:
            from astrapy import DataAPIClient

            client = DataAPIClient(self.token)
            db = client.get_database(self.api_endpoint)

            existing = [c.name for c in db.list_collections()]
            if self.collection_name not in existing:
                logger.info(f"Creating AstraDB collection '{self.collection_name}' (384 dims)...")
                db.create_collection(
                    self.collection_name,
                    definition={
                        "vector": {
                            "dimension": 384,
                            "metric": "cosine"
                        }
                    }
                )
                logger.info(f"Collection '{self.collection_name}' created successfully.")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.warning(f"Could not verify/create AstraDB collection: {e}")

    def add_documents(self, documents: List[Document]):
        """Stores chunked documents in AstraDB."""
        self.vectorstore.add_documents(documents)
        logger.info(f"Stored {len(documents)} chunks in AstraDB.")

    def delete_user_data(self, user_id: str):
        """Deletes all documents for a specific user to prevent storage waste."""
        try:
            logger.info(f"Cleaning up old data for User: {user_id}...")
            self.vectorstore.astra_env.collection.delete_many(
                filter={"user_id": user_id}
            )
            logger.info(f"Cleanup complete for user: {user_id}")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e} (Continuing)")

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """Retrieves documents along with cosine similarity scores."""
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)

    def similarity_search(
        self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Retrieves documents matching query and filter."""
        return self.vectorstore.similarity_search(query, k=k, filter=filter)
