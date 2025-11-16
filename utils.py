"""
Utility functions for the AI News Orchestrator
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any


def ensure_dir(directory: str) -> None:
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)


def save_to_json(data: Any, filepath: str) -> None:
    """Save data to JSON file"""
    ensure_dir(os.path.dirname(filepath) if os.path.dirname(filepath) else ".")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_from_json(filepath: str) -> Any:
    """Load data from JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = " ".join(text.split())
    return text.strip()


def format_date(date_str: str) -> str:
    """Format date string to YYYY-MM-DD"""
    try:
        from dateparser import parse
        parsed = parse(date_str)
        if parsed:
            return parsed.strftime("%Y-%m-%d")
    except:
        pass
    return date_str


def get_cache_key(query: str) -> str:
    """Generate cache key from query"""
    return query.lower().replace(" ", "_").replace("'", "").replace('"', "")


def validate_api_keys() -> Dict[str, bool]:
    """Check if required API keys are set"""
    from config import NEWSAPI_KEY, OPENAI_API_KEY, GEMINI_API_KEY, LLM_PROVIDER
    
    status = {
        "newsapi": bool(NEWSAPI_KEY),
        "llm": False
    }
    
    if LLM_PROVIDER == "openai":
        status["llm"] = bool(OPENAI_API_KEY)
    elif LLM_PROVIDER == "gemini":
        status["llm"] = bool(GEMINI_API_KEY)
    
    return status

