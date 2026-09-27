import os
import logging
from typing import Optional
from app.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def is_gemini_available(api_key: Optional[str] = None) -> bool:
    """
    Check if a valid Gemini API key is configured in app config, env vars, or passed directly.
    """
    key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
    return bool(key and key.strip() and not key.startswith("your_"))

def call_gemini_api(
    prompt: str,
    system_instruction: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Calls the Google Gemini API with seamless fallback mechanisms.
    Tries google-genai SDK if available, or direct HTTP REST endpoint.
    Returns None if key is absent, invalid, or API request fails.
    """
    key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
    if not key or not key.strip() or key.startswith("your_"):
        return None

    # Attempt 1: Try using official google-genai SDK if available
    try:
        from google import genai
        client = genai.Client(api_key=key)
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        if temperature:
            config["temperature"] = temperature

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config if config else None
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.debug(f"google-genai SDK call skipped/failed: {e}")

    # Attempt 2: Direct REST call using requests
    try:
        import requests
        models_to_try = [model_name, "gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        unique_models = []
        for m in models_to_try:
            if m not in unique_models:
                unique_models.append(m)

        for mod in unique_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={key}"
            headers = {"Content-Type": "application/json"}

            contents = []
            if system_instruction:
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"System Instruction: {system_instruction}"}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood. I will act strictly according to these instructions."}]
                })

            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 1024
                }
            }

            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            elif resp.status_code in [404, 400]:
                continue
            else:
                logger.warning(f"Gemini REST API error {resp.status_code}: {resp.text}")
                break
    except Exception as ex:
        logger.error(f"Error executing Gemini API call: {ex}")

    return None
