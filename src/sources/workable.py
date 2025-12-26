"""
Workable API source

Fetches jobs from Workable careers pages
Public widget API, no auth required
Popular globally, some EU presence
"""
import requests
from typing import List, Optional
from ..models import Job
from .base import BaseSource


class WorkableSource(BaseSource):
    """Workable careers widget API"""

    def get_source_name(self) -> str:
        """Return source name"""
        return "workable"

    def build_url(self, identifier: str) -> str:
        """
        Build API URL

        identifier is the account name (e.g., 'inventyou-ab')
        """
        return f"https://apply.workable.com/api/v1/widget/accounts/{identifier}"

    def _validate_response_structure(self, response: requests.Response):
        """Validate response has expected structure"""
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Response is not a dict")
        if 'jobs' not in data:
            raise ValueError("Response missing 'jobs' key")

    def fetch_jobs(self, identifier: str, limit: Optional[int] = None) -> List[Job]:
        """
        Fetch jobs from Workable

        Args:
            identifier: Company account (e.g., 'inventyou-ab')
            limit: Not used (API returns all jobs)

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
                # Extract location
                location = job_data.get('city', 'Remote')
                if job_data.get('country'):
                    location = f"{location}, {job_data['country']}"

                # Create Job object
                job = Job(
                    source="workable",
                    company=identifier.replace('-', ' ').title(),
                    job_id=job_data.get('shortcode', ''),
                    title=job_data.get('title', ''),
                    location=location,
                    url=job_data.get('url', ''),
                    updated_at='',  # Workable doesn't provide updated_at in widget API
                    content_text=job_data.get('description', '')
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"Workable API error: {e}")
        except Exception as e:
            raise Exception(f"Workable parse error: {e}")

