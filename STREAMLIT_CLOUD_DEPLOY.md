# Streamlit Cloud Deployment Guide 🚀

## Quick Comparison

| Platform | Free? | Setup Time | Best For |
|----------|-------|------------|----------|
| **Streamlit Cloud** | ✅ Yes | 5 minutes | **Streamlit apps (RECOMMENDED)** |
| Railway | ✅ Free tier | 10 minutes | General apps |
| Render | ✅ Free tier | 15 minutes | General apps |
| Heroku | ❌ Paid now | 20 minutes | Legacy apps |
| AWS/GCP | ❌ Complex | 30+ minutes | Production apps |

**Winner: Streamlit Cloud** - Perfect for your use case!

---

## Step-by-Step Deployment

### Prerequisites
1. GitHub account (free)
2. Streamlit Cloud account (free)
3. Your API keys ready

### Step 1: Prepare Your Code

Make sure your project is ready:
```bash
# Check you have these files:
- app.py
- requirements.txt
- All your Python modules
- README.md
```

### Step 2: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "AI News Orchestrator - Ready for deployment"

# Create repository on GitHub (via website)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` (it should be already)

### Step 3: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app" button
   - Select your repository
   - Select branch: `main`
   - Main file path: `app.py`

3. **Add Secrets (API Keys)**
   - Click "Advanced settings"
   - Go to "Secrets" tab
   - Add these secrets:
   ```
   NEWSAPI_KEY=your_actual_newsapi_key_here
   GEMINI_API_KEY=your_actual_gemini_key_here
   LLM_PROVIDER=gemini
   ```
   - Click "Save"

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://your-app-name.streamlit.app`

### Step 4: Share with Mentor

Copy the Streamlit Cloud URL and share it!

---

## Alternative: Railway (If Streamlit Cloud Fails)

If for some reason Streamlit Cloud doesn't work:

### Railway Setup

1. **Sign up**: https://railway.app (free tier available)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure**
   - Add environment variables:
     - `NEWSAPI_KEY`
     - `GEMINI_API_KEY`
     - `LLM_PROVIDER=gemini`
   - Set start command: `streamlit run app.py --server.port $PORT`

4. **Deploy**
   - Railway auto-detects and deploys
   - Get your URL

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure `requirements.txt` has all dependencies

### Issue: "API key not working"
**Solution:** Double-check secrets in Streamlit Cloud settings

### Issue: "spaCy model error"
**Solution:** Add to `requirements.txt`:
```
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

Or add to your deployment:
```python
# In app.py, add at the top:
import subprocess
subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=False)
```

### Issue: "App not loading"
**Solution:** 
- Check Streamlit Cloud logs
- Verify `app.py` is the main file
- Check all imports are correct

---

## Final Checklist

Before deploying:
- [ ] All code is pushed to GitHub
- [ ] `.env` is NOT in repository (in `.gitignore`)
- [ ] `requirements.txt` is complete
- [ ] API keys are ready
- [ ] Tested locally first

After deploying:
- [ ] App loads successfully
- [ ] API keys work (test with a query)
- [ ] All features work
- [ ] Share link with mentor

---

## Cost: $0.00

Everything is FREE:
- Streamlit Cloud: FREE
- GitHub: FREE
- NewsAPI: FREE (100 req/day)
- Gemini: FREE (60 req/min)

Perfect for your competition! 🎉

