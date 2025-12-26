# Setup Adzuna Scanner in GitHub Actions

## ✅ What's Been Fixed

The GitHub Actions workflows have been updated to support Adzuna scanner credentials. Now you just need to add the credentials to GitHub Secrets.

## 🔑 Required GitHub Secrets

You need to add these two secrets to GitHub Actions:

1. **ADZUNA_APP_ID**: Your Adzuna application ID
2. **ADZUNA_APP_KEY**: Your Adzuna API key

> **Note**: If you need the specific credential values for this repository, check the existing file `ADZUNA_GITHUB_SECRETS.md` or retrieve them from https://developer.adzuna.com/ dashboard.

## 📝 How to Add GitHub Secrets

### Step 1: Go to Repository Settings

Visit your repository's secrets page:
`https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

Or manually:
1. Go to your repository on GitHub
2. Click **Settings** (top menu bar)
3. Click **Secrets and variables** → **Actions** (left sidebar)

### Step 2: Add First Secret (ADZUNA_APP_ID)

1. Click **New repository secret** (green button)
2. Fill in:
   - **Name**: `ADZUNA_APP_ID`
   - **Secret**: `[your_adzuna_app_id]`
3. Click **Add secret**

### Step 3: Add Second Secret (ADZUNA_APP_KEY)

1. Click **New repository secret** again
2. Fill in:
   - **Name**: `ADZUNA_APP_KEY`
   - **Secret**: `[your_adzuna_app_key]`
3. Click **Add secret**

## ✅ What Happens Next

Once you add these secrets:

1. **Automatic Scans**: The twice-daily scans (9:00 and 17:00 UTC) will now include Adzuna
2. **More Jobs**: Adzuna will contribute 40-100 Dutch jobs per scan
3. **No Errors**: You won't see "Adzuna credentials not found" errors anymore

### Expected Output in GitHub Actions

Before adding secrets:
```
✗ adzuna/nl:devops:1: Adzuna credentials not found (ADZUNA_APP_ID, ADZUNA_APP_KEY)
```

After adding secrets:
```
🔍 Checking Adzuna credentials...
✅ Adzuna credentials exist in GitHub secrets
✓ adzuna/nl:devops:1: 30 jobs
✓ adzuna/nl:platform engineer:1: 25 jobs
```

## 🧪 Testing

After adding the secrets, you can test immediately:

1. Go to your repository's Actions tab: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click on **Scan Jobs Daily** workflow
3. Click **Run workflow** (dropdown button)
4. Click the green **Run workflow** button
5. Wait 2-3 minutes
6. Check the logs to see Adzuna scanning successfully

## 📊 Expected Impact

### Current Sources in `config.balanced.json`
- 110 Greenhouse boards
- 11 Lever accounts  
- 3 Ashby boards
- **5 Adzuna queries** (NEW! - will work after adding secrets)
- 2 WeWorkRemotely categories
- 1 Remotive feed

### Adzuna Queries That Will Run
```json
"adzuna": {
  "queries": [
    "nl:devops:1",
    "nl:platform engineer:1",
    "nl:devops engineer:1",
    "nl:cloud engineer:1",
    "nl:azure:1"
  ]
}
```

Each query searches for Dutch jobs and returns 20-50 relevant positions.

## 🆘 Troubleshooting

### If secrets don't work immediately

1. **Wait 1-2 minutes**: GitHub sometimes takes a moment to propagate secrets
2. **Re-run workflow**: Manually trigger the workflow again
3. **Check secret names**: Make sure they're exactly `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` (case-sensitive)

### To verify secrets are set

1. Go to your repository's secrets page: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. You should see both secrets listed (values are hidden for security)

## 🎯 Files Updated in This PR

1. ✅ `.github/workflows/scan-jobs.yml` - Added Adzuna credentials to daily scan workflow
2. ✅ `.github/workflows/fresh-scan.yml` - Added Adzuna credentials to fresh scan workflow
3. ✅ `.env.example` - Documented Adzuna environment variables for local development
4. ✅ `SETUP_ADZUNA_SECRETS.md` - This guide for setting up GitHub secrets

## 📚 Additional Resources

- Adzuna Developer Portal: https://developer.adzuna.com/
- Your Adzuna queries: See `config.balanced.json` and `config.explore.json`
- Original fix documentation: See `ADZUNA_FIXED.md` and `ADZUNA_GITHUB_SECRETS.md`

---

**Action Required**: Add the two GitHub secrets mentioned above, then Adzuna scanner will work! 🚀
