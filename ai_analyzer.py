"""
AI Analysis Module
Uses LLM to detect milestones, summarize events, and analyze articles
"""
import json
import re
from typing import List, Dict, Optional
from config import LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_MODEL


class AIAnalyzer:
    """Analyzes articles using LLM for milestone detection and summarization"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.openai_key = OPENAI_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.model = OPENAI_MODEL
    
    def analyze_event(self, articles: List[Dict], event_query: str) -> Dict:
        """
        Analyze articles and generate timeline, summary, and insights
        
        Args:
            articles: List of processed articles
            event_query: Original event query/title
            
        Returns:
            Dictionary with timeline, summary, highlights, and discrepancies
        """
        # Prepare article summaries for LLM
        article_summaries = []
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles
            summary = {
                "index": i,
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "published_date": article.get("publishedAt", ""),
                "content": article.get("cleaned_content", "")[:2000],  # Limit content length
                "extracted_dates": [d["date"] for d in article.get("extracted_dates", [])]
            }
            article_summaries.append(summary)
        
        # Generate analysis
        analysis = self._call_llm_for_analysis(event_query, article_summaries)
        
        return analysis
    
    def _call_llm_for_analysis(self, event_query: str, articles: List[Dict]) -> Dict:
        """Call LLM to analyze articles and generate timeline"""
        
        if self.provider == "openai" and self.openai_key:
            return self._analyze_with_openai(event_query, articles)
        elif self.provider == "gemini" and self.gemini_key:
            return self._analyze_with_gemini(event_query, articles)
        else:
            # Fallback to basic analysis without LLM
            return self._basic_analysis(event_query, articles)
    
    def _analyze_with_openai(self, event_query: str, articles: List[Dict]) -> Dict:
        """Analyze using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            # Prepare prompt
            articles_text = "\n\n".join([
                f"Article {a['index']} ({a['source']}, {a['published_date']}):\n"
                f"Title: {a['title']}\n"
                f"Content: {a['content'][:1500]}\n"
                f"Dates mentioned: {', '.join(a['extracted_dates'][:5])}"
                for a in articles
            ])
            
            prompt = f"""You are an AI news analyst. Analyze the following news articles about "{event_query}" and provide a comprehensive timeline and summary.

Articles:
{articles_text}

Please provide a JSON response with the following structure:
{{
    "timeline": [
        {{"date": "YYYY-MM-DD", "event": "Description of what happened on this date"}},
        ...
    ],
    "summary": "A comprehensive 2-3 paragraph summary of the entire event",
    "key_highlights": [
        "Key fact or milestone 1",
        "Key fact or milestone 2",
        ...
    ],
    "discrepancies": [
        {{
            "issue": "Clear description of the conflict/difference (e.g., 'Launch delayed' vs 'Launch on time')",
            "sources": ["Source 1", "Source 2"],
            "details": "What Source 1 says vs what Source 2 says"
        }},
        ...
    ],
    "verified_facts": [
        "Fact that appears consistently across sources",
        ...
    ]
}}

CRITICAL INSTRUCTIONS FOR DISCREPANCIES:
- Compare articles side-by-side for conflicting information
- Look for contradictions in: dates, outcomes, numbers, statements, claims
- Examples to detect:
  * "Launch delayed" vs "Launch on time"
  * Different dates for the same event
  * Conflicting numbers or statistics
  * Opposing statements about outcomes
- For each discrepancy, clearly state what the conflict is and which sources disagree
- If no significant conflicts exist, return an empty discrepancies array

Important:
- Order timeline events chronologically by date
- Extract actual dates from articles, don't make up dates
- Identify major turning points and milestones
- ACTIVELY COMPARE ARTICLES to find conflicts and differences
- Focus on verified facts that appear in multiple sources
"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that analyzes news articles and creates timelines. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._basic_analysis(event_query, articles)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._basic_analysis(event_query, articles)
    
    def _analyze_with_gemini(self, event_query: str, articles: List[Dict]) -> Dict:
        """Analyze using Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            articles_text = "\n\n".join([
                f"Article {a['index']} ({a['source']}, {a['published_date']}):\n"
                f"Title: {a['title']}\n"
                f"Content: {a['content'][:1500]}"
                for a in articles
            ])
            
            prompt = f"""Analyze these news articles about "{event_query}" and provide a JSON response with:
- timeline: chronological list of events with dates
- summary: 2-3 paragraph overview
- key_highlights: list of important facts
- discrepancies: array of conflicts with format {{"issue": "conflict description", "sources": ["Source1", "Source2"], "details": "what each says"}}
- verified_facts: facts confirmed by multiple sources

CRITICAL: Compare articles to find conflicts like "Launch delayed" vs "Launch on time", different dates, conflicting numbers, etc.

Articles:
{articles_text}

Respond with valid JSON only."""
            
            response = model.generate_content(prompt)
            result_text = response.text
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._basic_analysis(event_query, articles)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._basic_analysis(event_query, articles)
    
    def _basic_analysis(self, event_query: str, articles: List[Dict]) -> Dict:
        """Fallback basic analysis without LLM"""
        # Extract dates and create simple timeline
        timeline_events = []
        all_dates = set()
        
        for article in articles:
            dates = article.get("extracted_dates", [])
            for date_info in dates:
                # Handle both dict and string formats
                if isinstance(date_info, dict):
                    date_str = date_info.get("date", "")
                elif isinstance(date_info, str):
                    date_str = date_info
                else:
                    continue
                
                if date_str and date_str not in all_dates:
                    all_dates.add(date_str)
                    timeline_events.append({
                        "date": date_str,
                        "event": f"News reported by {article.get('source', 'Unknown')}: {article.get('title', '')[:100]}"
                    })
        
        # Sort by date
        timeline_events.sort(key=lambda x: x["date"])
        
        # Create summary from article titles
        titles = [a.get("title", "") for a in articles[:5]]
        summary = f"Analysis of {len(articles)} articles about '{event_query}'. Key sources include: {', '.join(set(a.get('source', 'Unknown') for a in articles[:5]))}."
        
        return {
            "timeline": timeline_events,
            "summary": summary,
            "key_highlights": titles[:5],
            "discrepancies": [],
            "verified_facts": []
        }
    
    def detect_bias(self, article: Dict) -> Dict:
        """Detect potential bias or clickbait in an article"""
        title = article.get("title", "")
        content = article.get("cleaned_content", "")[:1000]
        
        # Simple heuristics (can be enhanced with LLM)
        bias_indicators = {
            "clickbait_words": ["shocking", "amazing", "you won't believe", "secret", "exposed"],
            "subjective_words": ["terrible", "amazing", "worst", "best", "disaster"],
            "exclamation_count": title.count("!") + content.count("!")
        }
        
        score = 0
        flags = []
        
        title_lower = title.lower()
        for word in bias_indicators["clickbait_words"]:
            if word in title_lower:
                score += 10
                flags.append(f"Clickbait language detected: '{word}'")
        
        if bias_indicators["exclamation_count"] > 3:
            score += 5
            flags.append("Excessive exclamation marks")
        
        return {
            "bias_score": min(score, 100),
            "flags": flags,
            "is_clickbait": score > 15
        }

