"""
Main Flask application for YouTube Sentiment Analysis
"""
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
import json
from typing import Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from youtube_sentiment.models import db, User, SearchHistory, LoginHistory, CommentAnalysis
from youtube_sentiment.auth import auth
from youtube_sentiment.youtube_api import get_video_id

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///youtube_sentiment.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Custom filter for JSON parsing in templates
    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except:
            return {}
    
    # Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard/')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/analyze', methods=['POST'])
    @login_required
    def api_analyze():
        """API endpoint for analyzing YouTube comments"""
        data = request.get_json()
        youtube_url = data.get('url')
        max_comments = data.get('max_comments', 100)
        fetch_all = data.get('fetch_all', False)
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        try:
            # Import analysis functions here to avoid circular imports
            from youtube_sentiment.youtube_api import fetch_comments, fetch_all_comments
            from youtube_sentiment.language_processor import detect_language, translate_to_english
            from youtube_sentiment.sentiment_analyzer import analyze_sentiment, detect_toxicity
            
            # Fetch comments
            if fetch_all:
                comments = fetch_all_comments(youtube_url)
            else:
                comments = fetch_comments(youtube_url, max_comments)
            
            # Process comments
            processed_comments = []
            for comment in comments:
                # Detect language
                original_language = detect_language(comment['text'])
                
                # Translate if not English
                if original_language != 'en':
                    translated_text = translate_to_english(comment['text'])
                else:
                    translated_text = comment['text']
                
                # Perform sentiment analysis
                sentiment_result = analyze_sentiment(translated_text)
                
                # Detect toxicity
                is_toxic = detect_toxicity(translated_text)
                
                # Combine all results
                processed_comment = {
                    **comment,
                    'original_language': original_language,
                    'translated_text': translated_text,
                    'sentiment': sentiment_result['sentiment'],
                    'polarity': sentiment_result['polarity'],
                    'is_toxic': is_toxic
                }
                
                processed_comments.append(processed_comment)
            
            # Calculate summary statistics
            sentiments = [comment['sentiment'] for comment in processed_comments]
            languages = [comment['original_language'] for comment in processed_comments]
            from collections import Counter
            sentiment_distribution = dict(Counter(sentiments))
            language_distribution = dict(Counter(languages))
            
            # Save to database
            video_id = get_video_id(youtube_url)
            if video_id:
                # Create search history record
                search_history = SearchHistory(
                    user_id=current_user.id,
                    youtube_url=youtube_url,
                    video_id=video_id,
                    total_comments=len(processed_comments),
                    sentiment_distribution=json.dumps(sentiment_distribution),
                    language_distribution=json.dumps(language_distribution)
                )
                db.session.add(search_history)  # type: ignore
                db.session.commit()  # type: ignore
                
                # Save individual comments (limit to first 50 for performance)
                for comment in processed_comments[:50]:
                    comment_analysis = CommentAnalysis(
                        search_id=search_history.id,
                        comment_id=comment['id'],
                        author=comment['author'],
                        text=comment['text'],
                        original_language=comment['original_language'],
                        sentiment=comment['sentiment'],
                        polarity=comment['polarity'],
                        is_toxic=comment['is_toxic']
                    )
                    db.session.add(comment_analysis)  # type: ignore
                
                db.session.commit()  # type: ignore
            
            return jsonify({
                'success': True,
                'comments': processed_comments,
                'total_comments': len(processed_comments),
                'sentiment_distribution': sentiment_distribution,
                'language_distribution': language_distribution,
                'sample_comments': {
                    'positive': [c['text'] for c in processed_comments if c['sentiment'] == 'Positive'][:5],
                    'negative': [c['text'] for c in processed_comments if c['sentiment'] == 'Negative'][:5],
                    'neutral': [c['text'] for c in processed_comments if c['sentiment'] == 'Neutral'][:5]
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/chatbot', methods=['POST'])
    @login_required
    def api_chatbot():
        """API endpoint for chatbot interactions"""
        data = request.get_json()
        question = data.get('question')
        context = data.get('context', {})
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        try:
            # Import chatbot functions
            from youtube_sentiment.chatbot import initialize_chatbot, ask_question
            
            # Initialize chatbot with None to let it choose the best available model
            model = initialize_chatbot(None)
            if not model:
                return jsonify({'error': 'Chatbot not available. Please check your API configuration.'}), 500
            
            # Use the context data as-is, but ensure it has the required structure
            # The frontend already provides properly structured data
            context_data = context
            
            # Ask question
            response = ask_question(model, question, context_data)
            return jsonify({'response': response})
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Chatbot error: {error_details}")
            return jsonify({'error': f'Internal error: {str(e)}'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)