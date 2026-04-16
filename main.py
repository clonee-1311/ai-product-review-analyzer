import streamlit as st
import pandas as pd
import json
import csv
import time
from datetime import datetime
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
    extract_reviews_from_dom
)
from parse import parse_reviews_with_ollama
import os

# Streamlit UI
st.set_page_config(page_title="AI Review Analyzer", layout="wide")
st.title("🎯 AI Product Review Analyzer")
st.markdown("---")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input(
        "🔗 Enter Product URL",
        placeholder="https://www.amazon.in/product-dp/B0XXXXX"
    )
with col2:
    st.write("")
    st.write("")
    scrape_button = st.button("🚀 Scrape & Analyze", type="primary", width="stretch")

# Analysis options
analysis_type = st.radio(
    "Choose Analysis Type:",
    ["Sentiment Analysis", "Review Summarization", "Both"],
    horizontal=True
)

# Session state initialization
if 'reviews_data' not in st.session_state:
    st.session_state.reviews_data = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Step 1: Scrape the Website
if scrape_button and url:
    try:
        with st.spinner("🕷️ Scraping website content..."):
            # Scrape the website
            dom_content = scrape_website(url)
            
            if not dom_content:
                st.error("❌ Failed to scrape website. Please check the URL and try again.")
                st.stop()
            
            body_content = extract_body_content(dom_content)
            cleaned_content = clean_body_content(body_content)
            
            # Store the DOM content in session state
            st.session_state.dom_content = cleaned_content
            
            # Extract reviews
            st.info("📊 Extracting reviews from page...")
            reviews = extract_reviews_from_dom(cleaned_content)
            
            if not reviews:
                st.warning("⚠️ No reviews found on this page. Try a different product URL.")
                st.stop()
            
            st.success(f"✅ Found {len(reviews)} reviews!")
            
            # Parse and analyze reviews
            st.info("🤖 AI is analyzing reviews...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            analyzed_reviews = []
            for i, review in enumerate(reviews):
                status_text.text(f"Processing review {i+1}/{len(reviews)}...")
                
                try:
                    # Parse with Ollama based on analysis type
                    if analysis_type == "Sentiment Analysis":
                        analysis = parse_reviews_with_ollama(
                            [review['text'][:6000]], 
                            "Perform sentiment analysis on this review. Return format: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL' with a brief explanation."
                        )
                        review['sentiment'] = analysis.strip()
                        review['summary'] = ""
                    elif analysis_type == "Review Summarization":
                        analysis = parse_reviews_with_ollama(
                            [review['text'][:6000]], 
                            "Provide a concise one-sentence summary of this review."
                        )
                        review['summary'] = analysis.strip()
                        review['sentiment'] = ""
                    else:  # Both
                        sentiment = parse_reviews_with_ollama(
                            [review['text'][:6000]], 
                            "Perform sentiment analysis. Return only: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'."
                        )
                        summary = parse_reviews_with_ollama(
                            [review['text'][:6000]], 
                            "Provide a concise one-sentence summary."
                        )
                        review['sentiment'] = sentiment.strip()
                        review['summary'] = summary.strip()
                    
                    analyzed_reviews.append(review)
                    
                except Exception as e:
                    st.warning(f"⚠️ Error processing review {i+1}: {str(e)}")
                    review['sentiment'] = "ERROR"
                    review['summary'] = "Processing failed"
                    analyzed_reviews.append(review)
                
                # Update progress
                progress_bar.progress((i + 1) / len(reviews))
                time.sleep(0.5)  # Rate limiting
            
            status_text.text("✅ Analysis complete!")
            st.session_state.reviews_data = analyzed_reviews
            st.session_state.analysis_complete = True
            
    except Exception as e:
        st.error(f"❌ Error during scraping: {str(e)}")

# Display Results
if st.session_state.analysis_complete and st.session_state.reviews_data:
    st.markdown("---")
    st.header("📈 Analysis Results")
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.reviews_data)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        if 'rating' in df.columns:
            try:
                # Extract numeric rating values
                ratings = df['rating'].str.extract(r'(\d+\.?\d*)')[0]
                avg_rating = ratings.astype(float).mean()
                if not pd.isna(avg_rating):
                    st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
                else:
                    st.metric("Average Rating", "N/A")
            except:
                st.metric("Average Rating", "N/A")
    with col3:
        if 'sentiment' in df.columns and len(df) > 0 and df['sentiment'].iloc[0] != "":
            sentiment_counts = df['sentiment'].str.upper().value_counts()
            positive_count = sentiment_counts.get('POSITIVE', 0)
            if len(df) > 0:
                positive_pct = (positive_count / len(df)) * 100
                st.metric("Positive Reviews", f"{positive_pct:.1f}%")
            else:
                st.metric("Positive Reviews", "0%")
        else:
            st.metric("Positive Reviews", "N/A")
    with col4:
        st.metric("Analysis Type", analysis_type)
    
    st.markdown("---")
    
    # Display reviews table
    st.subheader("📋 Detailed Review Analysis")
    
    # Select columns to display
    display_columns = ['text', 'rating', 'date', 'author']
    if analysis_type in ["Sentiment Analysis", "Both"]:
        display_columns.append('sentiment')
    if analysis_type in ["Review Summarization", "Both"]:
        display_columns.append('summary')
    
    # Filter columns that exist
    available_columns = [col for col in display_columns if col in df.columns]
    st.dataframe(df[available_columns], width="stretch")
    
    # Export Options
    st.markdown("---")
    st.subheader("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    # CSV Export
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"reviews_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )
    
    # JSON Export
    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name=f"reviews_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            width="stretch"
        )
    
    # Show raw DOM content in expander
    with st.expander("🔍 View Raw Page Content"):
        preview_text = st.session_state.dom_content[:5000] + "..." if len(st.session_state.dom_content) > 5000 else st.session_state.dom_content
        st.text_area("DOM Content", preview_text, height=200)

elif not scrape_button:
    st.info("👆 Enter a product URL and click 'Scrape & Analyze' to begin!")
    
    # Example URLs
    st.markdown("### 📝 Example URLs to Try:")
    st.markdown("""
    - **Amazon**: `https://www.amazon.in/Samsung-Galaxy-Storage-Without-Charger/dp/B0BZCR6TNK/`
    - **Amazon Speakers**: `https://www.amazon.in/eMeet-Wireless-Bluetooth-Outdoor-Speaker/dp/B07CSRB6SH/`
    - **Best Buy**: `https://www.bestbuy.com/site/reviews/apple-airpods-pro-2nd-generation/6447382`
    """)