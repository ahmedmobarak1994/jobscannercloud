# TEST INSTRUCTIES - SEARCH ENGINES

## ✅ ALLES IS KLAAR!

**Credentials toegevoegd:**
- ✅ ADZUNA_APP_ID: eefa3bf0
- ✅ ADZUNA_APP_KEY: d8f65cb6ece4e2f3bb8c5ff1b6b09cf1
- ✅ Opgeslagen in: .env

**Sources geïmplementeerd:**
- ✅ RemoteOK (geen auth)
- ✅ Adzuna (credentials ready)

---

## 🚀 TEST OPTIE 1: QUICK TEST (AANBEVOLEN)

```bash
cd /Users/ahmedmobarak/Downloads/remote-sre-job-scanner
python3 quick_test.py
```

**Dit test:**
- RemoteOK API call
- Adzuna API call
- Toont sample jobs
- Verifieert dat beide werken

**Verwachte output:**
```
======================================================================
TESTING SEARCH ENGINES
======================================================================

1. Testing RemoteOK...
✅ RemoteOK: 500+ jobs fetched
   Relevant (SRE/Platform): 50-100 jobs
   Example: Senior SRE @ Company X

2. Testing Adzuna...
✅ Adzuna: 20-50 jobs fetched (query: 'site reliability engineer')
   Example: Site Reliability Engineer @ Dutch Startup (Amsterdam)

======================================================================
BOTH SOURCES TESTED!
======================================================================
```

---

## 🚀 TEST OPTIE 2: FULL SCAN (COMPLEET)

```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
```

**Dit test:**
- Alle sources (incl. Greenhouse/Lever/Ashby/Remotive/WWR/RemoteOK)
- Filtering pipeline
- Scoring
- Output naar explore.md

**Verwachte output:**
```
✅ Slack webhook configured
🚀 Starting job scan...
  📦 Scanning 122 sources...
  
  ... (existing sources) ...
  
  ✓ remoteok/all: 500+ jobs
  
🔍 Filtering 7000+ jobs...

============================================================
📊 SCAN SUMMARY
============================================================
  Sources scanned:   122
  Jobs fetched:      7000+
  Jobs passed:       15-25 (was 3-7!)
  New jobs:          X
  Errors:            Y
============================================================

📝 Explore output written to: out/explore.md
```

**Check resultaten:**
```bash
cat out/explore.md
```

---

## 📊 WAT JE ZOU MOETEN ZIEN:

### **In Scan Output:**
- ✅ `✓ remoteok/all: X jobs`
- ✅ Geen errors voor RemoteOK
- ✅ Meer jobs passed dan normaal
- ✅ Explore.md gegenereerd

### **In out/explore.md:**
- Meer remote SRE/Platform jobs
- NL startup jobs
- "Remote mogelijk" in beschrijvingen
- Global remote-first companies
- Meer variëteit dan voorheen

---

## ⚠️ MOGELIJKE PROBLEMEN:

### **Als Adzuna fails:**
```
❌ Adzuna failed: 401 Unauthorized
```
**Check:**
- Credentials correct in .env?
- `cat .env` om te verifiëren

### **Als RemoteOK fails:**
```
❌ RemoteOK failed: ...
```
**Mogelijke oorzaken:**
- Site temporarily down
- Rate limiting
- Network issue
**Fix:** Try again later

### **Als geen nieuwe matches:**
```
Jobs passed: 3 (same as before)
```
**Mogelijke oorzaken:**
- Filters zijn heel streng
- Search engines leveren jobs die niet door filters komen
**Check:** 
- Lower min_score in config.explore.json
- Check explore.md voor near-misses

---

## ✅ SUCCESS CRITERIA:

**Quick test:**
- [ ] Both sources return jobs
- [ ] No errors
- [ ] Sample jobs shown

**Full scan:**
- [ ] RemoteOK scanned successfully
- [ ] More jobs passed than usual
- [ ] explore.md generated
- [ ] Contains relevant jobs

---

## 🎯 NEXT STEPS NA SUCCESVOLLE TEST:

### **1. Add Adzuna queries to config**

Edit `config.explore.json`:
```json
"adzuna": {
  "queries": [
    "nl:site reliability engineer:1",
    "nl:platform engineer:1",
    "nl:devops engineer:1",
    "nl:cloud engineer:1"
  ]
}
```

### **2. Add to GitHub Secrets**

```
Repository → Settings → Secrets → Actions
+ ADZUNA_APP_ID = eefa3bf0
+ ADZUNA_APP_KEY = d8f65cb6ece4e2f3bb8c5ff1b6b09cf1
```

### **3. Test via GitHub Actions**

Push and trigger workflow to test in CI.

### **4. Add to Production Config**

If all works well, add to `config.balanced.json`.

### **5. Monitor Results**

- Check Slack for new matches
- Review explore.md weekly
- Adjust queries as needed

---

## 🚀 RUN NU:

```bash
cd /Users/ahmedmobarak/Downloads/remote-sre-job-scanner
python3 quick_test.py
```

**OF:**

```bash
python3 jobhunt.py --config config.explore.json scan --dry-run
cat out/explore.md
```

---

## 📝 HULP NODIG?

**Check deze files:**
- `SEARCH_ENGINES.md` - Complete documentatie
- `QUICK_START_SEARCH_ENGINES.md` - Step-by-step guide
- `TEST_STATUS.md` - Current status

**Of debug:**
```bash
# Check if sources load
python3 -c "from src.sources.remoteok import RemoteOKSource; print('RemoteOK OK')"
python3 -c "from src.sources.adzuna import AdzunaSource; print('Adzuna OK')"

# Check credentials
cat .env
```

---

**ALLES IS KLAAR - GA TESTEN!** 🚀

