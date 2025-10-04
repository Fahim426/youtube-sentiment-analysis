import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Number of comments to fetch (when not fetching all)
MAX_COMMENTS = 1000

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL') or 'sqlite:///youtube_sentiment.db'
SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here-change-in-production'