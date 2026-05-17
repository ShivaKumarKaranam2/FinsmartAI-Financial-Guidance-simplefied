# FinRAG: Metadata-Driven Financial Analysis

A standalone RAG system for financial data with metadata-driven clustering, hierarchical summarization, and tree-based retrieval.

## Features
- **Hierarchical Retrieval**: Drills down from Entity -> Year -> Month -> Document -> Chunk.
- **Metadata-Driven**: Groups context by company, time, and type.
- **Table-Aware**: Preserves markdown table structures during chunking.
- **Summarization**: Generates numeric-aware summaries using a finetuned model.

## Setup

### Prerequisites
- Python 3.10+
- `uv` package manager (implied preference)
- AstraDB Account
- HuggingFace Token (for Gemma model)

### Installation
1.  **Clone the repository** (if not already done).
2.  **Install dependencies using `uv`**:
    ```bash
    uv pip install -r requirements.txt
    ```

### Configuration
Create a `.env` file in the `FinRAG/` directory (see `.env.example`):
```bash
ASTRA_DB_API_ENDPOINT=...
ASTRA_DB_APPLICATION_TOKEN=...
HF_TOKEN=...
```

## Usage

### 1. Ingest Data
Process the dataset, generate summaries, and upsert to AstraDB:
```bash
python ingest.py
```
*Note: This may take time due to LLM summarization steps.*

### 2. Run the App
Launch the Streamlit interface:
```bash
streamlit run app.py
```

### 3. Testing
Run unit tests:
```bash
python -m unittest discover tests
```

## Architecture
- `finrag/`: Core package
  - `astradb_vectorstore.py`: Hierarchical upsert/query wrapper.
  - `chunking.py`: Table-aware text splitter.
  - `cluster.py`: logic for grouping chunks by metadata.
  - `summarizer.py`: LLM-based summarization.
  - `retriever.py`: Tree-based retrieval orchestration.
  - `model_factory.py`: Centralized model loading.
