import os
import sys
from dotenv import load_dotenv

# Explicitly load env
env_path = os.path.abspath("FinRAG/.env")
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

print(f"ASTRA_DB_API_ENDPOINT: {os.getenv('ASTRA_DB_API_ENDPOINT')}")
print(f"ASTRA_DB_APPLICATION_TOKEN: {os.getenv('ASTRA_DB_APPLICATION_TOKEN')}")

# Add FinRAG to path so 'import finrag' works inside the module
sys.path.append(os.path.abspath("FinRAG"))

try:
    from finrag.astradb_vectorstore import FinRAGVectorStore
    print("Initializing VectorStore...")
    vs = FinRAGVectorStore()
    print("VectorStore initialized.")
    
    print("Testing connectivity...")
    # Try a dummy search
    results = vs.similarity_search_with_score("test", k=1)
    print("Search successful!")
    print(results)
    
except Exception as e:
    print(f"Error: {e}")
