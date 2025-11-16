"""
Timeline Generator Module
Orders events chronologically and creates timeline visualization data
"""
from typing import List, Dict
from datetime import datetime
from collections import defaultdict


class TimelineGenerator:
    """Generates chronological timelines from events"""
    
    def __init__(self):
        pass
    
    def generate_timeline(self, analysis: Dict, articles: List[Dict]) -> List[Dict]:
        """
        Generate a consolidated timeline from AI analysis and articles
        
        Args:
            analysis: AI analysis dictionary with timeline, summary, etc.
            articles: List of processed articles
            
        Returns:
            List of timeline events with dates and descriptions
        """
        timeline_events = []
        
        # Add events from AI analysis
        if "timeline" in analysis:
            for event in analysis["timeline"]:
                if "date" in event and "event" in event:
                    timeline_events.append({
                        "date": event["date"],
                        "event": event["event"],
                        "source": "ai_analysis"
                    })
        
        # Add events from article dates
        for article in articles:
            dates = article.get("extracted_dates", [])
            for date_info in dates:
                date_str = date_info["date"]
                # Only add if not already in timeline
                if not any(e["date"] == date_str for e in timeline_events):
                    timeline_events.append({
                        "date": date_str,
                        "event": f"News coverage: {article.get('title', '')[:80]}",
                        "source": article.get("source", "Unknown")
                    })
        
        # Merge events on the same date
        timeline_events = self._merge_duplicate_dates(timeline_events)
        
        # Sort chronologically
        timeline_events = self._sort_timeline(timeline_events)
        
        # Identify major turning points
        timeline_events = self._identify_milestones(timeline_events)
        
        return timeline_events
    
    def _merge_duplicate_dates(self, events: List[Dict]) -> List[Dict]:
        """Merge events that occur on the same date"""
        date_groups = defaultdict(list)
        
        for event in events:
            date_groups[event["date"]].append(event)
        
        merged = []
        for date, date_events in date_groups.items():
            if len(date_events) == 1:
                merged.append(date_events[0])
            else:
                # Merge multiple events on same date
                event_descriptions = [e["event"] for e in date_events]
                sources = list(set([e.get("source", "Unknown") for e in date_events]))
                
                merged_event = {
                    "date": date,
                    "event": " | ".join(event_descriptions[:3]),  # Limit to 3 descriptions
                    "source": ", ".join(sources[:3]),
                    "event_count": len(date_events)
                }
                merged.append(merged_event)
        
        return merged
    
    def _sort_timeline(self, events: List[Dict]) -> List[Dict]:
        """Sort events chronologically"""
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return datetime.min
        
        return sorted(events, key=lambda x: parse_date(x["date"]))
    
    def _identify_milestones(self, events: List[Dict]) -> List[Dict]:
        """Identify major turning points/milestones"""
        if len(events) <= 3:
            # Mark all as milestones if few events
            for event in events:
                event["is_milestone"] = True
            return events
        
        # Mark first and last events as milestones
        if events:
            events[0]["is_milestone"] = True
            events[-1]["is_milestone"] = True
        
        # Identify events with significant keywords
        milestone_keywords = [
            "launch", "announced", "completed", "achieved", "landed", "successful",
            "failed", "breakthrough", "discovery", "summit", "signed", "released"
        ]
        
        for event in events[1:-1]:  # Skip first and last
            event_lower = event["event"].lower()
            if any(keyword in event_lower for keyword in milestone_keywords):
                event["is_milestone"] = True
            else:
                event["is_milestone"] = False
        
        return events
    
    def format_timeline_for_display(self, timeline: List[Dict]) -> str:
        """Format timeline as text for display"""
        lines = []
        for event in timeline:
            date = event["date"]
            description = event["event"]
            milestone_marker = "⭐ " if event.get("is_milestone", False) else "  "
            lines.append(f"{milestone_marker}{date} → {description}")
        
        return "\n".join(lines)
    
    def get_timeline_stats(self, timeline: List[Dict]) -> Dict:
        """Get statistics about the timeline"""
        if not timeline:
            return {
                "total_events": 0,
                "date_range": "N/A",
                "milestone_count": 0
            }
        
        dates = [datetime.strptime(e["date"], "%Y-%m-%d") for e in timeline if "date" in e]
        milestones = [e for e in timeline if e.get("is_milestone", False)]
        
        return {
            "total_events": len(timeline),
            "date_range": f"{timeline[0]['date']} to {timeline[-1]['date']}" if timeline else "N/A",
            "milestone_count": len(milestones),
            "duration_days": (max(dates) - min(dates)).days if dates else 0
        }

