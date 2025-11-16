"""
News Fetching Module
Fetches news articles from NewsAPI and GNews
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from config import NEWSAPI_KEY, MAX_ARTICLES, NEWSAPI_LANGUAGE, NEWSAPI_SORT_BY, CACHE_ARTICLES, CACHE_DIR
from utils import save_to_json, load_from_json, get_cache_key, ensure_dir


class NewsFetcher:
    """Fetches news articles from multiple sources"""
    
    def __init__(self):
        self.newsapi_key = NEWSAPI_KEY
        self.max_articles = MAX_ARTICLES
        self.cache_enabled = CACHE_ARTICLES
        self.cache_dir = CACHE_DIR
        
    def fetch_articles(self, query: str, days_back: int = 30) -> List[Dict]:
        """
        Fetch articles for a given query
        
        Args:
            query: Event title or keyword
            days_back: Number of days to look back for articles
            
        Returns:
            List of article dictionaries
        """
        # Check cache first
        if self.cache_enabled:
            cache_key = get_cache_key(query)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            cached = load_from_json(cache_path)
            if cached:
                return cached
        
        articles = []
        
        # Try NewsAPI first
        if self.newsapi_key:
            try:
                newsapi_articles = self._fetch_from_newsapi(query, days_back)
                articles.extend(newsapi_articles)
            except Exception as e:
                print(f"NewsAPI error: {e}")
        
        # Fallback to GNews if needed
        if len(articles) < self.max_articles:
            try:
                gnews_articles = self._fetch_from_gnews(query)
                # Avoid duplicates
                existing_urls = {a.get('url', '') for a in articles}
                for article in gnews_articles:
                    if article.get('url') not in existing_urls:
                        articles.append(article)
                        if len(articles) >= self.max_articles:
                            break
            except Exception as e:
                print(f"GNews error: {e}")
        
        # Limit to max articles
        articles = articles[:self.max_articles]
        
        # Cache results
        if self.cache_enabled and articles:
            ensure_dir(self.cache_dir)
            cache_key = get_cache_key(query)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            save_to_json(articles, cache_path)
        
        return articles
    
    def _fetch_from_newsapi(self, query: str, days_back: int) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": self.newsapi_key,
            "language": NEWSAPI_LANGUAGE,
            "sortBy": NEWSAPI_SORT_BY,
            "from": from_date,
            "pageSize": self.max_articles
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for item in data.get("articles", []):
            if item.get("title") and item.get("title") != "[Removed]":
                source_name = item.get("source", {}).get("name", "")
                if not source_name or source_name == "[Removed]":
                    # Try to extract from URL as fallback
                    url = item.get("url", "")
                    if url:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc
                            source_name = domain.replace("www.", "").split(".")[0].title()
                        except:
                            source_name = "Unknown"
                    else:
                        source_name = "Unknown"
                
                article = {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                    "source": source_name,
                    "publishedAt": item.get("publishedAt", ""),
                    "author": item.get("author", "")
                }
                articles.append(article)
        
        return articles
    
    def _fetch_from_gnews(self, query: str) -> List[Dict]:
        """Fetch articles from GNews (fallback)"""
        try:
            from gnews import GNews
            
            google_news = GNews(language='en', period='30d', max_results=self.max_articles)
            news_items = google_news.get_news(query)
            
            articles = []
            for item in news_items:
                source_name = item.get("publisher", {}).get("name", "")
                if not source_name:
                    # Try to extract from URL as fallback
                    url = item.get("url", "")
                    if url:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc
                            source_name = domain.replace("www.", "").split(".")[0].title()
                        except:
                            source_name = "Unknown"
                    else:
                        source_name = "Unknown"
                
                article = {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "content": self._extract_content_from_url(item.get("url", "")),
                    "url": item.get("url", ""),
                    "source": source_name,
                    "publishedAt": item.get("published date", ""),
                    "author": ""
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"GNews fetch error: {e}")
            return []
    
    def _extract_content_from_url(self, url: str) -> str:
        """Extract article content from URL"""
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find main content
            content_selectors = ['article', '.article-body', '.content', 'main', '.post-content']
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    return content.get_text(strip=True)
            
            # Fallback to body text
            return soup.get_text(strip=True)
        except:
            return ""

