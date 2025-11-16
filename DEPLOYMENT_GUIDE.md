# Free Deployment Guide 🚀

## Deploy Without Paying Anything!

This guide shows you how to deploy the AI News Orchestrator using **100% FREE APIs**.

### Required FREE APIs

1. **NewsAPI** - FREE (100 requests/day)
   - Sign up: https://newsapi.org/register
   - No credit card needed
   - Perfect for demo/testing

2. **Google Gemini** - FREE (60 requests/minute)
   - Get key: https://makersuite.google.com/app/apikey
   - No credit card needed
   - No payment required

### Step-by-Step Deployment

#### Option 1: Streamlit Cloud (Easiest - FREE)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your_repo_url
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Add secrets (API keys):
     ```
     NEWSAPI_KEY=your_newsapi_key
     GEMINI_API_KEY=your_gemini_key
     LLM_PROVIDER=gemini
     ```
   - Click "Deploy"

3. **Share the link** with your mentor!

#### Option 2: Other Platforms (Heroku, Railway, etc.)

1. **Set environment variables** in your platform:
   ```
   NEWSAPI_KEY=your_key
   GEMINI_API_KEY=your_key
   LLM_PROVIDER=gemini
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Run**:
   ```bash
   streamlit run app.py --server.port $PORT
   ```

### Configuration for Free Deployment

Your `.env` file should look like:
```env
# FREE APIs - No payment needed!
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_key_here
LLM_PROVIDER=gemini

# Optional settings
MAX_ARTICLES=10
NEWSAPI_LANGUAGE=en
CACHE_ARTICLES=true
```

### What Works with Free APIs

✅ News fetching (100 articles/day free)
✅ AI-powered timeline generation (Gemini free tier)
✅ Event summarization
✅ Source credibility scoring
✅ All features work perfectly!

### Rate Limits (Free Tiers)

- **NewsAPI**: 100 requests/day (enough for demo)
- **Gemini**: 60 requests/minute (more than enough)

### Troubleshooting

**If you hit rate limits:**
- The system caches articles, so re-analyzing same event doesn't use API
- NewsAPI limit resets daily
- Gemini limit resets per minute

**For production/demo:**
- Free tiers are sufficient for mentor review
- If needed, you can upgrade later (but not required)

### Cost Summary

💰 **Total Cost: $0.00**
- NewsAPI: FREE
- Gemini: FREE
- Deployment: FREE (Streamlit Cloud)

Perfect for your Vibethon submission! 🎉

