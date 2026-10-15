"""
Model factory for FinRAG embeddings and LLMs.
- get_huggingface_embeddings(): sentence-transformer embeddings for AstraDB
- get_qa_llm(): Fine-tuned HuggingFace model (Shiva-k22/gemma-FinAI) for RAG document Q&A
- get_llm(): NVIDIA NIM LLM for general purpose tasks / fallback
Uses lru_cache for framework-agnostic caching.
"""

from functools import lru_cache
import os
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__)


@lru_cache(maxsize=1)
def get_huggingface_embeddings():
    """
    Loads and caches the HuggingFace sentence transformer embedding model.
    """
    model_name = settings.astradb.embedding_model
    logger.info(f"Loading embedding model: {model_name}...")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model_name)
    except ImportError:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name=model_name)
        except Exception as e:
            logger.error(f"Failed to load HuggingFaceEmbeddings: {e}")
            raise


@lru_cache(maxsize=1)
def get_qa_llm():
    """
    Loads and caches the fine-tuned HuggingFace model `Shiva-k22/gemma-FinAI`
    for RAG document Q&A (question answering over financial documents).

    Returns a LangChain-compatible LLM wrapper. Falls back to NVIDIA NIM if
    the HuggingFace model fails to load (e.g., insufficient VRAM or missing token).
    """
    model_id = settings.llm.qa_model   # default: "Shiva-k22/gemma-FinAI"
    hf_token = settings.llm.hf_token or os.getenv("HF_TOKEN", "")

    logger.info(f"Loading fine-tuned QA model from HuggingFace: {model_id}...")

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        from langchain_huggingface import HuggingFacePipeline

        # Use GPU if available, otherwise CPU
        device = 0 if torch.cuda.is_available() else -1
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=hf_token if hf_token else None,
            trust_remote_code=True,
        )

        # Check if model is already downloaded locally to avoid freezing server with 5GB download
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                local_files_only=True,
                dtype=dtype,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
        except (OSError, EnvironmentError):
            logger.info(
                f"Local weights for '{model_id}' not found in cache. "
                "Falling back to high-speed cloud LLM (NVIDIA NIM / Groq)."
            )
            return get_llm()

        hf_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            top_p=0.95,
            repetition_penalty=1.15,
            device=device if not torch.cuda.is_available() else None,
        )

        logger.info(f"Fine-tuned QA model '{model_id}' loaded successfully.")
        return HuggingFacePipeline(pipeline=hf_pipeline)


    except Exception as e:
        logger.warning(
            f"Failed to load fine-tuned model '{model_id}': {e}. "
            "Falling back to NVIDIA NIM LLM."
        )
        # Graceful fallback to NVIDIA NIM
        return get_llm()


@lru_cache(maxsize=1)
def get_llm():
    """
    Loads the LLM for RAG tasks with 2-tier fallback:
      Tier 1: NVIDIA NIM (meta/llama-3.2-11b-vision-instruct)
      Tier 2: Groq (openai/gpt-oss-120b)
    """
    api_key = settings.llm.api_key or os.getenv("NVIDIA_NIM_API_KEY")
    model_name = settings.llm.rag_model or "meta/llama-3.2-11b-vision-instruct"

    if api_key:
        logger.info(f"Loading NVIDIA NIM LLM: {model_name}...")
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            return ChatNVIDIA(
                model=model_name,
                api_key=api_key,
                temperature=0.1,
                max_tokens=1024,
                top_p=0.95
            )
        except Exception as e:
            logger.warning(f"ChatNVIDIA initialization failed: {e}. Trying ChatOpenAI wrapper...")
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=model_name,
                    openai_api_key=api_key,
                    openai_api_base=settings.llm.base_url,
                    temperature=0.1,
                    max_tokens=1024
                )
            except Exception as e2:
                logger.warning(f"NVIDIA NIM failed: {e2}. Falling back to Groq...")

    # Fallback to Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        logger.info("Loading Groq fallback LLM (openai/gpt-oss-120b)...")
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=groq_api_key,
            temperature=0.1,
            max_tokens=2048
        )

    raise ValueError("Neither NVIDIA_NIM_API_KEY nor GROQ_API_KEY is available for RAG LLM.")

