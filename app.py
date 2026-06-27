import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from scrapper import load_sample_reviews, fetch_play_store_reviews
from analyzer import analyze_reviews


st.set_page_config(page_title="Review Discovery Engine", layout="wide")

st.title("AI-powered Review Discovery Engine — Demo")

st.sidebar.header("Configuration")
# Check Streamlit secrets first, then environment, then sidebar input
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    try:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    except:
        GOOGLE_API_KEY = ""

# Allow override from sidebar
sidebar_key = st.sidebar.text_input("Google Gemini API key (get free at ai.google.dev)", value="", type="password")
if sidebar_key:
    GOOGLE_API_KEY = sidebar_key

# Debug: show if key was detected
if GOOGLE_API_KEY:
    st.sidebar.success("✓ Google Gemini API key detected")
else:
    st.sidebar.warning("⚠ No Google Gemini API key found. Get free at ai.google.dev or paste above.")

source = st.sidebar.selectbox("Data source", ["sample", "play_store"])

if source == "play_store":
    pkg = st.sidebar.text_input("Play Store package name", value="com.spotify.music")
    count = st.sidebar.number_input("Reviews to fetch", min_value=10, max_value=500, value=100, step=10)
else:
    pkg = None
    count = None

if st.sidebar.button("Fetch & Analyze"):
    with st.spinner("Fetching reviews..."):
        if source == "sample":
            reviews = load_sample_reviews()
        else:
            try:
                reviews = fetch_play_store_reviews(pkg, int(count))
            except Exception as e:
                st.error(f"Failed to fetch Play Store reviews: {e}")
                reviews = []

    if not reviews:
        st.warning("No reviews found — try the sample data or increase count.")
    else:
        st.success(f"Loaded {len(reviews)} reviews — running analysis...")
        with st.spinner("Analyzing reviews with the AI..."):
            try:
                report = analyze_reviews(reviews, api_key=GOOGLE_API_KEY)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                report = {"error": str(e)}

        st.header("AI Analysis")
        if isinstance(report, dict):
            if "raw" in report and len(report) == 1:
                st.subheader("Raw model output")
                st.text(report["raw"])
            else:
                st.subheader("Summary")
                st.write(report.get("summary"))

                st.subheader("Themes")
                for t in report.get("themes", []):
                    st.write(f"- {t}")

                st.subheader("Top Issues")
                for it in report.get("top_issues", []):
                    st.write(f"- {it}")

                st.subheader("Segments & Unmet Needs")
                st.write(report.get("segments"))

                st.subheader("Sample Quotes")
                for q in report.get("sample_quotes", [])[:10]:
                    st.info(q)

        st.sidebar.markdown("---")
        st.sidebar.write("Fetched reviews preview:")
        for r in (reviews[:10] if reviews else []):
            st.sidebar.write(r.get("text")[:140])

else:
    st.info("Choose a source and click 'Fetch & Analyze' to start the demo.")
