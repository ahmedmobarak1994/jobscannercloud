# Search Engine Sources - Implementation Guide

## 🎯 STRATEGY: Two-Phase Approach

### **Phase 1: SEARCH ENGINES** ✅ (IMPLEMENTED)
Quick wins for broader coverage, especially NL market

### **Phase 2: EU ATS + Discovery** 🔜 (PLANNED)
Deeper integration with EU-specific ATS platforms

---

## ✅ PHASE 1: SEARCH ENGINES (IMPLEMENTED)

### **Why Search Engines First?**

**Problem we're solving:**
- Company ATS boards (Greenhouse/Lever/Ashby) miss NL startups
- Many NL companies don't explicitly mark "remote" in location field
- They mention it in description: "thuiswerken mogelijk", "flexible", "remote-first"

**Solution:**
Search engines find these jobs because they index full descriptions!

---

## 🌍 SOURCE 1: Adzuna NL

### **What is it?**
Official Jobs API for Netherlands market
- API: https://api.adzuna.com/v1/api/jobs/nl/search/{page}
- Coverage: ~10,000+ NL tech jobs
- Updates: Daily
- Quality: High (aggregates from Indeed, company sites, etc.)

### **Why Adzuna?**
✅ **Official API** (not scraping!)
✅ **NL-specific** (perfect for your market)
✅ **Description search** (finds "remote" in text)
✅ **Free tier** (5000 calls/month)
✅ **Stable** (used by major job sites)

### **Setup:**

1. **Get API credentials:**
   - Go to: https://developer.adzuna.com/signup
   - Sign up (free)
   - Get `app_id` and `app_key`

2. **Add to `.env`:**
   ```bash
   ADZUNA_APP_ID=your_app_id_here
   ADZUNA_APP_KEY=your_app_key_here
   ```

3. **Add to GitHub Secrets:**
   ```
   Repository → Settings → Secrets → Actions
   - ADZUNA_APP_ID
   - ADZUNA_APP_KEY
   ```

### **How to Use:**

**In config:**
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

**Query format:** `country:search_term:page`
- `country`: "nl" for Netherlands
- `search_term`: "site reliability engineer", "sre", "platform engineer"
- `page`: 1, 2, 3... (50 results per page)

### **Example Jobs:**
- SRE at NL startup (location: "Amsterdam", description: "remote mogelijk")
- Platform Engineer (location: "Netherlands", description: "thuiswerken 2 dagen/week")
- DevOps (location: "Utrecht", description: "flexible remote")

---

## 🌐 SOURCE 2: RemoteOK

### **What is it?**
Remote-only job board with public JSON feed
- API: https://remoteok.com/api
- Coverage: ~500-1000 remote tech jobs
- Updates: Multiple times daily
- Quality: Curated (human-verified remote jobs)

### **Why RemoteOK?**
✅ **No auth required** (public JSON)
✅ **Remote-only** (100% remote jobs)
✅ **Global coverage** (but can filter)
✅ **Tech-focused** (SRE/DevOps/Platform roles)
✅ **Fast** (single API call)

### **Setup:**
No credentials needed! Just add to config.

### **How to Use:**

**In config:**
```json
"remoteok": {
  "feeds": ["all"]
}
```

**Note:** RemoteOK returns ALL jobs in one call (~500-1000 jobs)
- Our filters (geo + title + score) will reduce to relevant matches

### **Example Jobs:**
- Remote SRE at EU startup
- Platform Engineer (Worldwide remote)
- DevOps Engineer (EMEA timezone)

---

## 📊 EXPECTED IMPACT

### **Volume:**
```
Current: ~6500 jobs (120+ sources)
With Adzuna: +200-500 NL jobs
With RemoteOK: +500-1000 remote jobs
Total: ~7200-8000 jobs scanned
```

### **After Filtering:**
```
Current passed: ~3-7 jobs
Expected with search engines: ~5-15 jobs
Extra matches: +2-8 per scan
```

### **Quality:**
✅ Same strict filters apply:
- Geo filtering (EU/EMEA)
- Title filtering (SRE/Platform/DevOps)
- Score threshold (min 5-8)
- Stack groups (min 1-2)

### **New Coverage:**
- ✅ NL startups (remote in text only)
- ✅ "Flexible remote" roles
- ✅ "Hybrid bespreekbaar" roles
- ✅ Companies without formal ATS

---

## 🧪 TESTING

### **1. Local Test (Without Slack):**
```bash
# Add credentials to .env
echo "ADZUNA_APP_ID=your_id" >> .env
echo "ADZUNA_APP_KEY=your_key" >> .env

# Test Adzuna
python3 << 'EOF'
from src.sources.adzuna import AdzunaSource
source = AdzunaSource()
jobs = source.fetch_jobs("nl:sre:1")
print(f"✅ Adzuna: {len(jobs)} jobs")
EOF

# Test RemoteOK
python3 << 'EOF'
from src.sources.remoteok import RemoteOKSource
source = RemoteOKSource()
jobs = source.fetch_jobs("all")
print(f"✅ RemoteOK: {len(jobs)} jobs")
EOF
```

### **2. Full Scan Test:**
```bash
# Add to config.explore.json first
python3 jobhunt.py --config config.explore.json scan --dry-run
```

Watch for:
```
✓ adzuna/nl:sre:1: X jobs
✓ remoteok/all: Y jobs
```

### **3. GitHub Actions:**
After testing locally, add to `config.balanced.json` and push.

---

## ⚙️ CONFIGURATION OPTIONS

### **Adzuna Queries:**

**Broad (more volume):**
```json
"adzuna": {
  "queries": [
    "nl:cloud engineer:1",
    "nl:platform engineer:1",
    "nl:infrastructure engineer:1"
  ]
}
```

**Focused (less volume, higher quality):**
```json
"adzuna": {
  "queries": [
    "nl:site reliability engineer:1",
    "nl:sre:1",
    "nl:platform sre:1"
  ]
}
```

**Multi-page (more results per query):**
```json
"adzuna": {
  "queries": [
    "nl:sre:1",
    "nl:sre:2",
    "nl:sre:3"
  ]
}
```

### **RemoteOK:**

```json
"remoteok": {
  "feeds": ["all"]
}
```

(RemoteOK only has one feed - all remote jobs)

---

## 🔧 TROUBLESHOOTING

### **Adzuna: 401 Unauthorized**
```
❌ Adzuna credentials not found (ADZUNA_APP_ID, ADZUNA_APP_KEY)
```
**Fix:** Add credentials to `.env` or GitHub Secrets

### **Adzuna: 429 Too Many Requests**
```
❌ Adzuna API error: 429
```
**Fix:** 
- Free tier: 5000 calls/month
- Reduce number of queries
- Or upgrade to paid tier

### **RemoteOK: Empty Results**
```
✓ remoteok/all: 0 jobs
```
**Fix:**
- RemoteOK might be temporarily down
- Source health will mark as TEMP_FAIL
- Will retry next scan

### **No New Matches**
```
Jobs passed: 3 (same as before)
```
**Fix:**
- Check if queries are too specific
- Lower `min_score` in explore config
- Check if remote detection works (search engines return "Remote" in location)

---

## 🎯 PHASE 2: WHAT'S NEXT?

**If Phase 1 works well, we'll add:**

### **1. EU ATS Sources** (Priority order)
1. **Recruitee** (most NL/EU startups use this)
2. **Workable** (popular globally, some EU)
3. **Personio** (German market leader)
4. **Pinpoint** (UK/EU scale-ups)
5. **Teamtailor** (Nordic + EU)

### **2. Discovery Pipeline**
- Parse GitHub company lists:
  - remoteintech/remote-jobs
  - yanirs/established-remote
  - EuropeanRemote/european-remote-software-companies
- Auto-detect ATS from company websites
- Output: discovered.sources.json

### **3. `ingest-urls` Command**
```bash
# You find jobs on Indeed/Talent, paste URLs
python3 jobhunt.py ingest-urls --file urls.txt
```
- Auto-detects ATS from apply URLs
- Adds to discovered sources
- Super practical for manual discovery!

### **4. Digest Mode**
- Two-tier output:
  - Slack: High signal (strict)
  - Digest: Medium signal (review weekly)
- No spam, more options

---

## 📈 SUCCESS METRICS

### **After 1 Week:**

**Search Engines Working:**
- ✅ Adzuna scans successfully
- ✅ RemoteOK scans successfully
- ✅ +2-8 new matches per week
- ✅ At least 1 NL startup job found
- ✅ No API errors / rate limits

**Ready for Phase 2:**
- ✅ Search engines stable
- ✅ No performance issues
- ✅ Filters work well
- ✅ User happy with results

---

## ✅ SUMMARY

**Implemented:**
- ✅ Adzuna NL API integration
- ✅ RemoteOK JSON feed integration
- ✅ Both registered in SOURCE_REGISTRY
- ✅ Error handling + retries
- ✅ Source health tracking

**Next Actions:**
1. Get Adzuna API credentials
2. Add to `.env` locally
3. Test: `python3 jobhunt.py scan --config config.explore.json`
4. If works: Add to `config.balanced.json`
5. Add to GitHub Secrets
6. Monitor results for 1 week

**Future (Phase 2):**
- EU ATS (Recruitee first!)
- Discovery pipeline
- `ingest-urls` command
- Digest mode

**SEARCH ENGINES ARE LIVE - TEST THEM!** 🚀

