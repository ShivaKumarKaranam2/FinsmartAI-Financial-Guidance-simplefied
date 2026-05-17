"""
FastAPI-compatible model loader using Nvidia API.
Replaces the original local HuggingFace model (Shiva-k22/gemma-FinAI).
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
    return _client

def load_model():
    """Kept for backward compatibility — no-op in API mode."""
    pass

def call_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
    """
    Generates a response from the Nvidia LLM API.
    Drop-in replacement for the original local model call_llm.
    """
    client = _get_client()
    
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": "You are an expert Indian financial advisor and data extractor. Always respond precisely and concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return f"Error generating response: {str(e)}"
