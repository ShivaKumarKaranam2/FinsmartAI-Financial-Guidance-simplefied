import os
from typing import List, Dict, Optional, Any
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore
from finrag.model_factory import get_huggingface_embeddings
from config import (
    ASTRA_DB_API_ENDPOINT,
    ASTRA_DB_APPLICATION_TOKEN,
    COLLECTION_NAME
)

class FinRAGVectorStore:
    def __init__(self):
        """
        Step 3: Embedding & Vector Storage interface.
        Auto-creates the collection if it doesn't exist.
        """
        self.embedding = get_huggingface_embeddings()

        # Pre-create the collection via astrapy if it doesn't exist
        self._ensure_collection_exists()

        # Initialize LangChain vectorstore wrapper
        # autodetect_collection=True: reads existing collection settings from AstraDB
        # instead of trying to re-impose settings, which causes a 400 error on existing collections.
        self.vectorstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name=COLLECTION_NAME,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            token=ASTRA_DB_APPLICATION_TOKEN,
            autodetect_collection=True,
        )

    def _ensure_collection_exists(self):
        """Create the AstraDB collection if it doesn't already exist."""
        try:
            from astrapy import DataAPIClient

            client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
            db = client.get_database(ASTRA_DB_API_ENDPOINT)

            existing = [c.name for c in db.list_collections()]
            if COLLECTION_NAME not in existing:
                print(f"Creating AstraDB collection '{COLLECTION_NAME}' (384 dims)...")
                
                # Use astrapy 2.1 compliant syntax for definition and indexing defaults
                db.create_collection(
                    COLLECTION_NAME,
                    definition={
                        "vector": {
                            "dimension": 384,
                            "metric": "cosine"
                        }
                    }
                )
                print(f"Collection '{COLLECTION_NAME}' created successfully.")
            else:
                print(f"Collection '{COLLECTION_NAME}' already exists.")
        except Exception as e:
            print(f"Warning: Could not verify/create collection: {e}")

    def add_documents(self, documents: List[Document]):
        """
        Stores chunks in AstraDB.
        """
        self.vectorstore.add_documents(documents)
        print(f"Stored {len(documents)} chunks in AstraDB.")

    def delete_user_data(self, user_id: str):
        """
        Step 12: Cleanup logic.
        Deletes all documents for a specific user to prevent storage waste logic.
        """
        try:
            print(f"Cleaning up old data for User: {user_id}...")
            # Direct AstraPy fix to delete via metadata filter
            self.vectorstore.astra_env.collection.delete_many(
                filter={"user_id": user_id}
            )
            print(f"Cleanup complete for user: {user_id}")
            
        except Exception as e:
            print(f"Cleanup Warning: {e} (Continuing ingestion)")

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Step 5 & 6: Retrieval & Context Validation support.
        """
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)
