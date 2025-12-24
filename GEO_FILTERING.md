# Geo-Filtering Documentation

## Overview

The scanner now includes **strict geo-filtering** to block jobs from unwanted regions (USA, Canada, Australia, etc.) and only allow EU/EMEA remote positions.

## How It Works

### 1. Location Parsing

Every job location is parsed into structured information:

```python
LocationInfo(
    is_remote=True,
    scope=REMOTE_COUNTRY,
    countries={'united kingdom'},
    regions={'europe'},
    has_us_state=False,
    has_city_restriction=False
)
```

### 2. Scope Classification

**LocationScope types:**

- `ONSITE` - Not remote
- `HYBRID` - Partially remote
- `REMOTE_RESTRICTED` - Remote but restricted to states/cities
- `REMOTE_COUNTRY` - Remote within specific country/countries
- `REMOTE_REGION` - Remote within region (EMEA, Europe, etc)
- `REMOTE_GLOBAL` - Worldwide remote
- `REMOTE_UNKNOWN` - Just says "Remote" with no details

### 3. Geo Policy

Configured in `filters.geo`:

```json
{
  "allowed_regions": ["europe", "emea", "eu", "uk", ...],
  "blocked_countries": ["united states", "canada", "australia", "new zealand"],
  "allow_worldwide_remote": false,
  "allow_unknown_remote": false
}
```

### 4. Decision Logic

**Geo gate runs FIRST**, before all other filters:

1. **Restricted** (US states, specific cities, "only" patterns) → BLOCK (unless EU country)
2. **Blocked countries** (USA, Canada, Australia, NZ) → BLOCK
3. **EU countries** (auto-detected list) → ALLOW
4. **Allowed regions** (EMEA, Europe, etc) → ALLOW  
5. **Worldwide remote** → BLOCK (by default, too much noise)
6. **Unknown remote** → BLOCK (be explicit!)

## Test Cases

```
✅ ALLOW: "Cardiff, London or Remote (UK)"
✅ ALLOW: "Paris, France; Remote - France"
✅ ALLOW: "Amsterdam, Netherlands"
✅ ALLOW: "Remote - EMEA"

❌ BLOCK: "Remote - USA"
❌ BLOCK: "Toronto, Remote in Canada"
❌ BLOCK: "Australia (Remote)"
❌ BLOCK: "Remote (Seattle, WA only)"
❌ BLOCK: "Seattle, SF, NYC, Remote"
❌ BLOCK: "Home based - Worldwide"
❌ BLOCK: "Remote" (no region specified)
```

## Configuration Options

### Strict Mode (Default)

```json
{
  "allow_worldwide_remote": false,
  "allow_unknown_remote": false
}
```

Best for avoiding spam. Only explicit EU/EMEA jobs pass.

### Relaxed Mode

```json
{
  "allow_worldwide_remote": true,
  "allow_unknown_remote": true
}
```

Allows "worldwide" and plain "Remote" jobs. More volume but more noise.

### Custom Countries

Add more allowed countries:

```json
{
  "allowed_regions": [
    "europe",
    "singapore",
    "japan",
    "south korea"
  ]
}
```

### Company Overrides (TODO)

Future feature to handle company-specific policies:

```json
{
  "company_overrides": {
    "canonical": {
      "allow_worldwide_remote": false
    }
  }
}
```

## Debugging

Use `--explain` to see geo decisions:

```bash
python3 jobhunt.py --config config.balanced.json scan --dry-run --explain
```

Output shows:
```
Job: Senior SRE @ Company
Location: Remote - USA
Parsed: LocationInfo(remote=True, scope=REMOTE_COUNTRY, countries={'united states'})

GATES:
  geo: ✗

DROP: Geo: blocked country: {'united states'}
```

## Edge Cases Handled

1. **US State codes in context**: "Remote (Seattle, WA)" → Detects "WA" → BLOCK
2. **Multiple US cities**: "Seattle, San Francisco, NYC, Remote" → BLOCK
3. **Canadian cities**: "Toronto", "Vancouver" → Detects Canada → BLOCK
4. **Australian cities**: "Sydney", "Melbourne" → Detects Australia → BLOCK
5. **Worldwide patterns**: "Home based - Worldwide", "Work from anywhere" → Configurable
6. **Restriction patterns**: "Remote (X only)", "Must be located in", "Only candidates within" → BLOCK unless EU
7. **EU auto-detection**: Netherlands, Germany, France, UK, etc automatically allowed

## Performance

- Geo gate runs FIRST → Fast rejection of US/CA/AU jobs
- No API calls, pure regex/string matching
- ~0.001s per job

## Migration from Old Filters

Old config (`remote_positive`, `remote_negative`, `allowed_regions`, `blocked_regions`) still works but is LEGACY.

New config uses `geo` section. If `geo` exists, old filters are skipped.

## Known Limitations

1. **Ambiguous locations**: "Remote" alone → Blocked by default (strict)
2. **Multi-country listings**: "Remote - USA, UK, Germany" → Detects USA → BLOCK (even though UK/DE present)
3. **Typos**: "Germeny" won't match Germany pattern
4. **Non-English**: "Fernarbeit" (German for remote) not detected

Workarounds: Add patterns to `COUNTRY_PATTERNS` in `location_parser.py`.

