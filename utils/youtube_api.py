from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import re

load_dotenv()

def extract_video_id(url):
    # Extract video ID from URL
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_comments(video_id, max_results=100):
    youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
    
    try:
        # Get video details to confirm it's a music video
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            return None, "Video not found"
        
        # Get comments
        comments = []
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText'
        )
        
        while request and len(comments) < max_results:
            response = request.execute()
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'likes': comment['likeCount']
                })
            
            request = youtube.commentThreads().list_next(request, response)
        
        return comments, None
    except Exception as e:
        return None, str(e)