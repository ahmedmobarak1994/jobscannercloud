"""
Remotive API source

Fetches jobs from Remotive.com API
Public API, no auth required
"""
import requests
from typing import List
from ..models import Job
from .base import BaseSource


class RemotiveSource(BaseSource):
    """Remotive job board API"""

    BASE_URL = "https://remotive.com/api/remote-jobs"

    def get_source_name(self) -> str:
        """Return source name"""
        return "remotive"

    def build_url(self, identifier: str) -> str:
        """Build API URL"""
        return f"{self.BASE_URL}?category={identifier}"

    def _validate_response_structure(self, response: requests.Response):
        """Validate response has expected structure"""
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Response is not a dict")
        if 'jobs' not in data:
            raise ValueError("Response missing 'jobs' key")
        if not isinstance(data['jobs'], list):
            raise ValueError("'jobs' is not a list")

    def fetch_jobs(self, identifier: str, limit: int = None) -> List[Job]:
        """
        Fetch jobs from Remotive

        Args:
            identifier: Job category (e.g., "software-dev")
            limit: Not used (API returns all)

        Returns:
            List of Job objects
        """
        try:
            # Build URL and fetch
            url = self.build_url(identifier)
            response = self._fetch_with_retry(url)
            response.raise_for_status()

            # Validate structure
            self._validate_response_structure(response)

            data = response.json()
            jobs = []

            # Parse jobs
            for job_data in data.get('jobs', []):
                # Skip if no publication date (likely expired)
                if not job_data.get('publication_date'):
                    continue

                # Create Job object
                job = Job(
                    source="remotive",
                    company=job_data.get('company_name', 'Unknown'),
                    job_id=str(job_data.get('id', '')),
                    title=job_data.get('title', ''),
                    location=job_data.get('candidate_required_location', 'Remote'),
                    url=job_data.get('url', ''),
                    updated_at=job_data.get('publication_date', ''),
                    content_text=self._extract_text(job_data.get('description', ''))
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"Remotive API error: {e}")
        except Exception as e:
            raise Exception(f"Remotive parse error: {e}")

    def _extract_text(self, html: str) -> str:
        """Extract plain text from HTML description"""
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

