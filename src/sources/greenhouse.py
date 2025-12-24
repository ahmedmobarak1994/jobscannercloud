"""
Greenhouse ATS source
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from .base import BaseSource
from ..models import Job


class GreenhouseSource(BaseSource):
    """Greenhouse Boards API"""

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def get_source_name(self) -> str:
        return "greenhouse"

    def build_url(self, board: str) -> str:
        return f"{self.BASE_URL}/{board}/jobs"

    def _validate_response_structure(self, response: requests.Response):
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Invalid response")
        if "jobs" not in data:
            raise ValueError("Missing jobs key")

    def fetch_jobs(self, board: str, limit: Optional[int] = None) -> List[Job]:
        url = self.build_url(board)
        resp = self._fetch_with_retry(url)

        if resp.status_code != 200:
            return []

        data = resp.json()
        jobs_data = data.get("jobs", [])

        if limit:
            jobs_data = jobs_data[:limit]

        jobs = []
        for job_data in jobs_data:
            try:
                job = self._normalize_job(board, job_data)
                jobs.append(job)
            except Exception:
                continue

        return jobs

    def _normalize_job(self, board: str, job_data: dict) -> Job:
        job_id = str(job_data["id"])
        title = job_data["title"]
        location = job_data.get("location", {}).get("name", "Unknown")
        url = job_data["absolute_url"]
        updated_at = job_data.get("updated_at")

        content_html = job_data.get("content", "")
        content_text = self._html_to_text(content_html)

        return Job(
            source="greenhouse",
            company=board,
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

