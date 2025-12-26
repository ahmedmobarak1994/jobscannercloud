# Quick Start - Test Search Engines Locally

## 🚀 LOKAAL TESTEN (NU!)

### **Stap 1: Test RemoteOK (geen credentials nodig)**

```bash
cd /Users/ahmedmobarak/Downloads/remote-sre-job-scanner
python3 test_search_engines.py
```

**Verwacht output:**
```
🧪 TESTING SEARCH ENGINE SOURCES
======================================================================

1️⃣  Testing RemoteOK...
----------------------------------------------------------------------
✅ RemoteOK: Fetched 500+ jobs

📝 Sample job:
  Title:    Senior Site Reliability Engineer
  Company:  Some Remote Company
  Location: Remote
  URL:      https://remoteok.com/remote-jobs/...

🎯 Relevant jobs (SRE/Platform/DevOps): 50-100

✅ RemoteOK source: WORKING
```

**Als dit werkt:** RemoteOK is ready to use!

---

### **Stap 2: Get Adzuna Credentials**

1. **Sign up (gratis):**
   - Go to: https://developer.adzuna.com/signup
   - Fill in form
   - Verify email
   - Get your `app_id` and `app_key`

2. **Add to `.env`:**
   ```bash
   echo "ADZUNA_APP_ID=your_app_id_here" >> .env
   echo "ADZUNA_APP_KEY=your_app_key_here" >> .env
   ```

3. **Test Adzuna:**
   ```bash
   python3 test_search_engines.py
   ```

**Verwacht output:**
```
2️⃣  Testing Adzuna...
----------------------------------------------------------------------
✅ Adzuna: Fetched 20-50 jobs (query: 'site reliability engineer')

📝 Sample job:
  Title:    Site Reliability Engineer
  Company:  Dutch Startup
  Location: Amsterdam, Netherlands
  URL:      https://www.adzuna.nl/...

🎯 All jobs from this query: 30

Top 5 jobs:
  1. Senior SRE @ Company A (Amsterdam)
  2. Platform Engineer @ Company B (Netherlands)
  3. DevOps Engineer @ Company C (Utrecht)
  ...

✅ Adzuna source: WORKING
```

**Als dit werkt:** Adzuna is ready to use!

---

### **Stap 3: Add to Config (Explore Mode)**

Create a test config or add to explore:

```bash
# Add RemoteOK to config.explore.json
```

**Edit `config.explore.json`:**
```json
{
  "sources": {
    ...existing sources...
    "remoteok": {
      "feeds": ["all"]
    }
  }
}
```

**If you have Adzuna credentials, also add:**
```json
{
  "sources": {
    ...existing sources...
    "adzuna": {
      "queries": [
        "nl:site reliability engineer:1",
        "nl:platform engineer:1",
        "nl:devops engineer:1"
      ]
    },
    "remoteok": {
      "feeds": ["all"]
    }
  }
}
```

---

### **Stap 4: Test Full Scan**

```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
```

**Watch for:**
```
✓ remoteok/all: 500+ jobs
✓ adzuna/nl:site reliability engineer:1: 20-50 jobs
✓ adzuna/nl:platform engineer:1: 20-50 jobs
✓ adzuna/nl:devops engineer:1: 20-50 jobs

🔍 Filtering 7000+ jobs...

Jobs passed: 10-20 (up from 3-7!)
```

---

### **Stap 5: Check Results**

If explore mode:
```bash
cat out/explore.md
```

You should see:
- More NL startup jobs
- Jobs with "remote mogelijk" in description
- More "platform engineer" roles
- More variety!

---

## ⚠️ TROUBLESHOOTING

### **RemoteOK: 0 jobs**
```python
print("RemoteOK might be down, try again later")
```

### **Adzuna: 401 Error**
```bash
# Check credentials
echo $ADZUNA_APP_ID
echo $ADZUNA_APP_KEY

# Re-add if empty
echo "ADZUNA_APP_ID=..." >> .env
echo "ADZUNA_APP_KEY=..." >> .env
```

### **No New Matches**
```bash
# Lower threshold in explore config
"min_score": 3  # was 5
```

### **Too Many Matches**
```bash
# Raise threshold
"min_score": 8  # was 5
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Run `python3 test_search_engines.py`
- [ ] RemoteOK returns 500+ jobs
- [ ] Get Adzuna credentials
- [ ] Adzuna returns 20+ jobs per query
- [ ] Add to config.explore.json
- [ ] Full scan test works
- [ ] See more results than before

---

## 🎯 NEXT STEPS

**If tests pass:**
1. Add to GitHub Secrets (ADZUNA_APP_ID, ADZUNA_APP_KEY)
2. Add to config.balanced.json (production)
3. Monitor Slack for new matches
4. Review out/explore.md weekly

**If tests fail:**
- Check error messages
- Verify credentials
- Check SEARCH_ENGINES.md for troubleshooting

---

## 📝 QUICK REFERENCE

**Test script:**
```bash
python3 test_search_engines.py
```

**Test scan:**
```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
```

**Get Adzuna credentials:**
https://developer.adzuna.com/signup

**Add to .env:**
```bash
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
```

**GO TEST NOW!** 🚀

