"""
Core data models
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import hashlib


class SourceHealth(Enum):
    OK = "ok"
    TEMP_FAIL = "temp_fail"
    PERM_FAIL = "perm_fail"


@dataclass
class Job:
    source: str
    company: str
    job_id: str
    title: str
    location: str
    url: str
    updated_at: Optional[str]
    content_text: str

    def get_db_key(self) -> str:
        """Unique key for deduplication"""
        return f"{self.source}:{self.company}:{self.job_id}"

    def get_content_hash(self) -> str:
        """Hash of content for change detection"""
        content = f"{self.title}|{self.location}|{self.content_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def is_updated(self, old_updated_at: Optional[str], old_hash: str) -> bool:
        """Check if job has been updated"""
        if self.updated_at and old_updated_at and self.updated_at != old_updated_at:
            return True
        if self.get_content_hash() != old_hash:
            return True
        return False


@dataclass
class SourceHealthRecord:
    source: str
    company: str
    status: SourceHealth
    last_check: str
    last_success: Optional[str]
    failure_count: int
    last_error: Optional[str]

