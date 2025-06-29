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
        background-color: #f0fff4;
    }
    .negative {
        color: #FF0000;
        background-color: #fff0f0;
    }
    .neutral {
        color: #CCCCCC;
        background-color: #f8f9fa;
    }
    .comment-box {
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .rating-badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎵 YouTube Song Comment Analyzer")
    st.markdown("Analyze sentiment of comments on any YouTube song")
    
    # Initialize session state for comments if not exists
    if 'analyzed_comments' not in st.session_state:
        st.session_state.analyzed_comments = []
    
    if 'video_id' not in st.session_state:
        st.session_state.video_id = ""
    
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
            
            # Store in session state
            st.session_state.analyzed_comments = analyzed_comments
            st.session_state.video_id = video_id
            
            st.success(f"Analyzed {len(analyzed_comments)} comments for video ID: {video_id}")
    
    # Only show sorting and results if we have comments
    if st.session_state.analyzed_comments:
        # Sorting options - using columns for better layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            sort_option = st.selectbox(
                "Sort comments by",
                ["Highest Rating", "Most Positive", "Most Negative", "Most Likes", "Newest First"],
                key="sort_option"
            )
        
        with col2:
            display_limit = st.slider(
                "Number of comments to display",
                5, min(50, len(st.session_state.analyzed_comments)), 
                10,
                key="display_limit"
            )
        
        # Sort comments based on selection - doesn't trigger rerun
        if st.session_state.analyzed_comments:
            comments_to_display = st.session_state.analyzed_comments.copy()
            
            if sort_option == "Highest Rating":
                comments_to_display.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_option == "Most Positive":
                comments_to_display.sort(key=lambda x: x['sentiment'], reverse=True)
            elif sort_option == "Most Negative":
                comments_to_display.sort(key=lambda x: x['sentiment'])
            elif sort_option == "Most Likes":
                comments_to_display.sort(key=lambda x: x['likes'], reverse=True)
            elif sort_option == "Newest First":
                comments_to_display.sort(key=lambda x: x['published_at'], reverse=True)
        
        # Display comments
        st.subheader("Comment Analysis Results")
        
        for comment in comments_to_display[:display_limit]:
            sentiment_class = comment['label']
            rating_color = "#1DB954" if comment['rating'] >= 7 else "#FF0000" if comment['rating'] <= 4 else "#FFA500"
            
            st.markdown(f"""
            <div class="comment-box {sentiment_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: bold; font-size: 1.1em;">{comment['author']}</div>
                    <div class="rating-badge" style="background-color: {rating_color}; color: white;">
                        {comment['rating']}/10
                    </div>
                </div>
                <p style="margin: 8px 0; font-size: 0.95em;">{comment['comment']}</p>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #666;">
                    <span>👍 {comment['likes']} likes</span>
                    <span class="{sentiment_class}" style="font-weight: bold;">{sentiment_class.capitalize()} sentiment ({comment['sentiment']:.2f})</span>
                    <span>{comment['published_at'][:10]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show statistics
        positive_count = sum(1 for c in st.session_state.analyzed_comments if c['label'] == 'positive')
        negative_count = sum(1 for c in st.session_state.analyzed_comments if c['label'] == 'negative')
        neutral_count = sum(1 for c in st.session_state.analyzed_comments if c['label'] == 'neutral')
        
        st.markdown(f"""
        <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
            <h4 style="margin-top: 0;">Overall Sentiment Distribution</h4>
            <div style="display: flex; justify-content: space-between;">
                <span class="positive">Positive: {positive_count} ({positive_count/len(st.session_state.analyzed_comments)*100:.1f}%)</span>
                <span class="neutral">Neutral: {neutral_count} ({neutral_count/len(st.session_state.analyzed_comments)*100:.1f}%)</span>
                <span class="negative">Negative: {negative_count} ({negative_count/len(st.session_state.analyzed_comments)*100:.1f}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()