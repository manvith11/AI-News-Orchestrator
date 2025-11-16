"""
Credibility Scorer Module
Evaluates source authenticity and article credibility
"""
from typing import Dict, List
from config import REPUTABLE_SOURCES
from ai_analyzer import AIAnalyzer


class CredibilityScorer:
    """Scores source and article credibility"""
    
    def __init__(self):
        self.reputable_sources = [s.lower() for s in REPUTABLE_SOURCES]
        self.ai_analyzer = AIAnalyzer()
    
    def score_source(self, source_name: str) -> Dict:
        """
        Score source credibility based on known reputable sources
        
        Args:
            source_name: Name of the news source
            
        Returns:
            Dictionary with credibility score and details
        """
        source_lower = source_name.lower()
        
        # Check if source is in reputable list
        is_reputable = any(reputable in source_lower for reputable in self.reputable_sources)
        
        # Base score - allow scores up to 100
        if is_reputable:
            # Very reputable sources get higher scores
            if any(name in source_lower for name in ["bbc", "reuters", "associated press", "ap news", "the new york times"]):
                base_score = 95
                reason = "Highly reputable news source"
            else:
                base_score = 88
                reason = "Known reputable news source"
        else:
            # Check for common patterns
            if any(word in source_lower for word in ["news", "times", "post", "tribune"]):
                base_score = 70
                reason = "Appears to be a news organization"
            elif any(word in source_lower for word in ["blog", "medium", "substack"]):
                base_score = 40
                reason = "Blog or independent publication"
            else:
                base_score = 55
                reason = "Unknown source"
        
        return {
            "score": base_score,
            "is_reputable": is_reputable,
            "reason": reason,
            "source_name": source_name
        }
    
    def score_article(self, article: Dict) -> Dict:
        """
        Score individual article credibility
        
        Args:
            article: Article dictionary
            
        Returns:
            Dictionary with article credibility score
        """
        # Get source score
        source_score_data = self.score_source(article.get("source", "Unknown"))
        source_score = source_score_data["score"]
        
        # Get bias detection
        bias_data = self.ai_analyzer.detect_bias(article)
        bias_score = bias_data["bias_score"]
        
        # Calculate overall credibility
        # Source credibility (70%) + Content quality (30%)
        content_quality = max(0, 100 - bias_score)
        overall_score = int(source_score * 0.7 + content_quality * 0.3)
        
        # Adjust for clickbait
        if bias_data.get("is_clickbait", False):
            overall_score = max(0, overall_score - 20)
        
        # Cap at 100
        overall_score = min(100, overall_score)
        
        return {
            "overall_score": overall_score,
            "source_score": source_score,
            "content_score": content_quality,
            "bias_score": bias_score,
            "is_clickbait": bias_data.get("is_clickbait", False),
            "flags": bias_data.get("flags", []),
            "source_details": source_score_data
        }
    
    def score_all_sources(self, articles: List[Dict]) -> Dict:
        """
        Score all sources and calculate average authenticity
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with source scores and average authenticity
        """
        source_scores = {}
        article_scores = []
        
        for article in articles:
            source = article.get("source", "Unknown")
            
            # Score source if not already scored
            if source not in source_scores:
                source_scores[source] = self.score_source(source)
            
            # Score article
            article_score = self.score_article(article)
            article_scores.append(article_score)
        
        # Calculate average authenticity
        if article_scores:
            avg_score = sum(a["overall_score"] for a in article_scores) / len(article_scores)
        else:
            avg_score = 0
        
        return {
            "average_authenticity": int(avg_score),
            "source_scores": source_scores,
            "article_scores": article_scores,
            "total_sources": len(source_scores),
            "reputable_sources_count": sum(1 for s in source_scores.values() if s["is_reputable"])
        }
    
    def get_authenticity_level(self, score: int) -> str:
        """Get human-readable authenticity level"""
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"

