# Config Files Overview

## 📋 Which Config to Use?

### `config.balanced.json` ⭐ **MAIN CONFIG**

**Used by:** GitHub Actions (production)

**Profile:** Balanced quality vs volume

**Settings:**
- 110+ companies
- Min score: 8
- EU/EMEA + Worldwide remote
- Blocks single-country residency-restricted remote
- Blocks non-engineering roles

**Result:** ~3-5 highly relevant matches per scan

**Use when:** You want regular automated alerts with high quality

---

### `config.production.json` 🎯 **STRICT**

**Profile:** Highest quality, lowest volume

**Settings:**
- Same companies as balanced
- Min score: 18 (much higher!)
- Requires 2 of 3 stack groups
- Stricter keyword requirements

**Result:** ~1-2 top matches per scan

**Use when:** You only want the absolute best matches (e.g., GitLab SRE with score 75+)

---

### `config.test.json` 🧪 **TESTING**

**Profile:** Very permissive (for testing)

**Settings:**
- Only GitLab
- Min score: 1
- Very broad filters

**Result:** Many matches (including false positives)

**Use when:** Testing the scanner, debugging filters

---

## 🚀 How to Use

### Default (Balanced)

```bash
python3 jobhunt.py scan
```

This uses `config.balanced.json` by default.

### Production (Strict)

```bash
python3 jobhunt.py --config config.production.json scan
```

### Test

```bash
python3 jobhunt.py --config config.test.json scan --dry-run
```

---

## 🎛️ Quick Tuning

### Want More Volume?

Edit `config.balanced.json`:

```json
"min_score": 5  // lower from 8
```

### Want Less Volume?

```json
"min_score": 12  // raise from 8
```

Or switch to `config.production.json`.

### Want Different Companies?

Edit `sources` section in your config:

```json
"sources": {
  "greenhouse": {
    "boards": ["add-company-here", ...]
  }
}
```

---

## 📊 Expected Results Comparison

| Config | Companies | Min Score | Typical Matches | Use Case |
|--------|-----------|-----------|----------------|----------|
| **balanced** | 110+ | 8 | 3-5 | Daily automated alerts |
| **production** | 110+ | 18 | 1-2 | Only top opportunities |
| **test** | 1 | 1 | 10+ | Testing/debugging |

---

## 🔄 Switching Configs

### GitHub Actions

Edit `.github/workflows/scan-jobs.yml`:

```yaml
- name: Run job scan
  run: |
    python3 jobhunt.py --config config.production.json scan
```

### Local

```bash
# Balanced (default)
python3 jobhunt.py scan

# Production (strict)
python3 jobhunt.py --config config.production.json scan

# Test
python3 jobhunt.py --config config.test.json scan --dry-run
```

---

## ✅ Recommendation

**Start with `config.balanced.json`** (default)

- Monitor Slack for 1 week
- If too much: switch to `config.production.json`
- If too little: lower `min_score` in `config.balanced.json`

The balanced config is already **highly selective** (0.05% hit rate = 3-5 matches from 6000+ jobs), so most users won't need stricter filtering.

