"""
Main application for YouTube Sentiment Analysis & Insights Chatbot
"""
import os
import sys
import json
from collections import Counter

# Handle both relative and absolute imports
try:
    # Try relative imports first (when running as module)
    from .youtube_api import fetch_comments, fetch_all_comments
    from .language_processor import detect_language, translate_to_english
    from .sentiment_analyzer import analyze_sentiment, detect_toxicity
    from .dashboard import create_dashboard
    from .chatbot import initialize_chatbot, ask_question
except ImportError:
    # Fall back to absolute imports (when running as script)
    try:
        from youtube_sentiment.youtube_api import fetch_comments, fetch_all_comments
        from youtube_sentiment.language_processor import detect_language, translate_to_english
        from youtube_sentiment.sentiment_analyzer import analyze_sentiment, detect_toxicity
        from youtube_sentiment.dashboard import create_dashboard
        from youtube_sentiment.chatbot import initialize_chatbot, ask_question
    except ImportError:
        # Add the parent directory to sys.path and try again
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        from youtube_sentiment.youtube_api import fetch_comments, fetch_all_comments
        from youtube_sentiment.language_processor import detect_language, translate_to_english
        from youtube_sentiment.sentiment_analyzer import analyze_sentiment, detect_toxicity
        from youtube_sentiment.dashboard import create_dashboard
        from youtube_sentiment.chatbot import initialize_chatbot, ask_question

def process_comments(video_url, max_comments=None):
    """
    Process YouTube comments through the full pipeline
    
    Args:
        video_url (str): YouTube video URL
        max_comments (int, optional): Maximum number of comments to process. 
                                     If None, fetches all comments.
        
    Returns:
        list: Processed comments with all analysis results
    """
    if max_comments is None:
        print(f"Fetching ALL comments from: {video_url}")
        comments = fetch_all_comments(video_url)
    else:
        print(f"Fetching comments from: {video_url} (max: {max_comments})")
        comments = fetch_comments(video_url, max_comments)
    
    print(f"Fetched {len(comments)} comments")
    
    processed_comments = []
    
    for i, comment in enumerate(comments):
        if (i + 1) % 50 == 0 or i + 1 == len(comments):
            print(f"Processing comment {i+1}/{len(comments)}")
        
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
    
    return processed_comments

def save_results(processed_comments, filename='results.json'):
    """
    Save processed comments to a JSON file
    
    Args:
        processed_comments (list): Processed comments
        filename (str): Output filename
    """
    # Convert to JSON-serializable format
    serializable_comments = []
    for comment in processed_comments:
        serializable_comment = comment.copy()
        # Convert any non-serializable objects
        serializable_comments.append(serializable_comment)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_comments, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {filename}")

def get_analysis_summary(processed_comments):
    """
    Get summary statistics of the analysis
    
    Args:
        processed_comments (list): Processed comments
        
    Returns:
        dict: Summary statistics with sample comments
    """
    sentiments = [comment['sentiment'] for comment in processed_comments]
    languages = [comment['original_language'] for comment in processed_comments]
    toxic_comments = [comment for comment in processed_comments if comment['is_toxic']]
    
    sentiment_distribution = dict(Counter(sentiments))
    language_distribution = dict(Counter(languages))
    
    # Get sample comments for each sentiment
    positive_comments = [c for c in processed_comments if c['sentiment'] == 'Positive'][:3]
    negative_comments = [c for c in processed_comments if c['sentiment'] == 'Negative'][:3]
    neutral_comments = [c for c in processed_comments if c['sentiment'] == 'Neutral'][:3]
    
    # Extract just the text for context
    sample_comments = {
        'positive': [c['text'][:100] + '...' if len(c['text']) > 100 else c['text'] for c in positive_comments],
        'negative': [c['text'][:100] + '...' if len(c['text']) > 100 else c['text'] for c in negative_comments],
        'neutral': [c['text'][:100] + '...' if len(c['text']) > 100 else c['text'] for c in neutral_comments]
    }
    
    return {
        'total_comments': len(processed_comments),
        'sentiment_distribution': sentiment_distribution,
        'language_distribution': language_distribution,
        'toxic_comments_count': len(toxic_comments),
        'sample_comments': sample_comments
    }

def run_analysis(video_url, fetch_all=False, max_comments=100):
    """
    Run the complete analysis pipeline
    
    Args:
        video_url (str): YouTube video URL
        fetch_all (bool): If True, fetch all comments. If False, use max_comments.
        max_comments (int): Maximum number of comments to process (used only if fetch_all is False)
        
    Returns:
        tuple: (processed_comments, dashboard_data, summary)
    """
    # Process comments
    if fetch_all:
        processed_comments = process_comments(video_url, max_comments=None)
    else:
        processed_comments = process_comments(video_url, max_comments=max_comments)
    
    # Create dashboard
    dashboard_data = create_dashboard(processed_comments)
    
    # Get summary
    summary = get_analysis_summary(processed_comments)
    
    # Save results
    save_results(processed_comments)
    
    return processed_comments, dashboard_data, summary

def interactive_chatbot(model, context_data=None):
    """
    Run interactive chatbot session
    
    Args:
        model (GenerativeModel): Initialized Gemini model
        context_data (dict): Context data for the chatbot
    """
    print("\n--- Chatbot Session ---")
    print("Ask questions about the analysis or type 'exit' to quit.")
    
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ['exit', 'quit']:
            break
            
        if question:
            response = ask_question(model, question, context_data)
            print(f"\nBot: {response}")

def main():
    """Main function to run the application"""
    # Example usage
    video_url = input("Enter YouTube video URL: ").strip()
    
    if not video_url:
        print("No URL provided. Using example URL.")
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    
    # Ask user if they want to fetch all comments
    fetch_all_input = input("Do you want to fetch ALL comments? (y/n, default=n): ").strip().lower()
    fetch_all = fetch_all_input in ['y', 'yes']
    
    try:
        # Run analysis
        if fetch_all:
            processed_comments, dashboard_data, summary = run_analysis(video_url, fetch_all=True)
        else:
            max_comments = input("Enter maximum number of comments to fetch (default=100): ").strip()
            max_comments = int(max_comments) if max_comments.isdigit() else 100
            processed_comments, dashboard_data, summary = run_analysis(video_url, fetch_all=False, max_comments=max_comments)
        
        # Print summary
        print("\n--- Analysis Summary ---")
        print(f"Total Comments: {summary['total_comments']}")
        print(f"Sentiment Distribution: {summary['sentiment_distribution']}")
        print(f"Language Distribution: {summary['language_distribution']}")
        print(f"Toxic Comments: {summary['toxic_comments_count']}")
        
        # Initialize chatbot with a working model
        chatbot_model = initialize_chatbot('models/gemini-flash-latest')
        
        if chatbot_model:
            # Run interactive chatbot
            interactive_chatbot(chatbot_model, summary)
        else:
            print("\nChatbot not available. Check your API configuration.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()