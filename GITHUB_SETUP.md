# GitHub Setup Instructions

## 1. Add Slack Webhook Secret

1. Go to: https://github.com/ahmedmobarak1994/jobscannercloud/settings/secrets/actions
2. Click "New repository secret"
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Your Slack webhook URL (from .env file)
5. Click "Add secret"

## 2. Enable GitHub Actions

1. Go to: https://github.com/ahmedmobarak1994/jobscannercloud/actions
2. Click "I understand my workflows, go ahead and enable them"

## 3. Trigger First Run (Manual)

1. Go to: https://github.com/ahmedmobarak1994/jobscannercloud/actions/workflows/scan-jobs.yml
2. Click "Run workflow" dropdown
3. Click green "Run workflow" button
4. Wait ~30 seconds and refresh - you'll see your first scan!

## 4. Schedule

The workflow runs automatically:
- **9:00 AM UTC** (10:00 CET)
- **5:00 PM UTC** (18:00 CET)

## 5. Check Logs

- Go to Actions tab
- Click on any workflow run
- Click "scan" job
- Expand steps to see output

## 6. Adjust Filters (Optional)

Edit `config.balanced.json` via GitHub web editor:
- Adjust `min_score` (8 = more volume, 15 = strict)
- Add/remove companies in `sources`
- Tweak keywords/weights

Then commit - next run will use new config!

## Troubleshooting

**No Slack alerts?**
- Check GitHub Actions logs for errors
- Verify SLACK_WEBHOOK_URL secret is set correctly
- Test locally: `python3 jobhunt.py test-slack`

**Too many alerts?**
- Increase `min_score` in config
- Tighten `title_allow_regex_any` patterns
- Increase `min_stack_groups` to 2

**Too few alerts?**
- Decrease `min_score`
- Add more companies
- Broaden `title_allow_regex_any`

