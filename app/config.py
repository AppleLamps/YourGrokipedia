"""Application configuration"""
import os
from pathlib import Path


class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenRouter API settings
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Grokipedia SDK settings
    LINKS_DIR = os.path.join(
        Path(__file__).parent.parent,
        'grokipedia-sdk',
        'grokipedia_sdk',
        'links'
    )
    LIGHTWEIGHT_MODE = os.getenv('GROKIPEDIA_LIGHTWEIGHT', '').strip().lower() in (
        '1', 'true', 'yes', 'on'
    )

