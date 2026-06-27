import os
from typing import List, Dict, Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _build_prompt(reviews: List[Dict]) -> str:
    sample_texts = "\n\n".join([r.get("text", "") for r in reviews[:50]])
    prompt = f"""
You are an expert product analyst. Given the following user reviews, produce:
1) A concise summary.
2) Top themes (3-8) as bullet points.
3) Top issues (3-6) ranked.
4) User segments and unmet needs.
5) 10 representative quotes.

Reviews:
{sample_texts}
"""
    return prompt


def analyze_reviews(reviews: List[Dict], api_key: str = None) -> Dict[str, Any]:
    prompt = _build_prompt(reviews)

    # Prefer OpenAI client if available, otherwise fallback to simple request via requests
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"error": "No API key provided. Set OPENAI_API_KEY or pass api_key."}

    if OpenAI is not None:
        client = OpenAI(api_key=key)
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful analyst."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            text = resp["choices"][0]["message"]["content"]
        except Exception:
            import requests

            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful analyst."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
            }
            r = requests.post(url, headers=headers, json=data, timeout=60)
            r.raise_for_status()
            j = r.json()
            text = j["choices"][0]["message"]["content"]

    # Very simple parsing: return raw and leave structured extraction for later
    return {"raw": text}
