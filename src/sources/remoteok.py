"""
RemoteOK JSON feed source

Fetches jobs from RemoteOK.com JSON feed
Public feed, no auth required
"""
import requests
from typing import List, Optional
from datetime import datetime
from ..models import Job
from .base import BaseSource


class RemoteOKSource(BaseSource):
    """RemoteOK remote jobs JSON feed"""

    JSON_URL = "https://remoteok.com/api"

    def get_source_name(self) -> str:
        """Return source name"""
        return "remoteok"

    def build_url(self, identifier: str) -> str:
        """Build API URL (identifier not used, always returns main feed)"""
        return self.JSON_URL

    def _validate_response_structure(self, response: requests.Response):
        """Validate response is a list"""
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Response is not a list")

    def fetch_jobs(self, identifier: str = "all", limit: Optional[int] = None) -> List[Job]:
        """
        Fetch jobs from RemoteOK

        Args:
            identifier: Not used (always fetches main feed)
            limit: Max results to return

        Returns:
            List of Job objects
        """
        try:
            # Fetch with retry
            url = self.build_url(identifier)

            # RemoteOK requires User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; JobScanner/1.0)'
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # Validate structure
            self._validate_response_structure(response)

            data = response.json()
            jobs = []

            # First item is metadata, skip it
            job_items = data[1:] if len(data) > 1 else []

            # Apply limit if specified
            if limit:
                job_items = job_items[:limit]

            # Parse jobs
            for job_data in job_items:
                if not isinstance(job_data, dict):
                    continue

                # Skip if no slug (means it's not a valid job)
                if not job_data.get('slug'):
                    continue

                # Create Job object
                job = Job(
                    source="remoteok",
                    company=job_data.get('company', 'Unknown'),
                    job_id=job_data.get('id', job_data.get('slug', '')),
                    title=job_data.get('position', ''),
                    location=job_data.get('location', 'Remote'),
                    url=f"https://remoteok.com/remote-jobs/{job_data.get('slug', '')}",
                    updated_at=str(job_data.get('date', '')),
                    content_text=job_data.get('description', '')
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"RemoteOK API error: {e}")
        except Exception as e:
            raise Exception(f"RemoteOK parse error: {e}")

