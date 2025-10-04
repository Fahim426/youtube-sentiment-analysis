"""
Module for creating dashboard visualizations
"""
from collections import Counter

def create_sentiment_chart(sentiment_data):
    """
    Create a pie chart showing sentiment distribution
    
    Args:
        sentiment_data (list): List of sentiment labels
        
    Returns:
        plotly.graph_objects.Figure: Pie chart figure
    """
    # We'll import plotly inside the function to avoid import issues
    try:
        import plotly.express as px
    except ImportError:
        print("Plotly not installed. Please install with: pip install plotly")
        return None
    
    sentiment_counts = Counter(sentiment_data)
    
    fig = px.pie(
        names=list(sentiment_counts.keys()),
        values=list(sentiment_counts.values()),
        title="Sentiment Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    return fig

def create_language_chart(language_data):
    """
    Create a bar chart showing language distribution
    
    Args:
        language_data (list): List of language codes
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # We'll import plotly inside the function to avoid import issues
    try:
        import plotly.express as px
    except ImportError:
        print("Plotly not installed. Please install with: pip install plotly")
        return None
    
    language_counts = Counter(language_data)
    
    fig = px.bar(
        x=list(language_counts.keys()),
        y=list(language_counts.values()),
        title="Language Distribution",
        labels={'x': 'Language', 'y': 'Number of Comments'},
        color=list(language_counts.values()),
        color_continuous_scale='Blues'
    )
    
    return fig

def get_top_comments(comments_data, sentiment, top_n=5):
    """
    Get top N comments based on sentiment
    
    Args:
        comments_data (list): List of comment dictionaries
        sentiment (str): Sentiment to filter by ('Positive' or 'Negative')
        top_n (int): Number of top comments to return
        
    Returns:
        list: Top N comments with highest polarity scores
    """
    # Filter comments by sentiment
    filtered_comments = [comment for comment in comments_data if comment['sentiment'] == sentiment]
    
    # Sort by polarity score (absolute value for negative sentiment)
    if sentiment == 'Positive':
        sorted_comments = sorted(filtered_comments, key=lambda x: x['polarity'], reverse=True)
    else:  # Negative
        sorted_comments = sorted(filtered_comments, key=lambda x: x['polarity'])
    
    return sorted_comments[:top_n]

def create_dashboard(processed_comments):
    """
    Create dashboard with all visualizations
    
    Args:
        processed_comments (list): List of processed comment dictionaries
        
    Returns:
        dict: Dictionary containing all dashboard figures
    """
    # Extract data for visualizations
    sentiments = [comment['sentiment'] for comment in processed_comments]
    languages = [comment['original_language'] for comment in processed_comments]
    
    # Create visualizations
    sentiment_chart = create_sentiment_chart(sentiments)
    language_chart = create_language_chart(languages)
    
    # Get top positive and negative comments
    top_positive = get_top_comments(processed_comments, 'Positive', 5)
    top_negative = get_top_comments(processed_comments, 'Negative', 5)
    
    return {
        'sentiment_chart': sentiment_chart,
        'language_chart': language_chart,
        'top_positive': top_positive,
        'top_negative': top_negative
    }