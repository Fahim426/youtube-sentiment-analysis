"""
Run script for YouTube Sentiment Analysis application
"""
import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_sentiment.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)