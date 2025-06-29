import streamlit as st
import requests
from utils.youtube_api import extract_video_id, get_video_comments
from utils.sentiment_analysis import analyze_comment_sentiment
from dotenv import load_dotenv
import os
import time

load_dotenv()

# MCP Server URL
MCP_SERVER = "http://localhost:5000"

# Page config
st.set_page_config(
    page_title="YouTube Song Comment Analyzer",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1DB954;
    }
    .stTextInput > div > div > input {
        color: #1DB954;
    }
    .positive {
        color: #1DB954;
    }
    .negative {
        color: #FF0000;
    }
    .neutral {
        color: #CCCCCC;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎵 YouTube Song Comment Analyzer")
    st.markdown("Analyze sentiment of comments on any YouTube song")
    
    # Input section
    with st.form("input_form"):
        youtube_url = st.text_input("Enter YouTube Song URL", placeholder="https://www.youtube.com/watch?v=...")
        comment_limit = st.slider("Number of comments to analyze", 10, 200, 50)
        submit_button = st.form_submit_button("Analyze Comments")
    
    if submit_button and youtube_url:
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
            return
        
        with st.spinner("Fetching and analyzing comments..."):
            progress_bar = st.progress(0)
            
            # Step 1: Get comments from YouTube
            comments, error = get_video_comments(video_id, comment_limit)
            if error:
                st.error(f"Error fetching comments: {error}")
                return
            
            progress_bar.progress(30)
            
            # Step 2: Analyze sentiment
            analyzed_comments = []
            for i, comment in enumerate(comments):
                sentiment = analyze_comment_sentiment(comment['text'])
                analyzed_comments.append({
                    'song_id': video_id,
                    'author': comment['author'],
                    'comment': comment['text'],
                    'likes': comment['likes'],
                    'published_at': comment['published_at'],
                    'sentiment': sentiment['sentiment'],
                    'rating': sentiment['rating'],
                    'label': sentiment['label']
                })
                progress_bar.progress(30 + int(40 * (i + 1) / len(comments)))
            
            progress_bar.progress(80)
            
            # Step 3: Store in MongoDB via MCP
            try:
                response = requests.post(
                    f"{MCP_SERVER}/store_comments",
                    json={"comments": analyzed_comments}
                )
                if response.status_code != 200:
                    st.warning(f"Comments couldn't be saved to database: {response.json().get('message')}")
            except Exception as e:
                st.warning(f"Couldn't connect to database: {str(e)}")
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            
            # Display results
            st.success(f"Analyzed {len(analyzed_comments)} comments for video ID: {video_id}")
            
            # Sorting options
            col1, col2 = st.columns(2)
            with col1:
                sort_option = st.selectbox(
                    "Sort comments by",
                    ["Highest Rating", "Most Positive", "Most Negative"],
                    key="sort_option"
                )
            
            with col2:
                display_limit = st.slider(
                    "Number of comments to display",
                    5, 50, 10,
                    key="display_limit"
                )
            
            # Sort comments
            if sort_option == "Highest Rating":
                analyzed_comments.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_option == "Most Positive":
                analyzed_comments.sort(key=lambda x: x['sentiment'], reverse=True)
            else:
                analyzed_comments.sort(key=lambda x: x['sentiment'])
            
            # Display comments
            st.subheader("Comment Analysis Results")
            
            for comment in analyzed_comments[:display_limit]:
                sentiment_class = comment['label']
                st.markdown(f"""
                <div class="comment-box" style="border-left: 4px solid {'#1DB954' if sentiment_class == 'positive' else '#FF0000' if sentiment_class == 'negative' else '#CCCCCC'}; 
                    padding: 10px; margin: 10px 0; background-color: #f8f9fa; border-radius: 0 8px 8px 0">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{comment['author']}</strong>
                        <span>Rating: <strong>{comment['rating']}/10</strong></span>
                    </div>
                    <p style="margin: 5px 0;">{comment['comment']}</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #666;">
                        <span>👍 {comment['likes']} likes</span>
                        <span class="{sentiment_class}">{sentiment_class.capitalize()} sentiment</span>
                        <span>{comment['published_at'][:10]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()