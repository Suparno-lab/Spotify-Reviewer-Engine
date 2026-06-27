import os
from typing import List, Dict, Any

try:
    from groq import Groq
except Exception:
    Groq = None


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

    # Prefer Groq client if available, otherwise fallback to simple request via requests
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key or key.strip() == "":
        return {"error": "No API key provided. Set GROQ_API_KEY in Streamlit secrets or paste in sidebar. Get free at console.groq.com"}

    key = key.strip()  # Remove any whitespace

    if Groq is None:
        raise RuntimeError("Groq library not installed. Run: pip install groq")
    
    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=2048,
    )
    text = resp.choices[0].message.content

    # Very simple parsing: return raw and leave structured extraction for later
    return {"raw": text}
