"""
FastAPI-compatible model loader using Nvidia API instead of local Streamlit model.
Replaces the original Shiva's streamlit-based model_loader that used @st.cache_resource
and downloaded a local HuggingFace model (Shiva-k22/gemma-FinAI).

All modules (expenses_categorizer, savings_analysis, investment_advisor) call
`call_llm(prompt)` from this file — so this single replacement fixes everything.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Initialize the OpenAI-compatible Nvidia client
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
                {"role": "system", "content": (
                    "You are FinSmart AI — a smart, friendly Indian personal finance assistant. "
                    "You speak like a knowledgeable friend, not a textbook. "
                    "When extracting data (expenses, income, savings), be precise and return only the requested structure. "
                    "When explaining, give a short plain-language summary first, then add bullet points or steps if needed. "
                    "Use real Indian examples (e.g., SIP in ELSS, PPF, EPF, Zerodha, UPI, CIBIL score). "
                    "Keep answers concise — avoid long paragraphs. Use ₹ for currency. "
                    "If something is complex, break it into numbered steps. "
                    "Never use jargon without a one-line explanation."
                )},
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
