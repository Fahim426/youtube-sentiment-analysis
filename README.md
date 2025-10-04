# YouTube Sentiment Analysis & Insights Chatbot

A comprehensive web application that analyzes YouTube comments for sentiment, language, and toxicity, with an AI-powered chatbot for insights.

## Features

- **YouTube Comment Analysis**: Fetch and analyze comments from any YouTube video
- **Multilingual Support**: Automatic language detection and translation
- **Sentiment Analysis**: Classify comments as positive, negative, or neutral
- **Toxicity Detection**: Identify potentially harmful or toxic comments
- **Interactive Dashboard**: Visualize analysis results with charts and graphs
- **AI Chatbot**: Ask questions about the analysis using Google's Gemini AI
- **User Authentication**: Secure login and registration system
- **Search History**: Track and review previous analyses
- **Responsive Design**: Works on desktop and mobile devices

## Technologies Used

- Python 3.x
- Flask web framework
- SQLAlchemy for database management
- YouTube Data API v3
- Google Generative AI (Gemini)
- TextBlob for sentiment analysis
- langdetect for language detection
- Bootstrap 5 for frontend

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   GOOGLE_API_KEY=your_google_api_key
   SECRET_KEY=your_secret_key
   ```
4. Initialize the database: `python init_db.py`
5. Run the application: `python run.py`

## Usage

1. Navigate to `http://localhost:5000`
2. Register for an account or log in
3. Enter a YouTube video URL
4. Analyze the comments
5. Interact with the AI chatbot to gain insights


## License

This project is licensed under the MIT License.
