"""
Web dashboard for YouTube Sentiment Analysis using Dash
"""
# Updated imports for relative paths
try:
    import dash
    from dash import dcc, html, Input, Output, callback, State
    import plotly.express as px
    import pandas as pd
    from collections import Counter
    import json
    import sys
    import os
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install required packages with: pip install dash plotly pandas")
    sys.exit(1)

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our package
try:
    from .youtube_api import fetch_comments, fetch_all_comments
    from .language_processor import detect_language, translate_to_english
    from .sentiment_analyzer import analyze_sentiment, detect_toxicity
    from .chatbot import initialize_chatbot, ask_question
except ImportError:
    # Fallback for direct execution
    from youtube_sentiment.youtube_api import fetch_comments, fetch_all_comments
    from youtube_sentiment.language_processor import detect_language, translate_to_english
    from youtube_sentiment.sentiment_analyzer import analyze_sentiment, detect_toxicity
    from youtube_sentiment.chatbot import initialize_chatbot, ask_question

# Initialize Dash app
app = dash.Dash(__name__, title="YouTube Sentiment Analysis")

# Global variables
processed_data = []
chatbot_model = None
analysis_summary = {}

def process_comments(video_url, max_comments=50, fetch_all=False):
    """
    Process YouTube comments through the full pipeline
    
    Args:
        video_url (str): YouTube video URL
        max_comments (int): Maximum number of comments to process
        fetch_all (bool): If True, fetch all comments regardless of max_comments
        
    Returns:
        list: Processed comments with all analysis results
    """
    if fetch_all:
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

def load_sample_data():
    """Load sample data for demonstration"""
    # This would normally be replaced with actual processed data
    sample_data = [
        {
            'text': 'This video is amazing!',
            'original_language': 'en',
            'sentiment': 'Positive',
            'polarity': 0.6,
            'is_toxic': False,
            'author': 'User1'
        },
        {
            'text': 'I love this content, keep it up!',
            'original_language': 'en',
            'sentiment': 'Positive',
            'polarity': 0.8,
            'is_toxic': False,
            'author': 'User2'
        },
        {
            'text': 'This is terrible, waste of time',
            'original_language': 'en',
            'sentiment': 'Negative',
            'polarity': -0.7,
            'is_toxic': False,
            'author': 'User3'
        },
        {
            'text': 'Not good at all',
            'original_language': 'en',
            'sentiment': 'Negative',
            'polarity': -0.4,
            'is_toxic': False,
            'author': 'User4'
        },
        {
            'text': 'It is okay, nothing special',
            'original_language': 'en',
            'sentiment': 'Neutral',
            'polarity': 0.0,
            'is_toxic': False,
            'author': 'User5'
        }
    ]
    return sample_data

def create_layout():
    """Create the app layout"""
    return html.Div([
        html.H1("YouTube Sentiment Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Input section
        html.Div([
            html.Div([
                html.Label("YouTube Video URL:", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='video-url',
                    type='text',
                    placeholder='Enter YouTube URL (e.g., https://www.youtube.com/watch?v=...)',
                    style={'width': '100%', 'padding': '12px', 'fontSize': '16px', 'marginTop': '5px'}
                )
            ], style={'width': '55%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Max Comments:", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='max-comments',
                    type='number',
                    value=50,
                    min=1,
                    max=1000,
                    step=10,
                    style={'width': '100%', 'padding': '12px', 'fontSize': '16px', 'marginTop': '5px'}
                )
            ], style={'width': '20%', 'display': 'inline-block', 'paddingLeft': '20px'}),
            
            html.Div([
                html.Label("Fetch All:", style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='fetch-all-checkbox',
                    options=[{'label': ' Yes', 'value': 'yes'}],
                    value=[],
                    style={'marginTop': '10px'}
                )
            ], style={'width': '10%', 'display': 'inline-block', 'paddingLeft': '20px'}),
            
            html.Div([
                html.Button(
                    'Analyze',
                    id='analyze-button',
                    n_clicks=0,
                    style={'padding': '12px 25px', 'fontSize': '16px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'marginTop': '25px'}
                )
            ], style={'width': '15%', 'display': 'inline-block', 'textAlign': 'right'})
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '20px'}),
        
        # Loading indicator
        html.Div(id='loading-output', style={'textAlign': 'center', 'margin': '20px'}),
        
        # Results section
        html.Div(id='results-section', children=[
            # Summary cards
            html.Div([
                html.Div([
                    html.H3("Total Comments", style={'textAlign': 'center'}),
                    html.H2(id='total-comments', children="0", style={'textAlign': 'center', 'color': '#1f77b4'})
                ], className='summary-card', style={'width': '23%', 'display': 'inline-block', 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("Positive", style={'textAlign': 'center'}),
                    html.H2(id='positive-count', children="0", style={'textAlign': 'center', 'color': 'green'})
                ], className='summary-card', style={'width': '23%', 'display': 'inline-block', 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("Negative", style={'textAlign': 'center'}),
                    html.H2(id='negative-count', children="0", style={'textAlign': 'center', 'color': 'red'})
                ], className='summary-card', style={'width': '23%', 'display': 'inline-block', 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("Neutral", style={'textAlign': 'center'}),
                    html.H2(id='neutral-count', children="0", style={'textAlign': 'center', 'color': 'orange'})
                ], className='summary-card', style={'width': '23%', 'display': 'inline-block', 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            ], style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            # Charts
            html.Div([
                dcc.Graph(id='sentiment-chart'),
                dcc.Graph(id='language-chart')
            ], style={'marginBottom': '30px'}),
            
            # Top comments
            html.Div([
                html.Div([
                    html.H3("Top Positive Comments", style={'color': 'green'}),
                    html.Div(id='top-positive-comments')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '15px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("Top Negative Comments", style={'color': 'red'}),
                    html.Div(id='top-negative-comments')
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%', 'padding': '15px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            ], style={'marginBottom': '30px'}),
            
            # Chatbot section
            html.Div([
                html.H2("AI Chatbot", style={'textAlign': 'center', 'marginBottom': '20px'}),
                html.Div([
                    html.Div(id='chatbot-history', style={'height': '300px', 'overflowY': 'scroll', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '15px'}),
                    html.Div([
                        dcc.Input(
                            id='chatbot-input',
                            type='text',
                            placeholder='Ask a question about the analysis...',
                            style={'width': '80%', 'padding': '12px', 'fontSize': '16px'}
                        ),
                        html.Button(
                            'Send',
                            id='chatbot-send',
                            n_clicks=0,
                            style={'width': '18%', 'padding': '12px', 'fontSize': '16px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'marginLeft': '2%'}
                        )
                    ], style={'display': 'flex'})
                ], style={'padding': '20px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            ], style={'marginTop': '20px'})
        ], style={'display': 'none'})  # Hidden by default
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

# Set the app layout
app.layout = create_layout()

@app.callback(
    [Output('loading-output', 'children'),
     Output('results-section', 'style'),
     Output('total-comments', 'children'),
     Output('positive-count', 'children'),
     Output('negative-count', 'children'),
     Output('neutral-count', 'children'),
     Output('sentiment-chart', 'figure'),
     Output('language-chart', 'figure'),
     Output('top-positive-comments', 'children'),
     Output('top-negative-comments', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('video-url', 'value'),
     State('max-comments', 'value'),
     State('fetch-all-checkbox', 'value')]
)
def update_dashboard(n_clicks, video_url, max_comments, fetch_all_value):
    """Update dashboard with analysis results"""
    global processed_data, analysis_summary, chatbot_model
    
    if n_clicks == 0 or not video_url:
        return ["", {'display': 'none'}, "0", "0", "0", "0", {}, {}, "", ""]
    
    try:
        # Show loading message
        loading_message = html.Div([
            html.H3("Analyzing comments...", style={'color': '#007bff'}),
            html.P("This may take a moment depending on the number of comments...")
        ])
        
        # Determine if we should fetch all comments
        fetch_all = 'yes' in fetch_all_value
        
        # Process the video URL
        processed_data = process_comments(video_url, max_comments=max_comments, fetch_all=fetch_all)
        
        # Get analysis summary
        analysis_summary = get_analysis_summary(processed_data)
        
        # Initialize chatbot model
        chatbot_model = initialize_chatbot('models/gemini-flash-latest')
        
        # Calculate summary statistics
        total_comments = analysis_summary['total_comments']
        sentiments = [comment['sentiment'] for comment in processed_data]
        sentiment_counts = Counter(sentiments)
        
        positive_count = sentiment_counts.get('Positive', 0)
        negative_count = sentiment_counts.get('Negative', 0)
        neutral_count = sentiment_counts.get('Neutral', 0)
        
        # Create charts
        sentiment_fig = px.pie(
            names=list(sentiment_counts.keys()),
            values=list(sentiment_counts.values()),
            title="Sentiment Distribution",
            color_discrete_sequence=['green', 'red', 'orange']
        )
        
        languages = [comment['original_language'] for comment in processed_data]
        language_counts = Counter(languages)
        language_fig = px.bar(
            x=list(language_counts.keys()),
            y=list(language_counts.values()),
            title="Language Distribution",
            labels={'x': 'Language', 'y': 'Number of Comments'},
            color=list(language_counts.values()),
            color_continuous_scale='Blues'
        )
        
        # Get top comments
        positive_comments = [c for c in processed_data if c['sentiment'] == 'Positive']
        negative_comments = [c for c in processed_data if c['sentiment'] == 'Negative']
        
        top_positive = sorted(positive_comments, key=lambda x: x['polarity'], reverse=True)[:3]
        top_negative = sorted(negative_comments, key=lambda x: x['polarity'])[:3]
        
        # Format top comments for display
        top_positive_html = html.Ul([
            html.Li([
                html.Strong(comment['author'] + ": "),
                comment['text']
            ]) for comment in top_positive
        ])
        
        top_negative_html = html.Ul([
            html.Li([
                html.Strong(comment['author'] + ": "),
                comment['text']
            ]) for comment in top_negative
        ])
        
        # Hide loading message and show results
        return ["", {'display': 'block'}, str(total_comments), str(positive_count), str(negative_count), str(neutral_count), sentiment_fig, language_fig, top_positive_html, top_negative_html]
        
    except Exception as e:
        error_message = html.Div([
            html.H3("Error occurred during analysis", style={'color': 'red'}),
            html.P(f"Error: {str(e)}")
        ])
        return [error_message, {'display': 'none'}, "0", "0", "0", "0", {}, {}, "", ""]

@app.callback(
    Output('chatbot-history', 'children'),
    [Input('chatbot-send', 'n_clicks')],
    [State('chatbot-input', 'value'),
     State('chatbot-history', 'children')]
)
def update_chatbot(n_clicks, user_input, chat_history):
    """Update chatbot conversation"""
    global chatbot_model, analysis_summary
    
    # Initialize chat history if None
    if chat_history is None:
        chat_history = []
    
    # If this is the first click or no input, return current history
    if n_clicks == 0 or not user_input:
        return chat_history
    
    # Add user message to history
    user_message = html.Div([
        html.Strong("You: ", style={'color': '#007bff'}),
        user_input
    ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': '#e9ecef', 'borderRadius': '5px'})
    
    # Add user message to history
    if isinstance(chat_history, list):
        new_history = chat_history + [user_message]
    else:
        new_history = [user_message]
    
    # Get chatbot response
    if chatbot_model:
        try:
            response = ask_question(chatbot_model, user_input, analysis_summary)
            bot_message = html.Div([
                html.Strong("Bot: ", style={'color': '#28a745'}),
                response
            ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        except Exception as e:
            bot_message = html.Div([
                html.Strong("Bot: ", style={'color': '#28a745'}),
                f"Sorry, I encountered an error: {str(e)}"
            ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
    else:
        bot_message = html.Div([
            html.Strong("Bot: ", style={'color': '#28a745'}),
            "Chatbot is not available. Please check your API configuration."
        ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
    
    # Add bot message to history
    new_history = new_history + [bot_message]
    
    return new_history

def run_dashboard():
    """Run the Dash web dashboard"""
    app.run(debug=True, host='0.0.0.0', port=8050)

if __name__ == '__main__':
    run_dashboard()