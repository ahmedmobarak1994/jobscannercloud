"""
Adzuna Jobs API source

Fetches jobs from Adzuna search engine
Requires API credentials (free tier available)
"""
import requests
import os
from typing import List, Optional
from ..models import Job
from .base import BaseSource


class AdzunaSource(BaseSource):
    """Adzuna job search API"""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, timeout: int = 30, max_retries: int = 2):
        super().__init__(timeout, max_retries)
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')

        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna credentials not found (ADZUNA_APP_ID, ADZUNA_APP_KEY)")

    def get_source_name(self) -> str:
        """Return source name"""
        return "adzuna"

    def build_url(self, identifier: str) -> str:
        """
        Build API URL

        identifier format: "country:query:page"
        e.g., "nl:site reliability engineer:1"
        """
        parts = identifier.split(':', 2)
        country = parts[0] if len(parts) > 0 else 'nl'
        query = parts[1] if len(parts) > 1 else ''
        page = parts[2] if len(parts) > 2 else '1'

        url = f"{self.BASE_URL}/{country}/search/{page}"
        return url

    def _validate_response_structure(self, response: requests.Response):
        """Validate response has expected structure"""
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Response is not a dict")
        if 'results' not in data:
            raise ValueError("Response missing 'results' key")

    def fetch_jobs(self, identifier: str, limit: Optional[int] = None) -> List[Job]:
        """
        Fetch jobs from Adzuna

        Args:
            identifier: "country:query:page" (e.g., "nl:sre:1")
            limit: Max results per page (API default: 50)

        Returns:
            List of Job objects
        """
        try:
            parts = identifier.split(':', 2)
            country = parts[0] if len(parts) > 0 else 'nl'
            query = parts[1] if len(parts) > 1 else ''
            page = parts[2] if len(parts) > 2 else '1'

            # Build URL and params
            url = self.build_url(identifier)
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': limit or 50,
                'what': query,
                'where': 'netherlands',
                'content-type': 'application/json'
            }

            # Fetch with retry
            response = self._fetch_with_retry(url + '?' + '&'.join(f'{k}={v}' for k, v in params.items()))
            response.raise_for_status()

            # Validate structure
            self._validate_response_structure(response)

            data = response.json()
            jobs = []

            # Parse results
            for job_data in data.get('results', []):
                # Extract fields
                job = Job(
                    source="adzuna",
                    company=job_data.get('company', {}).get('display_name', 'Unknown'),
                    job_id=str(job_data.get('id', '')),
                    title=job_data.get('title', ''),
                    location=job_data.get('location', {}).get('display_name', 'Netherlands'),
                    url=job_data.get('redirect_url', ''),
                    updated_at=job_data.get('created', ''),
                    content_text=job_data.get('description', '')
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"Adzuna API error: {e}")
        except Exception as e:
            raise Exception(f"Adzuna parse error: {e}")

