"""
Base source plugin
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import requests
import time
from ..models import Job, SourceHealth


class BaseSource(ABC):
    """Abstract ATS source plugin"""

    def __init__(self, timeout: int = 30, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    def get_source_name(self) -> str:
        pass

    @abstractmethod
    def build_url(self, identifier: str) -> str:
        pass

    @abstractmethod
    def fetch_jobs(self, identifier: str, limit: Optional[int] = None) -> List[Job]:
        pass

    @abstractmethod
    def _validate_response_structure(self, response: requests.Response):
        pass

    def validate_source(self, identifier: str) -> SourceHealth:
        """Validate source is accessible"""
        try:
            url = self.build_url(identifier)
            resp = self._fetch_with_retry(url)

            if resp.status_code != 200:
                return SourceHealth.PERM_FAIL

            self._validate_response_structure(resp)
            return SourceHealth.OK

        except requests.Timeout:
            return SourceHealth.TEMP_FAIL
        except requests.ConnectionError:
            return SourceHealth.TEMP_FAIL
        except Exception:
            return SourceHealth.PERM_FAIL

    def _fetch_with_retry(self, url: str) -> requests.Response:
        """Fetch with exponential backoff"""
        last_exc = None

        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.get(url, timeout=self.timeout)
                return resp
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                continue

        if last_exc:
            raise last_exc
        raise requests.RequestException(f"Failed after {self.max_retries} retries")

