"""
Source health tracking

Tracks health of job sources (OK, TEMP_FAIL, PERM_FAIL)
to avoid wasting time on broken sources.
"""
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta


class SourceHealth:
    """Track source health status"""

    # Health statuses
    OK = "OK"
    TEMP_FAIL = "TEMP_FAIL"
    PERM_FAIL = "PERM_FAIL"

    def __init__(self, db_path: str = ".state/source_health.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS source_health (
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                status TEXT NOT NULL,
                fail_count INTEGER DEFAULT 0,
                last_ok_at TEXT,
                last_error TEXT,
                last_http_status INTEGER,
                last_checked_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_type, source_id)
            )
        """)
        conn.commit()
        conn.close()

    def record_success(self, source_type: str, source_id: str):
        """Record successful fetch"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.utcnow().isoformat()

        conn.execute("""
            INSERT INTO source_health (source_type, source_id, status, fail_count, last_ok_at, last_checked_at)
            VALUES (?, ?, ?, 0, ?, ?)
            ON CONFLICT(source_type, source_id) DO UPDATE SET
                status = ?,
                fail_count = 0,
                last_ok_at = ?,
                last_checked_at = ?
        """, (source_type, source_id, self.OK, now, now, self.OK, now, now))

        conn.commit()
        conn.close()

    def record_failure(self, source_type: str, source_id: str, error: str, http_status: Optional[int] = None):
        """Record failed fetch"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.utcnow().isoformat()

        # Get current fail count
        cursor = conn.execute(
            "SELECT fail_count FROM source_health WHERE source_type = ? AND source_id = ?",
            (source_type, source_id)
        )
        row = cursor.fetchone()
        fail_count = (row[0] + 1) if row else 1

        # Determine status based on error type and fail count
        if http_status == 404:
            status = self.PERM_FAIL
        elif fail_count >= 3:
            status = self.PERM_FAIL
        else:
            status = self.TEMP_FAIL

        conn.execute("""
            INSERT INTO source_health (source_type, source_id, status, fail_count, last_error, last_http_status, last_checked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_type, source_id) DO UPDATE SET
                status = ?,
                fail_count = ?,
                last_error = ?,
                last_http_status = ?,
                last_checked_at = ?
        """, (source_type, source_id, status, fail_count, error, http_status, now,
              status, fail_count, error, http_status, now))

        conn.commit()
        conn.close()

    def get_status(self, source_type: str, source_id: str) -> str:
        """Get source status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT status FROM source_health WHERE source_type = ? AND source_id = ?",
            (source_type, source_id)
        )
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else self.OK

    def should_skip(self, source_type: str, source_id: str) -> bool:
        """Check if source should be skipped"""
        status = self.get_status(source_type, source_id)

        if status == self.PERM_FAIL:
            return True

        if status == self.TEMP_FAIL:
            # Check if enough time has passed for retry (exponential backoff)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT fail_count, last_checked_at FROM source_health WHERE source_type = ? AND source_id = ?",
                (source_type, source_id)
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                fail_count, last_checked = row
                last_checked_dt = datetime.fromisoformat(last_checked)
                backoff_minutes = min(2 ** fail_count, 60)  # Max 60 min
                retry_after = last_checked_dt + timedelta(minutes=backoff_minutes)

                if datetime.utcnow() < retry_after:
                    return True

        return False

    def get_stats(self) -> Dict[str, int]:
        """Get health statistics"""
        conn = sqlite3.connect(self.db_path)

        stats = {}
        for status in [self.OK, self.TEMP_FAIL, self.PERM_FAIL]:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM source_health WHERE status = ?",
                (status,)
            )
            stats[status] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_failed_sources(self) -> list:
        """Get list of failed sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT source_type, source_id, status, fail_count, last_error, last_http_status
            FROM source_health
            WHERE status IN (?, ?)
            ORDER BY status DESC, fail_count DESC
        """, (self.PERM_FAIL, self.TEMP_FAIL))

        results = []
        for row in cursor.fetchall():
            results.append({
                'type': row[0],
                'id': row[1],
                'status': row[2],
                'fail_count': row[3],
                'error': row[4],
                'http_status': row[5]
            })

        conn.close()
        return results

    def reset_source(self, source_type: str, source_id: str):
        """Reset source health (for manual retry)"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "DELETE FROM source_health WHERE source_type = ? AND source_id = ?",
            (source_type, source_id)
        )
        conn.commit()
        conn.close()

    def close(self):
        """Close database connection"""
        pass  # Connection closed after each operation

