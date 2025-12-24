# Remote SRE Job Scanner

Automated job scanner voor SRE/Platform/DevOps/Cloud Engineering vacatures met focus op remote EMEA posities.

## Features

- 🌍 **Multi-ATS Support**: Greenhouse, Lever, Ashby
- 🎯 **Smart Filtering**: Multi-stage gates (remote, region, title, stack, scoring)
- 🔍 **110+ Tech Companies**: GitLab, HashiCorp, Stripe, DataDog, Cloudflare, etc.
- 📊 **Explainability**: Zie waarom jobs wel/niet matchen
- 💾 **State Management**: SQLite dedupe + re-alerts op updates
- 📢 **Slack Alerts**: Real-time notificaties
- 🤖 **GitHub Actions**: Automatisch dagelijks scannen

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Slack

Maak een `.env` file:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Run Scan

```bash
# Test Slack
python3 jobhunt.py test-slack

# Dry run (geen alerts)
python3 jobhunt.py --config config.balanced.json scan --dry-run

# Live scan
python3 jobhunt.py --config config.balanced.json scan
```

## Configuration

### Config Profiles

- **`config.balanced.json`** - Aanbevolen: breed maar gefocust (110+ bedrijven, min_score: 8)
- **`config.production.json`** - Strict SRE focus (min_score: 18, 2 stack groups)
- **`config.test.json`** - Testing purposes

### Filters

#### Remote & Region
- ✅ Remote-first/fully remote/distributed
- ✅ EMEA/EU/Europe/Worldwide
- ❌ Hybrid/on-site
- ❌ "USA only"/"Canada only"

#### Titles
- ✅ SRE, Platform Engineer, DevOps, Cloud Engineer, Infrastructure Engineer
- ❌ Director, Manager, Frontend, AI Engineer, Data Scientist

#### Stack Groups (min 1 of 3)
- **Role**: SRE, reliability, devops, platform, infrastructure
- **Cloud**: AWS, Azure, GCP, Kubernetes, Terraform, Docker
- **Observability**: Prometheus, Grafana, monitoring, incident, on-call, SLO

#### Scoring
- Keywords: kubernetes (15), terraform (12), AWS/Azure/GCP (8), SRE (20)
- Title bonus: SRE (25), Platform (20), DevOps (15)
- Min score: 8 (balanced) / 12 (strict) / 18 (very strict)

## CLI Commands

```bash
# Scan
python3 jobhunt.py scan
python3 jobhunt.py --config config.balanced.json scan --dry-run
python3 jobhunt.py scan --explain  # Show filtering details
python3 jobhunt.py scan --print-all  # Show all jobs (incl rejected)

# Test Slack
python3 jobhunt.py test-slack
```

## Architecture

```
src/
├── models.py          # Job + SourceHealth models
├── config.py          # Config loading
├── state.py           # SQLite state management
├── filtering.py       # Multi-stage filtering + scoring
├── scanner.py         # Main orchestration
├── alerting.py        # Slack integration
└── sources/
    ├── base.py        # Abstract source plugin
    ├── greenhouse.py  # Greenhouse API
    ├── lever.py       # Lever API
    └── ashby.py       # Ashby API
```

## GitHub Actions

Automatic daily scans at 9:00 and 17:00 UTC:

```yaml
# .github/workflows/scan-jobs.yml
- Runs: 2x per day
- Alerts: Direct to Slack
- State: Persisted between runs
```

## Adding Companies

Edit `config.balanced.json`:

```json
{
  "sources": {
    "greenhouse": {
      "boards": ["company-slug"]
    },
    "lever": {
      "accounts": ["company-slug"]
    },
    "ashby": {
      "job_boards": ["CompanySlug"]
    }
  }
}
```

Find slugs:
- Greenhouse: `boards.greenhouse.io/{slug}`
- Lever: `jobs.lever.co/{slug}`
- Ashby: `jobs.ashbyhq.com/{slug}`

## Stats

Last run (Example):
- 111 companies scanned
- 6227 jobs analyzed
- 58 relevant matches (0.93% hit rate)
- Focus: Cloud/Platform/SRE/DevOps roles
- Regions: EMEA/EU/Worldwide

## Top Companies

GitLab, HashiCorp, Grafana, DataDog, Elastic, Stripe, Cloudflare, MongoDB, Coinbase, Databricks, JetBrains, Monzo, Adyen, Doctolib, Twilio, PagerDuty, Redis, Postman, Algolia, CircleCI, LaunchDarkly, Amplitude, Fivetran, +90 more

## License

MIT

## Contributing

PRs welcome! Add more companies, improve filters, or add new ATS sources.

