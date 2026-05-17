from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas import FinanceQueryRequest, FinanceAnalysisResponse, APIResponse
import sys
import json
import os


# Ensure Fin_Personal_Assitant is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../thiru_repo")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../thiru_repo/Fin_Personal_Assitant")))

# Import Finance Bot Logic
try:
    from Fin_Personal_Assitant.finance_bot.core import fin_smart_process
    from Fin_Personal_Assitant.model_loader import load_model
    # load_model() uses streamlit cache, which might not work here.
    # We should update model_loader to be framework agnostic or rely on LRU cache
    # For now, we trust the import.
except ImportError as e:
    print(f"Error importing Finance Bot: {e}")

router = APIRouter()

@router.post("/query", response_model=FinanceAnalysisResponse)
async def finance_query(request: FinanceQueryRequest):
    try:
        # Process specific finance logic
        # fin_smart_process handles routing between General QA and Analysis
        result = fin_smart_process(request.query)
        
        return FinanceAnalysisResponse(
            type=result.get("type"),
            response=result.get("response"),
            financial_summary=result.get("financial_summary"),
            cash_flow_summary=result.get("cash_flow_summary"),
            investment_guidance=result.get("investment_guidance"),
            investment_json=result.get("investment_json")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finance processing failed: {str(e)}")


# ── Streaming endpoint (NEW — original /query above is untouched) ──────────────
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

_stream_client = None

def _get_stream_client():
    global _stream_client
    if _stream_client is None:
        _stream_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
    return _stream_client


@router.post("/query/stream")
async def finance_query_stream(request: FinanceQueryRequest):
    """
    Streaming SSE version of /query for the general finance chatbot.
    Yields chunks as Server-Sent Events: data: <chunk>\n\n
    The original /query endpoint is completely unaffected.
    """
    async def generate():
        import asyncio
        try:
            client = _get_stream_client()
            
            # Build messages array starting with system prompt
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are FinSmart AI — a smart, friendly Indian personal finance assistant. "
                        "You talk like a knowledgeable friend, not a textbook or a formal advisor. "
                        "\n\nHow to respond:"
                        "\n- Start with a short, plain-language answer (1-2 sentences max)."
                        "\n- Then give structured details using bullet points or numbered steps."
                        "\n- Use real Indian examples: SIP, PPF, ELSS, FD, EPF, CIBIL, UPI, Zerodha, Groww, etc."
                        "\n- Use ₹ for currency. Keep numbers relatable (e.g., ₹5,000/month SIP)."
                        "\n- If a concept is complex, break it into simple numbered steps."
                        "\n- Use clean markdown: **bold** for key terms, `code` for numbers/formulas, > for tips."
                        "\n- Never write walls of text — keep paragraphs short."
                        "\n- If you don't know something specific, say so honestly and suggest where to look."
                    )
                }
            ]
            
            # Append chat history (max 4 messages)
            if request.chat_history:
                for msg in request.chat_history[-4:]:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("text", "")})
            
            # Append current query
            messages.append({"role": "user", "content": request.query})

            stream = client.chat.completions.create(
                model="meta/llama-3.3-70b-instruct",
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                top_p=0.95,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    # Send chunk as SSE event
                    yield f"data: {json.dumps({'chunk': delta.content})}\n\n"
                    await asyncio.sleep(0) # Flush to client immediately
            # Signal stream end
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
