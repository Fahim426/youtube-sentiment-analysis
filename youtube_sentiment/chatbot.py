"""
Module for Gemini-powered chatbot
"""
import sys
import os

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import for Gemini API using explicit paths to satisfy static analysis
try:
    import google.generativeai as genai
    from google.generativeai.client import configure
    from google.generativeai.generative_models import GenerativeModel
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    configure = None
    GenerativeModel = None
    genai = None
    print("Warning: google-generativeai not installed. Chatbot functionality will be disabled.")

# Import config properly
try:
    from config import GEMINI_API_KEY
except ImportError:
    # Fallback for direct execution - try absolute import
    try:
        import config
        GEMINI_API_KEY = config.GEMINI_API_KEY
    except ImportError:
        # If all else fails, get from environment variable
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Configure Gemini API
if GEMINI_AVAILABLE and GEMINI_API_KEY and configure:
    configure(api_key=GEMINI_API_KEY)

def list_available_models():
    """
    List available Gemini models
    
    Returns:
        list: List of available model names
    """
    if not GEMINI_AVAILABLE or not genai:
        return []
    
    try:
        # Use getattr to dynamically access list_models to satisfy static analysis
        list_models_func = getattr(genai, 'list_models', None)
        if list_models_func:
            models = list_models_func()
            return [model.name for model in models if "generateContent" in model.supported_generation_methods]
        else:
            # Fallback if list_models is not available
            return ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        # Return common model names as fallback
        return ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']

def initialize_chatbot(model_name=None):
    """
    Initialize the Gemini model for chatbot functionality
    
    Args:
        model_name (str, optional): Specific model to use. If None, will try available models.
        
    Returns:
        GenerativeModel: Configured Gemini model or None if API key is missing
    """
    if not GEMINI_AVAILABLE or not GenerativeModel:
        print("Warning: google-generativeai not installed. Chatbot functionality will be disabled.")
        return None
        
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found. Chatbot functionality will be disabled.")
        return None
    
    # If no model specified, try to find an appropriate one
    if not model_name:
        available_models = list_available_models()
        # Try common models in order of preference (with correct naming)
        preferred_models = [
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-pro',
            'models/gemini-flash-latest',
            'models/gemini-pro-latest',
            'gemini-1.5-flash', 
            'gemini-1.5-pro', 
            'gemini-pro'
        ]
        for model in preferred_models:
            if model in available_models or not available_models:
                model_name = model
                break
        # If still no model found, use the first available
        if not model_name and available_models:
            model_name = available_models[0]
        # Fallback to latest models
        if not model_name:
            model_name = 'models/gemini-flash-latest'
    
    try:
        model = GenerativeModel(model_name)
        print(f"Using Gemini model: {model_name}")
        return model
    except Exception as e:
        # Try fallback models
        fallback_models = [
            'models/gemini-flash-latest',
            'models/gemini-pro-latest',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        for fallback_model in fallback_models:
            if fallback_model != model_name:  # Don't retry the same model
                try:
                    model = GenerativeModel(fallback_model)
                    print(f"Using fallback Gemini model: {fallback_model}")
                    return model
                except Exception:
                    continue
        print(f"Error initializing Gemini model '{model_name}': {str(e)}")
        return None

def ask_question(model, question, context_data=None):
    """
    Ask a question to the chatbot with optional context
    
    Args:
        model (GenerativeModel): Initialized Gemini model
        question (str): Question to ask
        context_data (dict, optional): Context data from sentiment analysis
        
    Returns:
        str: Response from the chatbot
    """
    if not model:
        return "Chatbot is not available. Please check your API configuration."
    
    try:
        # Create prompt with context if available
        if context_data:
            # Build a more comprehensive prompt with sample comments
            prompt = f"""
            You are an AI assistant analyzing YouTube comment sentiment data. 
            Based on the following analysis data, answer the question at the end.
            
            === ANALYSIS DATA ===
            Total Comments Analyzed: {context_data.get('total_comments', 0)}
            
            Sentiment Distribution: 
            {context_data.get('sentiment_distribution', {})}
            
            Language Distribution: 
            {context_data.get('language_distribution', {})}
            
            Sample Comments by Sentiment:
            """
            
            # Add sample comments if available
            sample_comments = context_data.get('sample_comments', {})
            if sample_comments:
                for sentiment, comments in sample_comments.items():
                    if comments:
                        prompt += f"\n{sentiment.capitalize()} Comments:\n"
                        for i, comment in enumerate(comments, 1):
                            prompt += f"  {i}. {comment}\n"
            
            prompt += f"""
            === QUESTION ===
            {question}
            
            === INSTRUCTIONS ===
            Provide a concise and helpful response based on the data when relevant. 
            When discussing what people are talking about, reference the sample comments 
            to provide specific insights about the topics and themes in the comments.
            Keep your response under 200 words.
            """
        else:
            prompt = question
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error while processing your question: {str(e)}"
