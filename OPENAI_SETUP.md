# 🔑 OpenAI API Setup Guide

## Why GPT-4o-mini?

The project now uses **GPT-4o-mini** instead of GPT-2 because:
- ✅ Much better text quality and coherence
- ✅ More realistic and meaningful completions
- ✅ Better for demonstrating bias detection
- ✅ More accurate reflection of real-world AI systems
- ✅ Cost-effective (~$0.15 per 1M input tokens, $0.60 per 1M output tokens)

---

## Setup Instructions

### Step 1: Get an OpenAI API Key

1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Create an account or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy your API key (starts with `sk-...`)
6. **Important:** Store it securely - you won't be able to see it again!

### Step 2: Set the API Key as Environment Variable

#### Option A: Set Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

#### Option B: Use .env File

1. Create a file named `.env` in the project root
2. Add this line:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Install python-dotenv (already in requirements.txt)
4. The scripts will automatically load it

### Step 3: Install Required Packages

```bash
pip install openai python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

---

## Usage

### Generate Text

```bash
python src/generate_text.py combined
```

### Run Web Demo

```bash
streamlit run app_multi_bias.py
```

---

## Cost Estimation

**GPT-4o-mini Pricing:**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**For this project:**
- ~25 prompts × ~60 tokens each = ~1,500 tokens
- Cost per run: **~$0.001** (less than a penny!)
- 1,000 runs would cost ~$1

**Very affordable for academic projects!**

---

## Troubleshooting

### "OpenAI API key not found"

**Solution:** Make sure you've set the environment variable in the same terminal session where you run the script.

```powershell
# Set the key
$env:OPENAI_API_KEY="sk-your-key"

# Then run the script
python src/generate_text.py combined
```

### "Rate limit exceeded"

**Solution:** The scripts include delays between requests. If you still hit limits:
- Increase the `time.sleep()` value in the script
- Request a rate limit increase from OpenAI
- Use a paid OpenAI account (higher limits)

### "Insufficient quota"

**Solution:** 
- Add credits to your OpenAI account
- Check your usage limits at [https://platform.openai.com/usage](https://platform.openai.com/usage)
- New accounts get $5 free credit

---

## Security Best Practices

1. ✅ **Never commit API keys** to Git
   - The `.gitignore` file already excludes `.env`
   
2. ✅ **Use environment variables** instead of hardcoding

3. ✅ **Rotate keys regularly** for production use

4. ✅ **Set spending limits** in OpenAI dashboard

5. ✅ **Monitor usage** to avoid unexpected charges

---

## Alternative: Use GPT-2 (Free, Offline)

If you don't want to use OpenAI API, you can revert to GPT-2:

1. Edit `src/generate_text.py`
2. Change back to:
   ```python
   from transformers import pipeline
   generator = pipeline('text-generation', model='gpt2')
   ```

**Pros:** Free, runs locally, no API needed
**Cons:** Lower quality text, less coherent, requires more disk space

---

## Quick Start Checklist

- [ ] Created OpenAI account
- [ ] Generated API key
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Installed requirements: `pip install -r requirements.txt`
- [ ] Tested generation: `python src/generate_text.py gender`
- [ ] Verified web app: `streamlit run app_multi_bias.py`

---

## Example Session

```powershell
# Set API key
PS> $env:OPENAI_API_KEY="sk-proj-abc123..."

# Verify it's set
PS> echo $env:OPENAI_API_KEY
sk-proj-abc123...

# Run text generation
PS> python src/generate_text.py gender

# Output:
# ========================================
# MULTI-BIAS AI TEXT GENERATION (GPT-4o-mini)
# ========================================
# 
# Bias Type: GENDER
# ✓ OpenAI API key configured
# Using GPT-4o-mini for high-quality text generation
# ...
```

---

## Need Help?

- OpenAI Documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- OpenAI API Reference: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- Check your usage: [https://platform.openai.com/usage](https://platform.openai.com/usage)

---

**Ready to generate high-quality biased text for analysis! 🚀**
