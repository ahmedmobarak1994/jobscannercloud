"""
SQLite state management
"""
import sqlite3
import json
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pathlib import Path
from .models import Job, SourceHealth, SourceHealthRecord


class StateManager:
    """Manage job state and source health in SQLite"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                db_key TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                company TEXT NOT NULL,
                job_id TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                url TEXT NOT NULL,
                updated_at TEXT,
                content_hash TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_health (
                source TEXT NOT NULL,
                company TEXT NOT NULL,
                status TEXT NOT NULL,
                last_check TEXT NOT NULL,
                last_success TEXT,
                failure_count INTEGER DEFAULT 0,
                last_error TEXT,
                PRIMARY KEY (source, company)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_status ON source_health(status)")

        self.conn.commit()

    def get_job_state(self, db_key: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE db_key = ?", (db_key,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def save_job(self, job: Job, is_new: bool = True):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()

        if is_new:
            cursor.execute("""
                INSERT INTO jobs (db_key, source, company, job_id, title, location, url, 
                                updated_at, content_hash, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get_db_key(), job.source, job.company, job.job_id, job.title,
                job.location, job.url, job.updated_at, job.get_content_hash(),
                now, now
            ))
        else:
            cursor.execute("""
                UPDATE jobs 
                SET title = ?, location = ?, url = ?, updated_at = ?, content_hash = ?, last_seen = ?
                WHERE db_key = ?
            """, (job.title, job.location, job.url, job.updated_at, job.get_content_hash(), now, job.get_db_key()))

        self.conn.commit()

    def get_source_health(self, source: str, company: str) -> Optional[SourceHealthRecord]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM source_health WHERE source = ? AND company = ?", (source, company))
        row = cursor.fetchone()

        if not row:
            return None

        return SourceHealthRecord(
            source=row['source'],
            company=row['company'],
            status=SourceHealth(row['status']),
            last_check=row['last_check'],
            last_success=row['last_success'],
            failure_count=row['failure_count'],
            last_error=row['last_error']
        )

    def save_source_health(self, source: str, company: str, status: SourceHealth, error: Optional[str] = None):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()

        existing = self.get_source_health(source, company)

        if existing:
            new_failure_count = existing.failure_count + 1 if status != SourceHealth.OK else 0
            last_success = now if status == SourceHealth.OK else existing.last_success

            cursor.execute("""
                UPDATE source_health
                SET status = ?, last_check = ?, last_success = ?, 
                    failure_count = ?, last_error = ?
                WHERE source = ? AND company = ?
            """, (status.value, now, last_success, new_failure_count, error, source, company))
        else:
            cursor.execute("""
                INSERT INTO source_health (source, company, status, last_check, 
                                         last_success, failure_count, last_error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source, company, status.value, now,
                  now if status == SourceHealth.OK else None,
                  0 if status == SourceHealth.OK else 1,
                  error))

        self.conn.commit()

    def get_bad_sources(self) -> List[Tuple[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT source, company FROM source_health WHERE status = 'perm_fail'")
        return [(row['source'], row['company']) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()


class ScanCursor:
    """Track batch scanning progress"""

    def __init__(self, cursor_file: str):
        self.cursor_file = Path(cursor_file)
        self.cursor_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict:
        if not self.cursor_file.exists():
            return {"tier2_index": 0, "last_run": None}
        with open(self.cursor_file) as f:
            return json.load(f)

    def save(self, state: Dict):
        state["last_run"] = datetime.utcnow().isoformat()
        with open(self.cursor_file, 'w') as f:
            json.dump(state, f, indent=2)

