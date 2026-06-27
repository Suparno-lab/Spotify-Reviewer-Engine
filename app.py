import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from scrapper import load_sample_reviews, fetch_play_store_reviews
from analyzer import analyze_reviews, DEFAULT_QUESTIONS


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

st.sidebar.markdown("---")
st.sidebar.header("Custom Questions (Optional)")
add_custom = st.sidebar.checkbox("Add custom research questions?")
custom_questions = None
if add_custom:
    custom_input = st.sidebar.text_area(
        "Enter questions (one per line):",
        height=100,
        placeholder="e.g.\nWhat features do users want most?\nHow satisfied are users?"
    )
    if custom_input.strip():
        custom_questions = [q.strip() for q in custom_input.split("\n") if q.strip()]

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
                report = analyze_reviews(reviews, api_key=GOOGLE_API_KEY, custom_questions=custom_questions)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                report = {"error": str(e)}

        st.header("AI Analysis")
        if isinstance(report, dict):
            # Display structured Q&A if available
            if "questions_and_answers" in report:
                st.subheader("Research Findings")
                
                # Display each Q&A
                for i, qa in enumerate(report.get("questions_and_answers", []), 1):
                    with st.expander(f"**Q{i}: {qa.get('question', 'N/A')}**"):
                        st.markdown(f"**Answer:** {qa.get('answer', 'N/A')}")
                        
                        if qa.get("supporting_quotes"):
                            st.markdown("**Supporting Quotes:**")
                            for quote in qa.get("supporting_quotes", []):
                                st.info(f"*\"{quote}\"*")
                        
                        if qa.get("patterns"):
                            st.markdown("**Key Patterns:**")
                            for pattern in qa.get("patterns", []):
                                st.write(f"• {pattern}")
                
                # Overall summary
                if report.get("overall_summary"):
                    st.markdown("---")
                    st.subheader("Overall Summary")
                    st.write(report.get("overall_summary"))
            
            # Fallback to raw output if structured parsing failed
            elif "raw" in report:
                st.subheader("Analysis Output")
                st.write(report["raw"])
            
            # Show error if present
            if "error" in report:
                st.warning(f"⚠ {report['error']}")

        st.sidebar.markdown("---")
        st.sidebar.write("Fetched reviews preview:")
        for r in (reviews[:10] if reviews else []):
            st.sidebar.write(r.get("text")[:140])

else:
    st.info("Choose a source and click 'Fetch & Analyze' to start the demo.")
    
    st.markdown("---")
    st.markdown("### Default Research Questions")
    st.write("The analyzer will answer these questions by default:")
    for i, q in enumerate(DEFAULT_QUESTIONS, 1):
        st.write(f"{i}. {q}")
