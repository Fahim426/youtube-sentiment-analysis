"""
Module for fetching YouTube comments using YouTube Data API v3
"""
import os
import re
import sys

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import config properly
try:
    from config import YOUTUBE_API_KEY, MAX_COMMENTS
except ImportError:
    # Fallback for direct execution - try absolute import
    try:
        import config
        YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
        MAX_COMMENTS = config.MAX_COMMENTS
    except ImportError:
        # If all else fails, set default values
        YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
        MAX_COMMENTS = int(os.getenv('MAX_COMMENTS', 100))

from googleapiclient.discovery import build

def get_video_id(url):
    """
    Extract video ID from YouTube URL
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Video ID or None if not found
    """
    if not url:
        return None
        
    # Handle different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
    ]
    
    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matched, try simple extraction
    if 'v=' in url:
        # Extract video ID from v parameter
        start = url.find('v=') + 2
        end = url.find('&', start)
        if end == -1:
            end = len(url)
        video_id = url[start:end]
        # Validate video ID length (should be 11 characters)
        if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id):
            return video_id
    
    return None

def fetch_all_comments(video_url):
    """
    Fetch all comments from a YouTube video
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        list: List of all comments with metadata
    """
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL or unable to extract video ID")
    
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key not found. Please set YOUTUBE_API_KEY in .env file")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    comments = []
    next_page_token = None
    
    print("Fetching all comments (this may take a while)...")
    
    while True:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,  # Maximum allowed per request
            order='relevance',
            pageToken=next_page_token
        )
        
        try:
            response = request.execute()
        except Exception as e:
            raise Exception(f"Error fetching comments: {str(e)}")
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'id': item['id'],
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt'],
                'like_count': comment['likeCount'],
                'updated_at': comment['updatedAt']
            })
        
        next_page_token = response.get('nextPageToken')
        print(f"Fetched {len(comments)} comments so far...")
        
        # If there's no next page token, we've got all comments
        if not next_page_token:
            break
    
    print(f"Finished fetching. Total comments: {len(comments)}")
    return comments

def fetch_comments(video_url, max_results=MAX_COMMENTS):
    """
    Fetch top comments from a YouTube video (limited by max_results)
    
    Args:
        video_url (str): YouTube video URL
        max_results (int): Maximum number of comments to fetch
        
    Returns:
        list: List of comments with metadata
    """
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL or unable to extract video ID")
    
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key not found. Please set YOUTUBE_API_KEY in .env file")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    comments = []
    next_page_token = None
    
    while len(comments) < max_results:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            order='relevance',
            pageToken=next_page_token
        )
        
        try:
            response = request.execute()
        except Exception as e:
            raise Exception(f"Error fetching comments: {str(e)}")
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'id': item['id'],
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt'],
                'like_count': comment['likeCount'],
                'updated_at': comment['updatedAt']
            })
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return comments[:max_results]