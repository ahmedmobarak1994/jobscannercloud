"""
WeWorkRemotely RSS source

Fetches jobs from WeWorkRemotely RSS feed
Public feed, no auth required
"""
import requests
import xml.etree.ElementTree as ET
from typing import List
from datetime import datetime
from ..models import Job
from .base import BaseSource


class WeWorkRemotelySource(BaseSource):
    """WeWorkRemotely RSS feed"""

    RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    def fetch_jobs(self, identifier: str = "programming") -> List[Job]:
        """
        Fetch jobs from WeWorkRemotely RSS feed

        Args:
            identifier: Category (programming/devops/sysadmin)

        Returns:
            List of Job objects
        """
        # RSS URLs by category
        rss_urls = {
            "programming": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
            "devops": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
            "all": "https://weworkremotely.com/categories/remote-jobs.rss"
        }

        url = rss_urls.get(identifier, rss_urls["programming"])

        try:
            # Fetch RSS feed
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)
            jobs = []

            # Parse items
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                description_elem = item.find('description')
                pubdate_elem = item.find('pubDate')

                if title_elem is None or link_elem is None:
                    continue

                title = title_elem.text or ''
                link = link_elem.text or ''
                description = description_elem.text or '' if description_elem is not None else ''
                pubdate = pubdate_elem.text or '' if pubdate_elem is not None else ''

                # Extract company from title (format: "Company: Job Title")
                company = "Unknown"
                if ':' in title:
                    parts = title.split(':', 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                # Generate job ID from URL
                job_id = link.split('/')[-1] if '/' in link else link

                # Create Job object
                job = Job(
                    source="weworkremotely",
                    company=company,
                    job_id=job_id,
                    title=title,
                    location="Remote",  # WWR is all remote
                    url=link,
                    updated_at=pubdate,
                    content_text=self._clean_description(description)
                )

                jobs.append(job)

            return jobs

        except requests.RequestException as e:
            raise Exception(f"WWR RSS error: {e}")
        except ET.ParseError as e:
            raise Exception(f"WWR XML parse error: {e}")
        except Exception as e:
            raise Exception(f"WWR error: {e}")

    def _clean_description(self, html: str) -> str:
        """Clean HTML description to plain text"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()

