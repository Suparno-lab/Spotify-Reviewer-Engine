import os
from typing import List, Dict, Any

try:
    import google.generativeai as genai
except Exception:
    genai = None


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

    # Use Google Gemini API
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key or key.strip() == "":
        return {"error": "No API key provided. Set GOOGLE_API_KEY in Streamlit secrets or paste in sidebar. Get free at ai.google.dev"}

    key = key.strip()  # Remove any whitespace

    if genai is None:
        raise RuntimeError("google-generativeai library not installed. Run: pip install google-generativeai")
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    text = response.text

    # Very simple parsing: return raw and leave structured extraction for later
    return {"raw": text}
