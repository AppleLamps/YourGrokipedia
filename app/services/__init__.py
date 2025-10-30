"""Business logic services"""
from app.services.article_fetcher import (
    scrape_wikipedia,
    fetch_grokipedia_article
)
from app.services.comparison_service import compare_articles

__all__ = [
    'scrape_wikipedia',
    'fetch_grokipedia_article',
    'compare_articles'
]

