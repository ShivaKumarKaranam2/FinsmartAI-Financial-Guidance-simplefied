"""
Personal Finance Assistant Router.
Prefix: /api/finance_rag
Handles personal finance Q&A, automated cash flow classification, and real-time SSE streaming.
"""

import os
import json
import asyncio
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas.finance import FinanceQueryRequest, FinanceAnalysisResponse
from app.core.config import settings
from app.core.llm_provider import get_llm_client
from app.services.finance_bot.core import fin_smart_process

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=FinanceAnalysisResponse, summary="Query personal finance assistant")
async def finance_query(request: FinanceQueryRequest):
    """
    Process personal financial inquiries. Routes automatically between general financial Q&A
    and full personal budget/cash flow/investment analysis.
    """
    try:
        result = fin_smart_process(request.query)
        
        return FinanceAnalysisResponse(
            type=result.get("type", "general_answer"),
            response=result.get("response"),
            financial_summary=result.get("financial_summary"),
            cash_flow_summary=result.get("cash_flow_summary"),
            investment_guidance=result.get("investment_guidance"),
            investment_json=result.get("investment_json")
        )
        
    except Exception as e:
        logger.error(f"Finance query processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Finance processing failed: {str(e)}")


from app.core.llm_provider import stream_llm


@router.post("/query/stream", summary="Stream general finance chatbot responses via SSE")
async def finance_query_stream(request: FinanceQueryRequest):
    """
    Streaming SSE version of /query for interactive chat.
    Uses 3-tier fallback: Shiva-k22/gemma-FinAI -> meta/llama-3.2-11b-vision-instruct -> Groq.
    Yields chunks as Server-Sent Events: data: {"chunk": "..."}\n\n
    """
    async def generate():
        try:
            system_prompt = (
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
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Append chat history (max 4 messages)
            if request.chat_history:
                for msg in request.chat_history[-4:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("text", "")
                    })
            
            messages.append({"role": "user", "content": request.query})

            for chunk_content in stream_llm(messages, max_tokens=1024, temperature=0.3):
                yield f"data: {json.dumps({'chunk': chunk_content})}\n\n"
                await asyncio.sleep(0)
                    
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Finance query stream failed: {str(e)}", exc_info=True)
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
