import json
import os
from typing import List, Dict


def load_sample_reviews(path: str = "reviews_sample.json") -> List[Dict]:
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def fetch_play_store_reviews(package_name: str = "com.spotify.music", count: int = 200):
    try:
        from google_play_scraper import reviews as gp_reviews, Sort
    except Exception as e:
        raise RuntimeError("google_play_scraper package is required for Play Store scraping. Add it to requirements.txt") from e

    results, _ = gp_reviews(package_name, lang="en", country="us", sort=Sort.NEWEST, count=count)
    out = []
    for r in results:
        out.append({
            "source": "play_store",
            "id": r.get("reviewId") or r.get("reviewId"),
            "author": r.get("userName"),
            "rating": r.get("score"),
            "text": r.get("content"),
            "at": r.get("at") and r.get("at").isoformat() if r.get("at") else None,
        })
    return out
