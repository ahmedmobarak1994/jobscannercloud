"""
Slack alerting
"""
import os
import requests
from typing import Optional
from .models import Job


class SlackAlerter:
    """Send job alerts to Slack"""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL not configured")

    def send_alert(self, job: Job, result):
        """Send Slack alert for job"""
        message = self._format_message(job, result)
        payload = {
            "text": message,
            "unfurl_links": False,
            "unfurl_media": False,
        }
        resp = requests.post(self.webhook_url, json=payload, timeout=10)
        resp.raise_for_status()

    def _format_message(self, job: Job, result) -> str:
        """Format job as Slack message"""
        lines = [
            f"🎯 *{job.title}*",
            f"🏢 {job.company.upper()} ({job.source})",
            f"📍 {job.location}",
            f"⭐ Score: {result.score}",
        ]

        # Add top matched keywords
        if hasattr(result, 'keyword_matches') and result.keyword_matches:
            all_matches = []
            for category, keywords in result.keyword_matches.items():
                all_matches.extend(keywords)

            if all_matches:
                top_matches = all_matches[:5]
                lines.append(f"🔑 {', '.join(top_matches)}")

        lines.append(f"🔗 {job.url}")
        return "\n".join(lines)

    def send_test(self):
        """Send test message"""
        payload = {"text": "✅ Remote SRE Job Scanner is working!"}
        resp = requests.post(self.webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        print("✅ Test alert sent successfully!")

