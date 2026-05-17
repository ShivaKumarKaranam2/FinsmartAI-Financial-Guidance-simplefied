import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import streamlit as st

# Global cache for the model
@st.cache_resource
def load_model():
    model_name = "Shiva-k22/gemma-FinAI"
    
    # Determine device
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
        
    print(f"Loading model on {device}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32
    ).to(device)
    
    return tokenizer, model, device

# Helper function to serve as 'call_llm'
def call_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
    """
    Generates a response from the LLM based on the prompt.
    This acts as the bridge between logic modules and the model.
    """
    tokenizer, model, device = load_model()
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.95
        )
        
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Simple post-processing to strip the prompt from the output if the model repeats it
    # (Gemma sometimes repeats the prompt, but usually decode(skip_special_tokens=True) handles it.
    # However, for safety, let's just return the raw decode and let logic filter if needed, 
    # or try to split if the prompt is explicitly echoed.)
    
    # A cleaner approach for instruction models:
    # If the prompt ends with specific token, we might parse. 
    # For now, we return specific substring if prompt is echoed, 
    # but 'decode' usually gives full text.
    
    # Heuristic: verify if response starts with prompt and strip it
    if response.startswith(prompt):
        response = response[len(prompt):].strip()
        
    # Another common pattern is "User: ... Model: ..." or similar.
    # But since we control the prompt, we assume we get the full text.
    # Let's rely on the prompt structure forcing clean output.
    
    # NOTE: The notebook used `response = call_llm(prompt)`.
    # We strip the prompt part to return only the generated answer.
    # Since `inputs` are passed, `generate` returns full sequence (prompt+completion).
    
    input_len = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_len:]
    clean_response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # ---------------------------------------------------------
    # Safety Boilerplate Cleaner
    # ---------------------------------------------------------
    # Some models append "Do NOT provide..." constraints.
    # We use aggressive filtering to keep the UI clean.
    lines = clean_response.split('\n')
    filtered_lines = []
    for line in lines:
        l = line.strip()
        # Filter out lines that look like safety rules
        # Catches: "Do NOT provide...", "Do NOT give...", "5. Do NOT..."
        if "Do NOT" in l or "financial advice that is" in l or "legal or tax advice" in l:
            continue
        if "Provide a clear" in l and "response" in l:
            continue
        filtered_lines.append(line)
        
    final_output = "\n".join(filtered_lines).strip()
    
    # Fallback: If aggressive filtering removed everything, return the raw response 
    # (unless it was truly just a refusal, but better to show something than nothing).
    if not final_output and clean_response:
        return clean_response
        
    return final_output
