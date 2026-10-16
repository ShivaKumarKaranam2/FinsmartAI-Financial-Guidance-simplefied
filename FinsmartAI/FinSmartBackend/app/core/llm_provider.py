"""
Unified LLM Provider for FinSmart AI Backend.
Supports NVIDIA NIM and OpenAI-compatible endpoints with graceful error handling and fallbacks.
Follows Dependency Inversion (DIP) and Single Responsibility (SRP) principles.
"""

import os
import requests
from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__)

_openai_client: Optional[OpenAI] = None


def get_llm_client() -> OpenAI:
    """Returns a singleton OpenAI-compatible client configured for NVIDIA NIM."""
    global _openai_client
    if _openai_client is None:
        api_key = settings.llm.api_key or os.getenv("NVIDIA_NIM_API_KEY", "")
        base_url = settings.llm.base_url or os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        
        if not api_key:
            logger.warning("NVIDIA_NIM_API_KEY is not set. LLM calls will fail if invoked.")
            
        _openai_client = OpenAI(
            base_url=base_url,
            api_key=api_key or "missing-key"
        )
    return _openai_client


PRIMARY_HF_MODEL = "Shiva-k22/gemma-FinAI"
NVIDIA_FALLBACK_MODEL = "meta/llama-3.2-11b-vision-instruct"
GROQ_FALLBACK_MODEL = "openai/gpt-oss-120b"


def call_hf_primary(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.3
) -> str:
    """Primary Tier 1: Shiva-k22/gemma-FinAI via HuggingFace Inference (Dedicated Endpoint or Hub)."""
    hf_token = settings.llm.hf_token or os.getenv("HF_TOKEN", "")
    hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")  # Optional: set to deploy a dedicated HF Inference Endpoint
    from huggingface_hub import InferenceClient
    client = InferenceClient(
        base_url=hf_endpoint_url if hf_endpoint_url else None,
        token=hf_token if hf_token else None
    )
    full_prompt = f"<bos><start_of_turn>user\n{system_prompt}\n\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
    res = client.text_generation(
        full_prompt,
        model=PRIMARY_HF_MODEL if not hf_endpoint_url else None,
        max_new_tokens=max_tokens,
        temperature=max(temperature, 0.01),
    )
    if not res:
        raise RuntimeError("Empty response from HuggingFace model")
    return res


def call_nvidia_nim(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 1500,
    temperature: float = 0.3,
    model_name: str = NVIDIA_FALLBACK_MODEL
) -> str:
    """Fallback Tier 2: NVIDIA NIM meta/llama-3.2-11b-vision-instruct."""
    client = get_llm_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.95,
        timeout=45.0
    )
    return response.choices[0].message.content or ""


def call_groq_fallback(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
    temperature: float = 1.0
) -> str:
    """
    Fallback Tier 3: Groq openai/gpt-oss-120b using streaming completion.
    """
    from groq import Groq
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model=GROQ_FALLBACK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None
    )

    full_output = []
    for chunk in completion:
        delta = chunk.choices[0].delta.content or ""
        full_output.append(delta)

    return "".join(full_output)


def call_llm(
    prompt: str,
    max_tokens: int = 1500,
    temperature: float = 0.3,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None
) -> str:
    """
    Calls the LLM following the user's priority hierarchy:
      1. Primary: Shiva-k22/gemma-FinAI
      2. Fallback 1: meta/llama-3.2-11b-vision-instruct (NVIDIA NIM)
      3. Fallback 2: openai/gpt-oss-120b (Groq)
    Logs all inputs, outputs, latencies, and tier transitions.
    """
    import time

    default_system = (
        "You are FinSmart AI — a smart, friendly Indian personal finance assistant. "
        "You speak like a knowledgeable friend, not a textbook. "
        "When extracting data (expenses, income, savings), be precise and return only the requested structure. "
        "When explaining, give a short plain-language summary first, then add bullet points or steps if needed. "
        "Use real Indian examples (e.g., SIP in ELSS, PPF, EPF, Zerodha, UPI, CIBIL score). "
        "Keep answers concise — avoid long paragraphs. Use ₹ for currency. "
        "If something is complex, break it into numbered steps. "
        "Never use jargon without a one-line explanation."
    )

    sys_content = system_prompt if system_prompt is not None else default_system

    logger.info("=" * 60)
    logger.info(f"📥 [LLM INPUT]")
    logger.info(f"   Prompt chars: {len(prompt)} | Preview: {prompt[:150]}...")
    logger.info(f"   System prompt chars: {len(sys_content)}")

    # Tier 1: Shiva-k22/gemma-FinAI (Primary)
    # -- Direct HF serverless inference is skipped unless HF_ENDPOINT_URL is set (custom fine-tuned
    #    models are NOT supported on the free serverless API). We go straight to the HF Space instead.
    t0 = time.time()
    hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")

    if hf_endpoint_url:
        logger.info(f"🎯 [TIER 1] Attempting primary model via HF Endpoint: '{PRIMARY_HF_MODEL}'...")
        try:
            content = call_hf_primary(prompt, sys_content, max_tokens=min(max_tokens, 512), temperature=temperature)
            duration = round(time.time() - t0, 2)
            logger.info(f"✅ [LLM OUTPUT] Tier 1 HF Endpoint ({PRIMARY_HF_MODEL}) succeeded in {duration}s")
            logger.info(f"   Output preview: {content[:150]}...")
            logger.info("=" * 60)
            return content
        except Exception as e_hf:
            duration = round(time.time() - t0, 2)
            logger.warning(f"⚠️ [TIER 1 HF ENDPOINT FAILED] after {duration}s: {e_hf}. Trying HF Space...")
    else:
        logger.info(
            f"ℹ️  [TIER 1] HF_ENDPOINT_URL not set — skipping direct HF serverless (unsupported for custom "
            f"fine-tuned models). Trying HF Space: '{settings.llm.gemma_space_url}'..."
        )

    # Tier 1b: HF Space (Gradio API)
    try:
        content = call_hf_space(prompt, sys_content, max_tokens=min(max_tokens, 512), temperature=temperature)
        duration = round(time.time() - t0, 2)
        logger.info(f"✅ [LLM OUTPUT] Tier 1 HF Space ({PRIMARY_HF_MODEL}) succeeded in {duration}s")
        logger.info(f"   Output preview: {content[:150]}...")
        logger.info("=" * 60)
        return content
    except Exception as e_space:
        duration = round(time.time() - t0, 2)
        logger.warning(f"⚠️ [HF SPACE FAILED] after {duration}s: {e_space}. Falling back to Tier 2 (NVIDIA NIM: '{NVIDIA_FALLBACK_MODEL}')...")


    # Tier 2: meta/llama-3.2-11b-vision-instruct (NVIDIA NIM)
    t1 = time.time()
    logger.info(f"🔄 [TIER 2] Falling back to NVIDIA NIM: '{NVIDIA_FALLBACK_MODEL}'...")
    try:
        content = call_nvidia_nim(prompt, sys_content, max_tokens=max_tokens, temperature=temperature)
        duration = round(time.time() - t1, 2)
        logger.info(f"✅ [LLM OUTPUT] Tier 2 ({NVIDIA_FALLBACK_MODEL}) succeeded in {duration}s")
        logger.info(f"   Output preview: {content[:150]}...")
        logger.info("=" * 60)
        return content
    except Exception as e_tier2:
        duration = round(time.time() - t1, 2)
        logger.warning(f"⚠️ [TIER 2 FAILED] '{NVIDIA_FALLBACK_MODEL}' failed after {duration}s: {e_tier2}")

    # Tier 3: openai/gpt-oss-120b (Groq)
    t2 = time.time()
    logger.info(f"🔄 [TIER 3] Falling back to Groq: '{GROQ_FALLBACK_MODEL}'...")
    try:
        content = call_groq_fallback(prompt, sys_content, max_tokens=max_tokens, temperature=temperature)
        duration = round(time.time() - t2, 2)
        logger.info(f"✅ [LLM OUTPUT] Tier 3 ({GROQ_FALLBACK_MODEL}) succeeded in {duration}s")
        logger.info(f"   Output preview: {content[:150]}...")
        logger.info("=" * 60)
        return content
    except Exception as e_tier3:
        duration = round(time.time() - t2, 2)
        logger.error(f"❌ [TIER 3 FAILED] '{GROQ_FALLBACK_MODEL}' failed after {duration}s: {e_tier3}")
        logger.error(f"❌ All 3 tiers failed. Prompt could not be completed.")
        logger.info("=" * 60)

def stream_llm(
    messages: list,
    max_tokens: int = 1024,
    temperature: float = 0.3
):
    """
    Generator that streams LLM chunks following the user's 3-tier hierarchy:
      1. Primary: Shiva-k22/gemma-FinAI (HF Endpoint / Serverless)
      2. Fallback 1: meta/llama-3.2-11b-vision-instruct (NVIDIA NIM)
      3. Fallback 2: openai/gpt-oss-120b (Groq)
    """
    import time
    logger.info("=" * 60)
    logger.info("📥 [STREAMING LLM REQUEST]")
    logger.info(f"   Messages count: {len(messages)}")

    # Tier 1: Shiva-k22/gemma-FinAI
    # -- Direct HF serverless inference only works for featured base models, NOT custom fine-tuned weights.
    #    Skip it unless a dedicated HF_ENDPOINT_URL (paid HF Inference Endpoint) is configured.
    #    Instead, try the HF Space (Gradio API) which actually hosts the fine-tuned model.
    t0 = time.time()
    hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")  # Optional: dedicated HF Inference Endpoint

    if hf_endpoint_url:
        logger.info(f"🎯 [TIER 1] Attempting primary model stream via HF Endpoint: '{PRIMARY_HF_MODEL}'...")
        hf_token = settings.llm.hf_token or os.getenv("HF_TOKEN", "")
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(base_url=hf_endpoint_url, token=hf_token if hf_token else None)
            prompt_str = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
            gen = client.text_generation(prompt_str, stream=True, max_new_tokens=min(max_tokens, 512))
            first_chunk = next(gen)
            yield first_chunk
            for chunk in gen:
                yield chunk
            duration = round(time.time() - t0, 2)
            logger.info(f"✅ [LLM STREAM OUTPUT] Tier 1 HF Endpoint ({PRIMARY_HF_MODEL}) completed in {duration}s")
            return
        except Exception as e_hf_endpoint:
            duration = round(time.time() - t0, 2)
            logger.warning(f"⚠️ [TIER 1 HF ENDPOINT FAILED] after {duration}s: {e_hf_endpoint}. Trying HF Space...")
    else:
        logger.info(
            f"ℹ️  [TIER 1] HF_ENDPOINT_URL not set — skipping direct HF serverless (not supported for custom "
            f"fine-tuned models). Trying HF Space: '{settings.llm.gemma_space_url}'..."
        )

    # Tier 1b: HF Space (Gradio API) — hosts the actual fine-tuned gemma-FinAI model
    try:
        space_response = call_hf_space_messages(
            messages,
            max_tokens=min(max_tokens, 512),
            temperature=temperature,
        )
        if space_response:
            yield space_response
            duration = round(time.time() - t0, 2)
            logger.info(f"✅ [LLM STREAM OUTPUT] Tier 1 HF Space ({PRIMARY_HF_MODEL}) completed in {duration}s")
            return
    except Exception as e_space:
        duration = round(time.time() - t0, 2)
        logger.warning(
            f"⚠️ [TIER 1 HF SPACE FAILED] after {duration}s: {e_space}. "
            f"Falling back to Tier 2 (NVIDIA NIM: '{NVIDIA_FALLBACK_MODEL}')..."
        )

    # Tier 2: meta/llama-3.2-11b-vision-instruct (NVIDIA NIM)
    t1 = time.time()
    logger.info(f"🔄 [TIER 2] Streaming from NVIDIA NIM: '{NVIDIA_FALLBACK_MODEL}'...")
    try:
        client = get_llm_client()
        stream = client.chat.completions.create(
            model=NVIDIA_FALLBACK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            stream=True,
            timeout=45.0
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
        duration = round(time.time() - t1, 2)
        logger.info(f"✅ [LLM STREAM OUTPUT] Tier 2 ({NVIDIA_FALLBACK_MODEL}) completed in {duration}s")
        return
    except Exception as e_tier2:
        duration = round(time.time() - t1, 2)
        logger.warning(f"⚠️ [TIER 2 FAILED] '{NVIDIA_FALLBACK_MODEL}' failed after {duration}s: {e_tier2}. Falling back to Tier 3 (Groq)...")

    # Tier 3: openai/gpt-oss-120b (Groq)
    t2 = time.time()
    logger.info(f"🔄 [TIER 3] Streaming from Groq: '{GROQ_FALLBACK_MODEL}'...")
    try:
        from groq import Groq
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        client = Groq(api_key=groq_api_key)
        stream = client.chat.completions.create(
            model=GROQ_FALLBACK_MODEL,
            messages=messages,
            temperature=1.0,
            max_completion_tokens=max_tokens,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
        duration = round(time.time() - t2, 2)
        logger.info(f"✅ [LLM STREAM OUTPUT] Tier 3 ({GROQ_FALLBACK_MODEL}) completed in {duration}s")
        return
    except Exception as e_tier3:
        duration = round(time.time() - t2, 2)
        logger.error(f"❌ [TIER 3 FAILED] Groq stream failed after {duration}s: {e_tier3}")
        raise RuntimeError(f"All 3 LLM streaming tiers failed. Last error: {e_tier3}") from e_tier3





def load_model():
    """
    Backward-compatibility shim for legacy callers expecting local model loader.
    Logs warning and returns a placeholder tuple (tokenizer, model, device)
    so imports don't crash when using API-based inference.
    """
    logger.info("load_model() invoked. Operating in API mode via NVIDIA NIM.")
    return None, None, "api"

# New helper to call HuggingFace Space endpoint if primary HF inference fails.
def _space_runtime_url(url: str) -> str:
    """Normalize a Space URL to its runtime host.

    Accepts either the web URL (https://huggingface.co/spaces/owner/name) or the
    runtime host (https://owner-name.hf.space) and always returns the runtime host,
    which is where the Gradio API actually lives.
    """
    import re
    url = (url or "").strip().rstrip("/")
    m = re.match(r"https?://huggingface\.co/spaces/([^/]+)/([^/?#]+)", url)
    if m:
        owner, name = m.group(1), m.group(2)
        sub = f"{owner}-{name}".replace("_", "-").lower()
        return f"https://{sub}.hf.space"
    return url


def _parts(content) -> list:
    """Convert a message content value into Gradio 6 parts format (list of parts)."""
    if isinstance(content, list):
        return content
    return [{"text": str(content if content is not None else ""), "type": "text"}]


def _text(content) -> str:
    """Extract plain text from Gradio chat content (str or list-of-parts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return str(content or "")


def _call_space(history: list, max_tokens: int, temperature: float,
                url: Optional[str] = None, fn: Optional[str] = None,
                timeout: int = 60, retries: int = 2) -> str:
    """Call the HF Space Gradio API (queue + SSE) and return the assistant reply text.

    Handles ZeroGPU cold starts / sleep by retrying on 502/503 with backoff. `history`
    must be a list of {role, content} dicts where content is in Gradio parts format.

    Attempts the primary (fine-tuned) model at most `retries` (default 2) times; after
    that the caller falls back to NVIDIA NIM, then Groq.
    """
    import time, json, requests

    base = _space_runtime_url(url or settings.llm.gemma_space_url)
    fn_name = (fn or getattr(settings.llm, "gemma_space_fn", "/bot_reply") or "/bot_reply").strip("/")
    endpoint = f"{base}/gradio_api/call/{fn_name}"
    payload = {"data": [history, int(max_tokens), float(temperature)]}

    headers = {}
    token = settings.llm.hf_token or os.getenv("HF_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
            if resp.status_code in (502, 503):
                # Space is asleep / cold-starting on ZeroGPU — wait and retry.
                wait = min(20, 5 * (attempt + 1))
                last_err = RuntimeError(f"Space waking up (HTTP {resp.status_code})")
                logger.info(f"⏳ [HF SPACE] waking up (HTTP {resp.status_code}), retry {attempt + 1}/{retries} in {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            event_id = resp.json()["event_id"]

            data = None
            with requests.get(f"{endpoint}/{event_id}", stream=True, timeout=timeout) as stream:
                event = None
                for line in stream.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("event:"):
                        event = line.split(":", 1)[1].strip()
                    elif line.startswith("data:"):
                        payload_str = line.split(":", 1)[1].strip()
                        if event == "error":
                            raise RuntimeError(f"Space returned error: {payload_str}")
                        if event == "complete":
                            data = json.loads(payload_str)

            if data is None:
                raise RuntimeError("Space returned no result")
            # /bot_reply returns the full message history, wrapped as a single output
            if isinstance(data, list) and data and isinstance(data[0], list):
                data = data[0]
            if isinstance(data, list) and data:
                last = data[-1]
                return _text(last.get("content") if isinstance(last, dict) else last)
            return _text(data)
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))

    raise RuntimeError(f"HF Space inference failed: {last_err}")


def call_hf_space(prompt: str, system_prompt: str = "", max_tokens: int = 512,
                  temperature: float = 0.3) -> str:
    """Inference via HuggingFace Space (Gradio API) for the custom fine-tuned gemma-FinAI model.

    The Space bakes in its own system prompt, so `system_prompt` is intentionally ignored.
    """
    history = [{"role": "user", "content": _parts(prompt)}]
    return _call_space(history, max_tokens, temperature)


def call_hf_space_messages(messages: List[Dict[str, Any]], max_tokens: int = 1024,
                           temperature: float = 0.3) -> str:
    """Like `call_hf_space` but preserves multi-turn chat structure.

    System messages are dropped because the Space already supplies its own system prompt.
    """
    history: List[Dict[str, Any]] = []
    for m in messages:
        role = m.get("role", "user")
        if role == "system":
            continue
        history.append({
            "role": "assistant" if role == "assistant" else "user",
            "content": _parts(m.get("content", "")),
        })
    if not history or history[-1]["role"] != "user":
        history.append({"role": "user", "content": _parts("")})
    return _call_space(history, max_tokens, temperature)
