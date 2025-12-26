# Job Boards Added - Summary

## ✅ NIEUWE JOB BOARDS (2)

### 1. **Remotive.com** 🌍

**Type:** Public API (JSON)

**Coverage:**
- ~100-200 software development jobs
- Global remote job board
- Updates daily
- No authentication required

**Categories:**
- software-dev (default)

**URL:** https://remotive.com/api/remote-jobs

**Integration:**
```json
"remotive": {
  "categories": ["software-dev"]
}
```

**Sample jobs:**
- Remote SRE roles
- Platform Engineering
- DevOps positions
- Infrastructure roles

---

### 2. **WeWorkRemotely (WWR)** 📡

**Type:** RSS Feed (XML)

**Coverage:**
- ~50-100 jobs per category
- Curated remote jobs
- Updates multiple times daily
- No authentication required

**Categories:**
- programming
- devops

**URL:** https://weworkremotely.com/categories/remote-programming-jobs.rss

**Integration:**
```json
"weworkremotely": {
  "categories": ["programming", "devops"]
}
```

**Sample jobs:**
- Full-stack roles (filtered by our keywords)
- DevOps/SRE
- Platform teams
- Infrastructure engineers

---

## 📊 EXPECTED IMPACT

### **Volume Increase:**
```
Before: ~6200 jobs from 120 sources
After:  ~6400-6500 jobs from 122 sources (+3-5%)
```

### **Quality:**
Same strict filtering applies:
- ✅ Geo filtering (EU/EMEA only)
- ✅ Title filtering (SRE/Platform/DevOps)
- ✅ Stack groups (min 1-2)
- ✅ Score threshold (min 5-8)

### **Unique Coverage:**
Job boards often have roles NOT on company career pages:
- Startups without formal ATS
- Contract/freelance (filtered out if not FTE)
- Companies using multiple posting platforms

---

## 🔧 TECHNICAL DETAILS

### **Remotive Source**
```python
class RemotiveSource(BaseSource):
    BASE_URL = "https://remotive.com/api/remote-jobs"
    
    def fetch_jobs(category: str) -> List[Job]:
        # Fetch JSON
        # Parse to Job model
        # Same error handling as Greenhouse
```

**Features:**
- 10s timeout
- JSON parsing with error handling
- HTML description → plain text
- candidate_required_location → location field

### **WeWorkRemotely Source**
```python
class WeWorkRemotelySource(BaseSource):
    RSS_URL = "https://weworkremotely.com/..."
    
    def fetch_jobs(category: str) -> List[Job]:
        # Fetch RSS XML
        # Parse with ElementTree
        # Extract company from title
```

**Features:**
- 10s timeout
- XML parsing with error handling
- Company extraction from "Company: Title" format
- HTML cleanup in descriptions

---

## 🧪 TESTING

Both sources have been:
- ✅ Unit tested (API/RSS calls work)
- ✅ Integrated into scanner
- ✅ Added to config.balanced.json
- ✅ Registered in SOURCE_REGISTRY

**Next scan will include them automatically!**

---

## 📈 MONITORING

Watch for these in logs:
```
✓ remotive/software-dev: X jobs
✓ weworkremotely/programming: Y jobs
✓ weworkremotely/devops: Z jobs
```

If errors:
- Source health tracking will auto-skip after 3 failures
- No impact on other sources
- Check logs for details

---

## 🎯 WHY THESE TWO?

1. **Remotive:**
   - Most popular remote job board
   - Clean API (no scraping needed)
   - Good SRE/Platform coverage
   - EMEA-friendly companies

2. **WeWorkRemotely:**
   - Second most popular
   - RSS = ultra-reliable (no auth)
   - Curated (less spam than some boards)
   - Strong tech company presence

**NOT added:**
- Remote.co (requires scraping)
- FlexJobs (paywall)
- Indeed/LinkedIn (too much noise)
- Talent.com (low quality for senior roles)

---

## 🚀 NEXT STEPS

**Automatic:** Next scan (in ~30 min) will include both boards

**Manual test:**
```bash
python3 jobhunt.py --config config.balanced.json scan --dry-run
```

**Expected in Slack:**
- Same quality as before (strict filtering)
- Maybe 1-2 more matches from job boards
- No spam (geo + title filters prevent it)

---

## ✅ SUMMARY

**Added:** 2 major job boards
**Volume:** +150-300 jobs scanned
**Matches:** +0-2 per scan (after filtering)
**Risk:** Low (error handling + source health)
**Maintenance:** Zero (public APIs)

**JOB BOARDS NU ACTIEF!** 🎉

