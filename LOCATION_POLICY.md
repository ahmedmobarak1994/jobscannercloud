# Location Policy Test Cases

## ✅ SHOULD PASS (Broad EU/EMEA or Worldwide)

```
Remote, EMEA                                    → ALLOW (regional - EMEA)
Remote - EMEA                                   → ALLOW (regional - EMEA)
Home based - EMEA                              → ALLOW (regional - EMEA)
Home based - Worldwide                         → ALLOW (worldwide WFA)
Remote, Europe                                 → ALLOW (regional - Europe)
Remote - EU                                    → ALLOW (regional - EU)
```

## ❌ SHOULD BLOCK (Single-country = Residency Restricted)

```
Remote - Poland                                → BLOCK (single-country, residency likely required)
Remote - France                                → BLOCK (single-country, residency likely required)
Remote (UK)                                    → BLOCK (single-country, residency likely required)
Remote - Ireland                               → BLOCK (single-country, residency likely required)
Toronto, Remote in Canada                      → BLOCK (blocked country + residency)
Remote - USA                                   → BLOCK (blocked country)
Remote (Seattle, WA only)                      → BLOCK (city/state restriction)
Australia (Remote)                             → BLOCK (blocked country)
```

## Logic

**Single-country remote** (e.g., "Remote - Poland") is treated as **residency-restricted** because:

1. Most companies use this format when they can only hire in that specific country (tax/legal/payroll)
2. If they support EU-wide remote, they say "Remote, EMEA" or "Remote - Europe"
3. Exception: If location mentions both country AND EMEA/EU (e.g., "Remote, Germany (EMEA)"), it passes

**This is intentionally strict** to avoid jobs you can't actually apply for due to residency requirements.

## Title Blocks

```
✅ ALLOW:
- Site Reliability Engineer
- Platform Engineer
- DevOps Engineer
- Infrastructure Engineer
- Cloud Infrastructure Engineer
- Production Engineer

❌ BLOCK:
- Software Architect (too senior/different track)
- Security Engineer (security-only track)
- Data Infrastructure Engineer (data engineering track)
- Machine Learning Platform Engineer (ML track)
- UX Designer, Product Manager, etc. (non-engineering)
- Project Maintainer (not IC engineering)
- Support Engineer, Field Engineer (customer-facing)
```

## Expected Results After This Fix

From your previous 14 alerts, should now be reduced to ~3-5:

✅ **KEEP:**
- GitLab - Intermediate SRE, Database Operations (Remote, EMEA)
- GitLab - Intermediate SRE, Environment Automation (Remote, EMEA)
- Maybe: Canonical SRE roles if "Home based - EMEA" (not "Home based - Worldwide" data roles)

❌ **REMOVE:**
- Dropbox - Remote - Poland
- Twilio - Architect role
- Monzo - Remote (UK) 
- Algolia - Remote - France
- Canonical - Data Infrastructure roles (Kafka, OpenSearch, etc.)
- Canonical - UX Designer
- JetBrains - Security/AI/Maintainer roles
- Monzo - ML Platform role

