# Remote SRE Job Scanner

Automated job scanner for SRE/Platform/DevOps/Cloud Engineering roles with **strict EU/EMEA geo-filtering**.

## 🎯 What It Does

- Scans 110+ tech companies via ATS APIs (Greenhouse, Lever, Ashby)
- **Strict geo-filtering**: Only EU/EMEA or worldwide remote (blocks US/Canada/Australia, blocks single-country residency-restricted remote)
- **Role filtering**: Only SRE/Platform/DevOps/Infrastructure engineers (blocks PM/architect/support/data/ML)
- **Smart deduplication**: SQLite state tracking, only alerts on new/updated jobs
- **Slack integration**: Real-time alerts with scoring and reasons
- **GitHub Actions**: Automated scans 2x per day

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Slack (Optional)

Create `.env` file:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Configure Adzuna (Optional)

Adzuna is a job search engine that provides additional job coverage, especially for the Netherlands market.

1. Sign up for free API credentials at https://developer.adzuna.com/signup
2. Add to your `.env` file:

```bash
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

**For GitHub Actions**: Add these as repository secrets (Settings → Secrets and variables → Actions):
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`

Note: If not configured, Adzuna sources will be skipped automatically.

### 4. Run

```bash
# Test Slack
python3 jobhunt.py test-slack

# Dry run (no alerts)
python3 jobhunt.py scan --dry-run

# Live scan with alerts
python3 jobhunt.py scan

# Fresh scan (clear state)
./test_fresh_scan.sh
```

## ⚙️ Configuration

### Main Config: `config.balanced.json`

This is the **production config** used by GitHub Actions.

**Key settings:**

- **110+ companies**: GitLab, Stripe, Datadog, Cloudflare, Dropbox, Canonical, JetBrains, Monzo, etc.
- **Geo policy**: Strict EU/EMEA or worldwide only
- **Title filters**: SRE/Platform/DevOps/Infrastructure only
- **Min score**: 8 (balanced quality vs volume)

### Alternative Config: `config.production.json`

Stricter version with:
- Min score: 18 (fewer but higher quality matches)
- Requires 2 of 3 stack groups
- More restrictive keywords

### Test Config: `config.test.json`

For testing - very permissive filters.

## 🌍 Geo-Filtering Policy

See [LOCATION_POLICY.md](LOCATION_POLICY.md) for details.

**TLDR:**

✅ **ALLOW:**
- "Remote, EMEA"
- "Remote - Europe"
- "Home based - Worldwide"
- "Remote - EU"

❌ **BLOCK:**
- "Remote - USA/Canada/Australia"
- "Remote - Poland" (single-country = residency restricted)
- "Remote (UK)" (single-country = residency restricted)
- "Toronto, Remote in Canada"
- "Remote (Seattle, WA only)"

**Why?** Single-country remote usually means you must live in that country (payroll/legal). Only broad regional (EMEA) or worldwide remote is allowed.

## 🎯 Role Filtering

**ALLOW:**
- Site Reliability Engineer
- Platform Engineer
- DevOps Engineer
- Infrastructure Engineer
- Cloud Infrastructure Engineer
- Production Engineer

**BLOCK:**
- Architect, Manager, Director
- Product Manager, Program Manager
- Support Engineer, Field Engineer, Solutions Architect
- Security Engineer (security-only track)
- Data Engineer, Data Infrastructure
- ML/AI Platform Engineer
- Designer, UX/UI

## 📊 Typical Results

**Volume:** ~3-5 relevant matches per scan from 6000+ jobs

**Example matches:**
- GitLab - Intermediate SRE (Remote, EMEA)
- Canonical - Senior SRE (Home based - Worldwide)
- Platform Engineer roles at EU companies

## 🤖 GitHub Actions

Automated scans run **2x per day** (9:00 and 17:00 UTC).

**Workflows:**

1. **`scan-jobs.yml`** - Regular scheduled scans
2. **`fresh-scan.yml`** - Manual trigger with cache clear

**Setup:**

1. Add GitHub Secret: `SLACK_WEBHOOK_URL`
2. Go to Actions tab → Enable workflows
3. Trigger manually or wait for scheduled run

See [GITHUB_SETUP.md](GITHUB_SETUP.md) for details.

## 🧪 Testing

```bash
# Test location parser
python3 test_location_parser.py

# Fresh scan (clears state)
./test_fresh_scan.sh

# Dry run with explanations
python3 jobhunt.py scan --dry-run --explain
```

## 📁 Project Structure

```
.
├── jobhunt.py              # CLI entry point
├── requirements.txt        # Python dependencies
├── config.balanced.json    # Main production config
├── config.production.json  # Strict alternative
├── config.test.json        # Test config
├── src/
│   ├── config.py          # Config loading
│   ├── models.py          # Job data models
│   ├── state.py           # SQLite state management
│   ├── filtering.py       # Multi-stage filtering
│   ├── location_parser.py # Geo-filtering logic
│   ├── scanner.py         # Main orchestration
│   ├── alerting.py        # Slack integration
│   └── sources/           # ATS integrations
│       ├── greenhouse.py
│       ├── lever.py
│       └── ashby.py
├── .github/workflows/     # GitHub Actions
├── test_fresh_scan.sh     # Fresh scan script
└── test_location_parser.py # Location parser tests
```

## 🔧 Tuning

### Get More Volume

Lower `min_score` in config:

```json
"min_score": 8  // default
"min_score": 5  // more volume
```

### Get Higher Quality

Increase `min_score`:

```json
"min_score": 15  // only top matches
```

### Add More Companies

Edit `config.balanced.json`:

```json
"sources": {
  "greenhouse": {
    "boards": ["company-slug", ...]
  }
}
```

Find slugs from job board URLs:
- Greenhouse: `boards.greenhouse.io/{slug}`
- Lever: `jobs.lever.co/{slug}`
- Ashby: `jobs.ashbyhq.com/{slug}`

### Adjust Geo Policy

Edit `filters.geo` in config:

```json
"geo": {
  "allow_worldwide_remote": true,  // allow "work from anywhere"
  "blocked_countries": [...]       // countries to block
}
```

## 📚 Documentation

- [LOCATION_POLICY.md](LOCATION_POLICY.md) - Geo-filtering logic and test cases
- [GEO_FILTERING.md](GEO_FILTERING.md) - Technical details of geo-filtering
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub Actions setup

## 🐛 Debugging

```bash
# See why jobs are rejected
python3 jobhunt.py scan --dry-run --print-all

# See geo-filtering reasons
python3 jobhunt.py scan --dry-run --explain | grep "Geo:"

# Check filter stats
python3 jobhunt.py scan --dry-run
```

## 📈 Stats

Last production scan:
- Companies scanned: 111
- Jobs fetched: 6,200+
- Jobs passed filters: 3-5
- Hit rate: ~0.05% (extremely selective)
- Alerts sent: New/updated only

## 🎯 Success Criteria

You know it's working when you get:

✅ Only EU/EMEA or worldwide remote jobs
✅ Only SRE/Platform/DevOps/Infrastructure roles
✅ No US/Canada/Australia spam
✅ No Product Manager/Architect/Support roles
✅ No single-country residency-restricted remote

## 🤝 Contributing

Add more companies, improve filters, or add new ATS sources via PR!

## 📄 License

MIT

