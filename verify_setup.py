import os
from importlib import util

def check_pkg(name):
    spec = util.find_spec(name)
    return spec is not None

reqs = ["streamlit", "dotenv", "openai", "google_play_scraper"]
missing = [r for r in reqs if not check_pkg(r)]
if missing:
    print("Missing packages:", missing)
    print("Run: python -m pip install -r requirements.txt")
else:
    print("All required packages appear installed.")
