"""
Recruitee API source

Fetches jobs from Recruitee careers pages
Public API, no auth required
Very popular in NL/EU startups
"""
import requests
from typing import List, Optional
from ..models import Job
from .base import BaseSource


class RecruiteeSource(BaseSource):
    """Recruitee careers API"""

    def get_source_name(self) -> str:
        """Return source name"""
        return "recruitee"

    def build_url(self, identifier: str) -> str:
        """
        Build API URL

        identifier is the subdomain (e.g., 'payter' for payter.recruitee.com)
        """
        return f"https://{identifier}.recruitee.com/api/offers"

    def _validate_response_structure(self, response: requests.Response):
        """Validate response has expected structure"""
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Response is not a dict")
        if 'offers' not in data:
            raise ValueError("Response missing 'offers' key")
        if not isinstance(data['offers'], list):
            raise ValueError("'offers' is not a list")

    def fetch_jobs(self, identifier: str, limit: Optional[int] = None) -> List[Job]:
        """
        Fetch jobs from Recruitee

        Args:
            identifier: Company subdomain (e.g., 'payter')
            limit: Not used (API returns all published offers)

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

            # Parse offers
            for offer in data.get('offers', []):
                # Skip if not published
                if offer.get('status') != 'published':
                    continue

                # Extract location
                location_parts = []
                if offer.get('city'):
                    location_parts.append(offer['city'])
                if offer.get('country'):
                    location_parts.append(offer['country'])
                location = ', '.join(location_parts) if location_parts else 'Remote'

                # Get careers URL
                careers_url = offer.get('careers_url', '')
                if not careers_url:
                    # Fallback to constructed URL
                    careers_url = f"https://{identifier}.recruitee.com/o/{offer.get('slug', '')}"

                # Create Job object
                job = Job(
                    source="recruitee",
                    company=identifier.replace('-', ' ').title(),  # Convert slug to name
                    job_id=str(offer.get('id', '')),
                    title=offer.get('title', ''),
                    location=location,
                    url=careers_url,
                    updated_at=offer.get('updated_at', ''),
                    content_text=offer.get('description', '')
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"Recruitee API error: {e}")
        except Exception as e:
            raise Exception(f"Recruitee parse error: {e}")

