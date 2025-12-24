# GitHub Actions Workflows - Final Setup

## ✅ Active Workflows (2)

### 1. **scan-jobs.yml** (PRIMARY)

**Schedule:** 2x per day
- 09:00 UTC (10:00 CET)
- 17:00 UTC (18:00 CET)

**Features:**
- ✅ Source health tracking
- ✅ Cache management
- ✅ Slack integration
- ✅ Debug output
- ✅ Manual trigger with cache clear option

**Config:** `config.balanced.json`

**Status:** ✅ ACTIVE & WORKING

---

### 2. **fresh-scan.yml** (MANUAL)

**Schedule:** Manual trigger only

**Features:**
- ✅ Bypasses all cache
- ✅ Forces fresh scan of all jobs
- ✅ Useful for testing changes

**Config:** `config.balanced.json`

**Status:** ✅ ACTIVE (manual use)

---

## ❌ Disabled Workflows (1)

### **jobhunt.yml.disabled** (OLD)

**Why disabled:**
- Ran every 2 hours (12x/day) = overkill
- Overlapped with scan-jobs.yml
- Less features than scan-jobs.yml
- Caused duplicate work

**Status:** ❌ DISABLED (renamed to .disabled)

---

## 📊 Current Schedule

```
Daily Schedule (UTC):
00:00 ─────────────────────────────
02:00 ─────────────────────────────
04:00 ─────────────────────────────
06:00 ─────────────────────────────
08:00 ─────────────────────────────
09:00 🚀 SCAN (scan-jobs.yml)
10:00 ─────────────────────────────
12:00 ─────────────────────────────
14:00 ─────────────────────────────
16:00 ─────────────────────────────
17:00 🚀 SCAN (scan-jobs.yml)
18:00 ─────────────────────────────
20:00 ─────────────────────────────
22:00 ─────────────────────────────
```

**Total:** 2 scans per day (optimal for job boards)

---

## 🔧 Configuration

All workflows use: **`config.balanced.json`**

**Config details:**
- 120+ sources (Greenhouse, Lever, Ashby)
- Strict EU/EMEA + Worldwide geo filtering
- Comprehensive title blocks
- Min score: 8 (balanced)
- Source health tracking enabled

---

## 🚀 How to Use

### Regular Scans (Automatic)

Nothing to do! Runs automatically 2x/day.

Check results:
- 👉 https://github.com/ahmedmobarak1994/jobscannercloud/actions
- Slack alerts for new jobs
- Logs in Actions UI

### Fresh Scan (Manual)

When you want to force a fresh scan (e.g., after config changes):

1. Go to: https://github.com/ahmedmobarak1994/jobscannercloud/actions/workflows/fresh-scan.yml
2. Click "Run workflow"
3. Check "Clear cache" if you want ALL jobs to be considered new
4. Click green "Run workflow" button
5. Wait ~2 minutes
6. Check Slack for alerts

### Check Source Health

After a scan, check which sources are healthy:

```bash
python3 jobhunt.py source-health
```

This shows OK/TEMP_FAIL/PERM_FAIL status of all sources.

---

## 📈 Expected Results

**Per scan:**
- Sources scanned: ~118-120
- Jobs fetched: ~6000-6500
- Jobs passed: ~5-10 (strict filtering!)
- New alerts: 0-2 (only if new jobs posted)

**Source health:**
- OK: ~116-118
- TEMP_FAIL: 0-2 (temporary issues)
- PERM_FAIL: 0-2 (404s, permanently broken)

---

## ⚠️ Troubleshooting

### No Slack Alerts

**Check:**
1. GitHub Secret `SLACK_WEBHOOK_URL` is set
2. Workflow logs show "✅ Slack webhook configured"
3. Jobs passed > 0 and New jobs > 0

**Fix:**
- Add/update secret: https://github.com/ahmedmobarak1994/jobscannercloud/settings/secrets/actions

### Workflow Failures

**Common causes:**
1. Config file missing/invalid → Fixed (now uses config.balanced.json)
2. Slack webhook not set → Not fatal, just no alerts
3. API rate limits → Rare with 2x/day schedule

**Check logs:**
- https://github.com/ahmedmobarak1994/jobscannercloud/actions

### Too Many/Few Alerts

**Too many:**
- Increase `min_score` in config.balanced.json
- Or switch to config.production.json (min_score: 18)

**Too few:**
- Lower `min_score` in config.balanced.json
- Add more sources
- Check if geo filtering is too strict

---

## 🎯 Summary

- ✅ **1 primary workflow** (scan-jobs.yml, 2x/day)
- ✅ **1 manual workflow** (fresh-scan.yml, on-demand)
- ✅ **Source health** automatically tracked
- ✅ **Slack alerts** for new jobs only
- ✅ **Clean, maintainable** setup

**Everything is working as designed!** 🚀

