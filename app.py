"""
AI News Orchestrator - Streamlit Application
Main UI for the news timeline generator
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import json

from news_fetcher import NewsFetcher
from article_processor import ArticleProcessor
from ai_analyzer import AIAnalyzer
from timeline_generator import TimelineGenerator
from credibility_scorer import CredibilityScorer
from utils import validate_api_keys


# Page configuration
st.set_page_config(
    page_title="AI News Orchestrator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "articles" not in st.session_state:
        st.session_state.articles = []
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}
    if "timeline" not in st.session_state:
        st.session_state.timeline = []
    if "credibility" not in st.session_state:
        st.session_state.credibility = {}


def create_timeline_visualization(timeline: list) -> go.Figure:
    """Create interactive timeline visualization using Plotly"""
    if not timeline:
        return None
    
    # Prepare data
    dates = [datetime.strptime(e["date"], "%Y-%m-%d") for e in timeline]
    events = [e["event"][:100] + "..." if len(e["event"]) > 100 else e["event"] for e in timeline]
    milestones = [e.get("is_milestone", False) for e in timeline]
    
    # Create figure
    fig = go.Figure()
    
    # Add milestone events
    milestone_dates = [d for d, m in zip(dates, milestones) if m]
    milestone_events = [e for e, m in zip(events, milestones) if m]
    
    if milestone_dates:
        fig.add_trace(go.Scatter(
            x=milestone_dates,
            y=[1] * len(milestone_dates),
            mode='markers+text',
            marker=dict(size=15, color='#ff6b6b', symbol='star'),
            text=[f"⭐ {e[:50]}" for e in milestone_events],
            textposition="top center",
            name="Milestones",
            hovertemplate="<b>%{text}</b><br>Date: %{x}<extra></extra>"
        ))
    
    # Add regular events
    regular_dates = [d for d, m in zip(dates, milestones) if not m]
    regular_events = [e for e, m in zip(events, milestones) if not m]
    
    if regular_dates:
        fig.add_trace(go.Scatter(
            x=regular_dates,
            y=[0.5] * len(regular_dates),
            mode='markers+text',
            marker=dict(size=10, color='#4ecdc4', symbol='circle'),
            text=[e[:50] for e in regular_events],
            textposition="top center",
            name="Events",
            hovertemplate="<b>%{text}</b><br>Date: %{x}<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title="Event Timeline",
        xaxis_title="Date",
        yaxis=dict(showgrid=False, showticklabels=False, range=[-0.5, 2]),
        height=400,
        hovermode='closest',
        showlegend=True,
        template="plotly_white"
    )
    
    return fig


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📰 AI News Orchestrator</h1>', unsafe_allow_html=True)
    st.markdown("### Reconstruct the story from multiple news sources")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key Status
        api_status = validate_api_keys()
        st.subheader("API Status")
        
        if api_status["newsapi"]:
            st.success("✅ NewsAPI")
        else:
            st.warning("⚠️ NewsAPI key not set")
            st.info("Get your free API key at: https://newsapi.org/register")
        
        if api_status["llm"]:
            st.success("✅ LLM API")
        else:
            st.warning("⚠️ LLM API key not set")
            st.info("Set OPENAI_API_KEY or GEMINI_API_KEY in .env file")
        
        st.divider()
        
        # Settings
        st.subheader("Settings")
        max_articles = st.slider("Max Articles", 5, 20, 10)
        days_back = st.slider("Days to look back", 7, 90, 30)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        event_query = st.text_input(
            "Enter event title or keyword",
            placeholder="e.g., Chandrayaan-3 Mission, OpenAI GPT-5 Launch, COP28 Summit",
            key="event_input"
        )
    
    with col2:
        st.write("")  # Spacing
        analyze_button = st.button("🔍 Analyze Event", type="primary", use_container_width=True)
    
    # Analyze button clicked
    if analyze_button and event_query:
        with st.spinner("Fetching and analyzing news articles..."):
            try:
                # Initialize components
                fetcher = NewsFetcher()
                processor = ArticleProcessor()
                analyzer = AIAnalyzer()
                timeline_gen = TimelineGenerator()
                scorer = CredibilityScorer()
                
                # Fetch articles
                st.info(f"📡 Fetching articles for: {event_query}")
                articles = fetcher.fetch_articles(event_query, days_back=days_back)
                
                if not articles:
                    st.error("❌ No articles found. Try a different search term or check your API keys.")
                    return
                
                st.success(f"✅ Found {len(articles)} articles")
                
                # Process articles
                st.info("🔧 Processing articles...")
                processed_articles = processor.process_articles(articles[:max_articles])
                
                # Analyze with AI
                st.info("🤖 Analyzing with AI...")
                analysis = analyzer.analyze_event(processed_articles, event_query)
                
                # Generate timeline
                st.info("📅 Generating timeline...")
                timeline = timeline_gen.generate_timeline(analysis, processed_articles)
                
                # Score credibility
                st.info("⭐ Scoring credibility...")
                credibility = scorer.score_all_sources(processed_articles)
                
                # Store in session state
                st.session_state.articles = processed_articles
                st.session_state.analysis = analysis
                st.session_state.timeline = timeline
                st.session_state.credibility = credibility
                
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
    
    # Display results
    if st.session_state.timeline:
        st.divider()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Articles Analyzed", len(st.session_state.articles))
        
        with col2:
            st.metric("Timeline Events", len(st.session_state.timeline))
        
        with col3:
            timeline_gen = TimelineGenerator()
            timeline_stats = timeline_gen.get_timeline_stats(st.session_state.timeline)
            st.metric("Date Range", timeline_stats.get("duration_days", 0), "days")
        
        with col4:
            scorer = CredibilityScorer()
            avg_auth = st.session_state.credibility.get("average_authenticity", 0)
            auth_level = scorer.get_authenticity_level(avg_auth)
            st.metric("Avg Authenticity", f"{avg_auth}%", auth_level)
        
        st.divider()
        
        # Timeline Visualization
        st.subheader("📅 Event Timeline")
        timeline_fig = create_timeline_visualization(st.session_state.timeline)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        # Timeline Text
        with st.expander("📋 View Timeline Details", expanded=False):
            timeline_gen = TimelineGenerator()
            timeline_text = timeline_gen.format_timeline_for_display(st.session_state.timeline)
            st.text(timeline_text)
        
        # Event Summary
        st.subheader("📝 Event Summary")
        if "summary" in st.session_state.analysis:
            st.write(st.session_state.analysis["summary"])
        else:
            st.info("Summary not available")
        
        # Key Highlights
        if "key_highlights" in st.session_state.analysis and st.session_state.analysis["key_highlights"]:
            st.subheader("✨ Key Highlights")
            for highlight in st.session_state.analysis["key_highlights"]:
                st.markdown(f"- {highlight}")
        
        # Verified Facts
        if "verified_facts" in st.session_state.analysis and st.session_state.analysis["verified_facts"]:
            st.subheader("✅ Verified Facts")
            for fact in st.session_state.analysis["verified_facts"]:
                st.markdown(f"- {fact}")
        
        # Discrepancies / Conflicts
        
        # Named Entity Recognition (NER) Results
        
        # Remove duplicates and display
        
        # Sources and Credibility
        st.subheader("📚 Sources & Credibility")
        
        source_scores = st.session_state.credibility.get("source_scores", {})
        article_scores = st.session_state.credibility.get("article_scores", [])
        
        # Sort articles by credibility score (highest first)
        articles_with_scores = []
        for i, article in enumerate(st.session_state.articles):
            score = article_scores[i]["overall_score"] if i < len(article_scores) else 0
            articles_with_scores.append((article, score, i))
        
        # Sort by score (descending)
        articles_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Display sources in columns (sorted by credibility)
        for article, score, original_idx in articles_with_scores:
            with st.expander(f"📰 {article.get('title', 'Untitled')[:60]}...", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Source:** {article.get('source', 'Unknown')}")
                    st.write(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                    if article.get('url'):
                        st.markdown(f"[Read Full Article]({article['url']})")
                
                with col2:
                    if original_idx < len(article_scores):
                        score_data = article_scores[original_idx]
                        scorer = CredibilityScorer()
                        overall = score_data["overall_score"]
                        auth_level = scorer.get_authenticity_level(overall)
                        
                        st.metric("Credibility", f"{overall}%", auth_level)
                        
                        if score_data.get("is_clickbait"):
                            st.warning("⚠️ Possible clickbait")
                        
                        if score_data.get("flags"):
                            for flag in score_data["flags"]:
                                st.caption(f"⚠️ {flag}")
        
        # Export options
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            export_data = {
                "event_query": event_query if 'event_input' in st.session_state else "",
                "analysis": st.session_state.analysis,
                "timeline": st.session_state.timeline,
                "credibility": st.session_state.credibility,
                "articles_count": len(st.session_state.articles)
            }
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(export_data, indent=2, default=str),
                file_name=f"news_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Timeline text export
            timeline_gen = TimelineGenerator()
            timeline_text = timeline_gen.format_timeline_for_display(st.session_state.timeline)
            st.download_button(
                label="📥 Download Timeline",
                data=timeline_text,
                file_name=f"timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


if __name__ == "__main__":
    main()

