import os
import json
from typing import List, Dict, Any

try:
    import google.generativeai as genai
except Exception:
    genai = None


# Default research questions
DEFAULT_QUESTIONS = [
    "Why do users struggle to discover new music?",
    "What are the most common frustrations with recommendations?",
    "What listening behaviors are users trying to achieve?",
    "What causes users to repeatedly listen to the same content?",
    "Which user segments experience different discovery challenges?",
    "What unmet needs emerge consistently across reviews?"
]


def _build_prompt(reviews: List[Dict], questions: List[str] = None) -> str:
    if questions is None:
        questions = DEFAULT_QUESTIONS
    
    sample_texts = "\n\n".join([r.get("text", "") for r in reviews[:100]])
    
    questions_str = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    
    prompt = f"""You are an expert product analyst. Analyze the following user reviews and answer each question with specific insights, patterns, and supporting evidence.

REVIEWS:
{sample_texts}

QUESTIONS TO ANSWER:
{questions_str}

For each question, provide:
- A clear, concise answer (2-3 sentences)
- 2-3 specific supporting quotes from the reviews
- Any relevant user segments or patterns

Format your response as JSON with this exact structure:
{{
  "questions_and_answers": [
    {{
      "question": "Question text",
      "answer": "Your answer",
      "supporting_quotes": ["Quote 1", "Quote 2", "Quote 3"],
      "patterns": ["Pattern 1", "Pattern 2"]
    }}
  ],
  "overall_summary": "Brief overall summary of key insights"
}}"""
    return prompt


def analyze_reviews(reviews: List[Dict], api_key: str = None, custom_questions: List[str] = None) -> Dict[str, Any]:
    questions = custom_questions if custom_questions else DEFAULT_QUESTIONS
    prompt = _build_prompt(reviews, questions)

    # Use Google Gemini API
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key or key.strip() == "":
        return {"error": "No API key provided. Set GOOGLE_API_KEY in Streamlit secrets or paste in sidebar. Get free at ai.google.dev"}

    key = key.strip()  # Remove any whitespace

    if genai is None:
        raise RuntimeError("google-generativeai library not installed. Run: pip install google-generativeai")
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    response = model.generate_content(prompt)
    text = response.text

    # Try to parse as JSON, fallback to raw text
    try:
        # Extract JSON from response (in case there's markdown formatting)
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0]
        
        result = json.loads(json_str)
        return result
    except Exception:
        # Return raw text if JSON parsing fails
        return {"raw": text, "error": "Could not parse structured response"}
