"""
Lever ATS source
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from .base import BaseSource
from ..models import Job


class LeverSource(BaseSource):
    """Lever Postings API"""

    BASE_URL = "https://api.lever.co/v0/postings"

    def get_source_name(self) -> str:
        return "lever"

    def build_url(self, account: str) -> str:
        return f"{self.BASE_URL}/{account}?mode=json"

    def _validate_response_structure(self, response: requests.Response):
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Invalid response")

    def fetch_jobs(self, account: str, limit: Optional[int] = None) -> List[Job]:
        url = self.build_url(account)
        resp = self._fetch_with_retry(url)

        if resp.status_code != 200:
            return []

        jobs_data = resp.json()

        if limit:
            jobs_data = jobs_data[:limit]

        jobs = []
        for job_data in jobs_data:
            try:
                job = self._normalize_job(account, job_data)
                jobs.append(job)
            except Exception:
                continue

        return jobs

    def _normalize_job(self, account: str, job_data: dict) -> Job:
        job_id = job_data["id"]
        title = job_data["text"]
        location = job_data.get("categories", {}).get("location", "Unknown")
        url = job_data["hostedUrl"]
        updated_at = str(job_data.get("createdAt", ""))

        description_html = job_data.get("description", "")
        lists_html = "\n".join(job_data.get("lists", []))
        content_html = f"{description_html}\n{lists_html}"
        content_text = self._html_to_text(content_html)

        return Job(
            source="lever",
            company=account,
            job_id=job_id,
            title=title,
            location=location,
            url=url,
            updated_at=updated_at,
            content_text=content_text
        )

    @staticmethod
    def _html_to_text(html: str) -> str:
        if not html:
            return ""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
            return soup.get_text(separator=' ', strip=True)
        except Exception:
            return html

