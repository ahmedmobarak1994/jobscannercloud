# Location Policy - STRICT EU/EMEA + Worldwide Only

## 🎯 Policy Goal

**Only allow jobs you can actually apply for without residency restrictions:**
- ✅ Broad EU/EMEA remote (any EU country)
- ✅ Worldwide/Work-from-anywhere remote (true global)
- ❌ Single-country remote (even if EU) = residency requirement
- ❌ US/Canada/Australia remote
- ❌ City/state restricted remote

## ✅ SHOULD PASS (Broad Regional or Worldwide)

```
Remote, EMEA                                    → ALLOW (regional - any EU/EMEA country)
Remote - EMEA                                   → ALLOW (regional - EMEA wide)
Home based - EMEA                              → ALLOW (regional - EMEA wide)
Home based - Worldwide                         → ALLOW (worldwide WFA)
Remote, Europe                                 → ALLOW (regional - Europe wide)
Remote - EU                                    → ALLOW (regional - EU wide)
Amsterdam, Netherlands; Berlin, Germany; Remote → ALLOW (multi-country EU)
```

## ❌ SHOULD BLOCK (Residency Restricted)

**Single-Country Remote (Even if EU):**
```
Remote - Poland                                → BLOCK (Poland residency required)
Remote - France                                → BLOCK (France residency required)
Remote (UK)                                    → BLOCK (UK residency required)
Remote - Ireland                               → BLOCK (Ireland residency required)
Remote - Netherlands                           → BLOCK (NL residency required)
Remote - Germany                               → BLOCK (DE residency required)
```

**Reason:** Even though these are EU countries, "Remote - [single country]" format typically means:
- Must have work authorization in that specific country
- Payroll/legal entity only in that country
- Cannot work from other EU countries

**Blocked Countries:**
```
Toronto, Remote in Canada                      → BLOCK (Canada + residency)
Remote - USA                                   → BLOCK (blocked country)
Remote (Seattle, WA only)                      → BLOCK (city/state restriction)
Australia (Remote)                             → BLOCK (blocked country)
```

## Logic Explanation

**Why block "Remote - France" but allow "Remote, EMEA"?**

1. **"Remote, EMEA"** = company supports hiring across EU/EMEA region (flexible location)
2. **"Remote - France"** = company can only hire in France (payroll/legal constraint)

**Exception:** If location says BOTH country AND region (e.g., "Remote, France (EMEA)"), it passes because EMEA context indicates broader support.

## If You Want Country-Specific Remote

**If you live/work in Netherlands and want "Remote - Netherlands" to pass:**

Add to your config:
```json
"geo": {
  "allowed_single_countries": ["netherlands", "belgium", "germany"],
  ...
}
```

But by default, we block ALL single-country remote to avoid residency surprises.

## Test Cases

```
✅ ALLOW:
- Remote, EMEA
- Home based - Worldwide  
- Amsterdam; Berlin; Remote
- Remote - Europe

❌ BLOCK:
- Remote - Poland (residency)
- Remote - France (residency)
- Remote (UK) (residency)
- Remote - USA (blocked country)
- Toronto, Remote in Canada (blocked country)
- Remote (Seattle, WA only) (city restriction)
```

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

