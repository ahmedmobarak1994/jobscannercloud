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

    def fetch_jobs(self, category: str = "software-dev") -> List[Job]:
        """
        Fetch jobs from Remotive

        Args:
            category: Job category (default: software-dev)

        Returns:
            List of Job objects
        """
        try:
            # Build URL
            url = self.BASE_URL
            params = {"category": category} if category else {}

            # Fetch with timeout
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            jobs = []

            # Parse jobs
            for job_data in data.get('jobs', []):
                # Skip if expired
                if job_data.get('publication_date') is None:
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
        # Simple HTML strip (can be improved with BeautifulSoup if needed)
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

