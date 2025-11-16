"""
Article Processing Module
Extracts dates, entities, and processes article content
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
import dateparser
from bs4 import BeautifulSoup

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        # Model not found, try to download it
        import subprocess
        import sys
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                         check=False, capture_output=True)
            nlp = spacy.load("en_core_web_sm")
            SPACY_AVAILABLE = True
        except:
            SPACY_AVAILABLE = False
            nlp = None
            print("Warning: spaCy model not available. NER features will be limited.")
except Exception as e:
    SPACY_AVAILABLE = False
    nlp = None
    print(f"Warning: spaCy not available: {e}. NER features will be limited.")


class ArticleProcessor:
    """Processes articles to extract dates, entities, and clean content"""
    
    def __init__(self):
        self.nlp = nlp if SPACY_AVAILABLE else None
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process a single article
        
        Args:
            article: Article dictionary with title, content, etc.
            
        Returns:
            Processed article with extracted dates and entities
        """
        processed = article.copy()
        
        # Clean content
        processed["cleaned_content"] = self._clean_content(
            article.get("content", "") or article.get("description", "")
        )
        
        # Extract dates
        processed["extracted_dates"] = self._extract_dates(
            processed["cleaned_content"],
            article.get("publishedAt", "")
        )
        
        # Extract entities
        if self.nlp:
            processed["entities"] = self._extract_entities(processed["cleaned_content"])
        else:
            processed["entities"] = {}
        
        # Combine all text for analysis
        processed["full_text"] = f"{article.get('title', '')} {processed['cleaned_content']}"
        
        return processed
    
    def _clean_content(self, content: str) -> str:
        """Clean HTML and normalize text"""
        if not content:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-\'"]', ' ', text)
        
        return text.strip()
    
    def _extract_dates(self, text: str, published_date: str = "") -> List[Dict]:
        """
        Extract dates from text
        
        Returns:
            List of date dictionaries with date string and context
        """
        dates = []
        
        # Parse published date
        if published_date:
            try:
                parsed = dateparser.parse(published_date, settings={'RELATIVE_BASE': datetime.now()})
                if parsed:
                    # Normalize to timezone-naive datetime
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    # Filter out future dates (likely parsing errors)
                    if parsed <= datetime.now():
                        dates.append({
                            "date": parsed.strftime("%Y-%m-%d"),
                            "datetime": parsed,
                            "context": "Article publication date",
                            "source": "metadata"
                        })
            except:
                pass
        
        # Extract dates from text using dateparser
        # Look for date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(?:on|by|since|until|from|to)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',  # "on January 1, 2024"
        ]
        
        found_dates = set()
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                try:
                    parsed = dateparser.parse(date_str, settings={'RELATIVE_BASE': datetime.now()})
                    if parsed:
                        # Normalize to timezone-naive datetime
                        if parsed.tzinfo is not None:
                            parsed = parsed.replace(tzinfo=None)
                        # Filter out future dates (likely parsing errors)
                        if parsed > datetime.now():
                            continue
                        date_key = parsed.strftime("%Y-%m-%d")
                        if date_key not in found_dates:
                            found_dates.add(date_key)
                            # Get context (surrounding text)
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            context = text[start:end].strip()
                            
                            dates.append({
                                "date": date_key,
                                "datetime": parsed,
                                "context": context,
                                "source": "text"
                            })
                except:
                    continue
        
        # Also try dateparser on the full text for natural language dates
        try:
            # Look for phrases like "on July 14, 2023"
            natural_dates = re.finditer(
                r'\b(?:on|by|since|until|from|to|in)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
                text,
                re.IGNORECASE
            )
            for match in natural_dates:
                date_str = match.group(1)
                parsed = dateparser.parse(date_str, settings={'RELATIVE_BASE': datetime.now()})
                if parsed:
                    # Normalize to timezone-naive datetime
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    # Filter out future dates (likely parsing errors)
                    if parsed > datetime.now():
                        continue
                    date_key = parsed.strftime("%Y-%m-%d")
                    if date_key not in found_dates:
                        found_dates.add(date_key)
                        dates.append({
                            "date": date_key,
                            "datetime": parsed,
                            "context": match.group(0),
                            "source": "text"
                        })
        except:
            pass
        
        # Filter out any remaining future dates and sort
        current_date = datetime.now()
        valid_dates = [d for d in dates if d["datetime"] and d["datetime"] <= current_date]
        
        # Sort by date (all datetimes are now timezone-naive)
        valid_dates.sort(key=lambda x: x["datetime"] if x["datetime"] else datetime.min)
        
        return valid_dates
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy
        
        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        if not self.nlp or not text:
            return {}
        
        doc = self.nlp(text[:1000000])  # Limit text length for performance
        
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Geopolitical entities (countries, cities)
            "DATE": [],
            "EVENT": [],
            "LOC": []  # Locations
        }
        
        for ent in doc.ents:
            entity_type = ent.label_
            entity_text = ent.text.strip()
            
            if entity_type in entities and entity_text not in entities[entity_type]:
                entities[entity_type].append(entity_text)
        
        return entities
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process multiple articles"""
        return [self.process_article(article) for article in articles]

