"""
Configuration file for AI News Orchestrator
Handles API keys and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "openai" or "gemini" (gemini is free!)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# News API Configuration
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "10"))
NEWSAPI_LANGUAGE = os.getenv("NEWSAPI_LANGUAGE", "en")
NEWSAPI_SORT_BY = os.getenv("NEWSAPI_SORT_BY", "publishedAt")

# Application Settings
CACHE_ARTICLES = os.getenv("CACHE_ARTICLES", "true").lower() == "false"
CACHE_DIR = os.getenv("CACHE_DIR", "data/cache")

# Reputable sources for credibility scoring
REPUTABLE_SOURCES = [
    "bbc", "reuters", "ap news", "associated press", "the new york times",
    "the washington post", "the guardian", "cnn", "npr", "pbs", "al jazeera",
    "bloomberg", "wall street journal", "forbes", "time", "newsweek"
]

