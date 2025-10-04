"""
Module for language detection and translation (fixed with input sanitization)
"""

import logging
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detect the language of a given text safely.
    """
    try:
        if not text or not text.strip():
            return 'unknown'
        # Handle texts with only emojis or symbols
        if all(not ch.isalnum() for ch in text):
            return 'unknown'
        return detect(text)
    except Exception as e:
        logging.warning(
            f"Language detection failed for text: {text[:30]}... Error: {str(e)}"
        )
        return 'unknown'


def translate_to_english(text: str, src_lang: str = None) -> str:
    """
    Translate text to English safely.
    """
    try:
        if not text or not text.strip():
            return text

        # If source language not provided, detect it
        if src_lang is None:
            src_lang = detect_language(text)

        # If already English or detection failed
        if src_lang in ['en', 'unknown']:
            return text

        # Use deep-translator
        translated = GoogleTranslator(source='auto', target='en').translate(text)

        # deep-translator can sometimes return None
        if translated is None:
            return text

        return translated

    except Exception as e:
        logging.error(
            f"Translation failed for text: {text[:30]}... Error: {str(e)}"
        )
        return text  # Return original if translation fails
