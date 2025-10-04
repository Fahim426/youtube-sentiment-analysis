"""
Module for sentiment analysis and toxicity detection
"""
from textblob import TextBlob
import re
from typing import Any

def analyze_sentiment(text):
    """
    Perform sentiment analysis on text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Dictionary containing sentiment label and polarity score
    """
    try:
        blob = TextBlob(text)
        # Access sentiment attribute properly
        sentiment_obj: Any = blob.sentiment
        polarity = float(sentiment_obj.polarity) if hasattr(sentiment_obj, 'polarity') else 0.0
        
        if polarity > 0.1:
            sentiment = 'Positive'
        elif polarity < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
            
        return {
            'sentiment': sentiment,
            'polarity': polarity
        }
    except Exception as e:
        # Default to neutral if analysis fails
        return {
            'sentiment': 'Neutral',
            'polarity': 0.0
        }

def detect_toxicity(text):
    """
    Simple toxicity/hate speech detection based on keywords
    Note: This is a basic implementation. For production use, consider using a dedicated toxicity detection API.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        bool: True if toxicity is detected, False otherwise
    """
    # Basic keyword-based toxicity detection
    # In a real application, you might want to use a more sophisticated approach
    toxicity_keywords = [
        'hate', 'kill', 'stupid', 'idiot', 'dumb', 'worthless', 'disgusting',
        'disgust', 'shut up', 'shutup', 'shut your', 'go to hell', 'damn',
        'retard', 'retarded', 'moron', 'moronic', 'crap', 'trash', 'garbage',
        'useless', 'pathetic', 'awful', 'terrible', 'horrible', 'horrid'
    ]
    
    text_lower = text.lower()
    
    # Check for exact matches
    for keyword in toxicity_keywords:
        if keyword in text_lower:
            return True
    
    # Check for pattern matches (for more flexible detection)
    toxic_patterns = [
        r'\byou\s+are\s+(a\s+)?(idiot|stupid|dumb|moron|retard)',
        r'\bfuck\b',
        r'\bshit\b',
        r'\bdie\b',
        r'\bkys\b'  # kill yourself
    ]
    
    for pattern in toxic_patterns:
        if re.search(pattern, text_lower):
            return True
            
    return False