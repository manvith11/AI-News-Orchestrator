# Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Install spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

## Step 3: Get API Keys

### NewsAPI (Required)
1. Go to https://newsapi.org/register
2. Sign up for free account (100 requests/day)
3. Copy your API key

### LLM Provider (Choose One)

**Option A: Google Gemini (FREE - Recommended for Demo)**
1. Go to https://makersuite.google.com/app/apikey
2. Create API key (no credit card needed!)
3. Free tier: 60 requests/minute - perfect for demo

**Option B: OpenAI (Paid - $0.001-0.002 per request)**
1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Add credits to your account (requires payment)

## Step 4: Configure Environment

### What is `.env` file?
The `.env` file stores your API keys securely. It's like a password file that the app reads to connect to APIs.

### How to create it:

**Method 1: Manual (Easiest)**
1. In your project folder, create a new file named `.env` (just `.env`, nothing else)
2. Open it in any text editor (Notepad, VS Code, etc.)
3. Copy and paste this content:
   ```env
   NEWSAPI_KEY=your_newsapi_key_here
   GEMINI_API_KEY=your_gemini_key_here
   LLM_PROVIDER=gemini
   ```
4. Replace `your_newsapi_key_here` with your actual NewsAPI key
5. Replace `your_gemini_key_here` with your actual Gemini key
6. Save the file

**Method 2: Using Command (Optional)**
```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Windows CMD
copy .env.example .env

# On Mac/Linux
cp .env.example .env
```

Then edit `.env` and replace the placeholder text with your actual API keys.

**Note**: Gemini is FREE and perfect for demo! No payment needed.

## Step 5: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser automatically!

## Testing Without API Keys

The system will work in a limited mode without API keys:
- News fetching will fail (need NewsAPI)
- AI analysis will use basic fallback (no LLM features)
- Timeline generation will still work with cached data

## Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**spaCy model missing?**
```bash
python -m spacy download en_core_web_sm
```

**API errors?**
- Check your API keys are correct
- Verify you have credits/quota remaining
- Check internet connection

## Next Steps

1. Try searching for an event: "Chandrayaan-3 Mission"
2. Explore the timeline visualization
3. Check source credibility scores
4. Export results as JSON

Happy analyzing! 🚀

