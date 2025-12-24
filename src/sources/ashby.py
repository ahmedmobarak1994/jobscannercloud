"""
Ashby ATS source
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from .base import BaseSource
from ..models import Job


class AshbySource(BaseSource):
    """Ashby Job Board"""

    BASE_URL = "https://jobs.ashbyhq.com"

    def get_source_name(self) -> str:
        return "ashby"

    def build_url(self, job_board: str) -> str:
        return f"{self.BASE_URL}/{job_board}/embed"

    def _validate_response_structure(self, response: requests.Response):
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Invalid response")
        if "jobs" not in data:
            raise ValueError("Missing jobs key")

    def fetch_jobs(self, job_board: str, limit: Optional[int] = None) -> List[Job]:
        url = self.build_url(job_board)
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
                job = self._normalize_job(job_board, job_data)
                jobs.append(job)
            except Exception:
                continue

        return jobs

    def _normalize_job(self, job_board: str, job_data: dict) -> Job:
        job_id = job_data["id"]
        title = job_data["title"]
        location = job_data.get("location", "Unknown")
        url = f"{self.BASE_URL}/{job_board}/{job_id}"
        updated_at = None

        description = job_data.get("description", "")
        requirements = job_data.get("requirements", "")
        content_html = f"{description}\n{requirements}"
        content_text = self._html_to_text(content_html)

        return Job(
            source="ashby",
            company=job_board.lower(),
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

